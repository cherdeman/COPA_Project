# Preliminary analysis of COPA's Summary Case data
# Each row is a complaint, the summary data does not include names of
# complainants or officers

import os
import pandas as pd

##### LOADING FUNCTIONS #####

def load_full_dataset(filename):
	'''
	Load data from specified file. This loads the full dataset with an added
	"COMPLAINT_YEAR" column

	Inputs:
	    filename: (string) filename for the copa file

	Returns: pandas dataframe
	'''
	full_df = pd.read_csv(filename, index_col = 0)

	# Remove timestamp from date string
	full_df["SIMPLE_DATE"] = full_df["COMPLAINT_DATE"].str.split(" ").str[0]

	# Extract year from SIMPLE_DATE and convert to int
	full_df["COMPLAINT_YEAR"] = full_df["SIMPLE_DATE"].str.split("/").str[2].astype(int)

	# Drop SIMPLE_DATE and reorder columns
	full_df.drop("SIMPLE_DATE", axis = 1)
	cols = full_df.columns.tolist()
	cols = [cols[0]] + [cols[-1]] + cols[1:len(cols)-2]
	full_df = full_df[cols]

	# Find number of officers involved, exclude values over 15
	# This limits excessive row expansion
	full_df["OFFICER_COUNT"] = full_df["RACE_OF_INVOLVED_OFFICERS"].str.count("\|") + 1
	limit_officers = full_df[(full_df["OFFICER_COUNT"] <= 15) | (pd.isnull(full_df["OFFICER_COUNT"]))]

	# Split all columns that may have multiple values
	split_cols = ["BEAT", "RACE_OF_COMPLAINANTS", "SEX_OF_COMPLAINANTS", 
		"AGE_OF_COMPLAINANTS", "RACE_OF_INVOLVED_OFFICERS", 
		"SEX_OF_INVOLVED_OFFICERS", "AGE_OF_INVOLVED_OFFICERS", 
		"YEARS_ON_FORCE_OF_INVOLVED_OFFICERS"]
	
	split_df = pd.concat([limit_officers[col].str.split("|", expand = True) for col in split_cols], axis = 1, keys = split_cols)
	split_df.columns = split_df.columns.map(lambda x: "_".join((x[0], str(x[1]))))
	
	# Rejoin with full df
	new_df = pd.concat([split_df, full_df.drop(split_cols + ["OFFICER_COUNT"], axis = 1)], axis = 1)
	new_df.fillna(value = Nan, inplace = True)
	
	# HIGH LEVEL SUMMARY STATISTICS
	# Total complaints
	num_complaints = new_df.shape[0]

	# Year range
	min_year = new_df["COMPLAINT_YEAR"].min()
	max_year = new_df["COMPLAINT_YEAR"].max()

	# Complaints by year
	year = new_df.groupby("COMPLAINT_YEAR").size().to_frame()

	# Complaints by assignment
	assignment = new_df["ASSIGNMENT"].value_counts().to_frame()

	# Print Statements
	print()
	print("There were ", num_complaints, "reported complaints against CPD ", 
		"officers between ", min_year, " and ", max_year, ".")
	print()
	print("Below are the complaint breakdowns by year and jurisdictional", 
		"assignment: ")
	print()
	print("YEAR")
	for y in year.index:
		print(y, ": ", year.loc[y][0])
	print()
	print("JURISDICTIONAL ASSIGNMENT")
	for a in assignment.index:
		print(a, ": ", assignment.loc[a][0])
	print()

	return new_df

def reduce_to_copa_ipra(full_dataset):
	'''
	Subset the dataset to include only complaints assigned to COPA or IPRA
	and only complaints that concern a single complainant, officer, and beat

	Inputs:
		full_dataset: (pandas dataframe)

	Returns: pandas dataframe
	'''
	# Extract COPA and IPRA assignments
	copa_ipra_df = full_dataset[full_dataset["ASSIGNMENT"].str.contains("IPRA")
	 | full_dataset["ASSIGNMENT"].str.contains("COPA")]

	# HIGH LEVEL SUMMARY STATISTICS
	# Total complaints for COPA/IPRA and full dataframes
	num_complaints_final = copa_ipra_df.shape[0]
	num_complaints_full = full_dataset.shape[0]
	final_pct = num_complaints_final / num_complaints_full

	# Year range
	min_year = copa_ipra_df["COMPLAINT_YEAR"].min()
	max_year = copa_ipra_df["COMPLAINT_YEAR"].max()

	# Complaints by year
	year = copa_ipra_df.groupby("COMPLAINT_YEAR").size().to_frame()

	# Complaints by assignment
	assignment = copa_ipra_df["ASSIGNMENT"].value_counts().to_frame()

	# Complaints by current category
	category = copa_ipra_df["CURRENT_CATEGORY"].value_counts().to_frame()

	# Complaints by current status
	status = copa_ipra_df["CURRENT_STATUS"].value_counts().to_frame()

	# Complaints by finding
	finding = copa_ipra_df["FINDING_CODE"].value_counts().to_frame()

	# Print Statements
	print()
	print(num_complaints_final, " or ", "{:.0%}".format(final_pct), "of all", 
		"complaints were under IPRA or COPA jurisdiction between ", 
		min_year, " and ", max_year, ".")
	print()
	print("Below are the complaint breakdowns by year, category, status, and finding:")
	print()
	print("YEAR")
	for y in year.index:
		print(y, ": ", year.loc[y][0])
	print()
	print("CURRENT CATEGORY")
	for c in category.index:
		print(c, ": ", category.loc[c]["CURRENT_CATEGORY"])
	print()
	print("CURRENT STATUS")
	for s in status.index:
		print(s, ": ", status.loc[s]["CURRENT_STATUS"])
	print()
	print("FINDING")
	for f in finding.index:
		print(f, ": ", finding.loc[f]["FINDING_CODE"])

	return copa_ipra_df


##### COMPLAINT ANALYSIS #####

def top_k_complaints_by_beat(copa_ipra_df, beat, k, year = None, month = None):
	'''
	Find the top complaints in a police beat, with the option to specify
	a year and/or month of interest.

	Inputs:
		copa_ipra_df: (pandas dataframe) dataframe that excludes BIA cases
		beat: (string) represents a Chicago police beat 
		k: (int) the number of items to return
		year: (int) optional year of interest
		month: (int) optional month of interest

	Returns: list of tuples representing the complaint category and number of
		complaints
	'''
	assert type(beat) == str, ("Beat number must be input as string")
	
	# Subset dataframe on beat, year, and month (as needed)
	if year == None and month == None:
		beat_df = copa_ipra_df[copa_ipra_df["BEAT"].map(lambda x: beat in x)]
	elif year != None and month == None:
		year_df = copa_ipra_df[copa_ipra_df["COMPLAINT_YEAR"] == year]
		beat_df = year_df[year_df["BEAT"].map(lambda x: beat in x)]
	elif year == None and month != None:
		month_df = copa_ipra_df[copa_ipra_df["COMPLAINT_MONTH"] == month]
		beat_df = month_df[month_df["BEAT"].map(lambda x: beat in x)]
	else:
		year_df = copa_ipra_df[copa_ipra_df["COMPLAINT_YEAR"] == year]
		year_month_df = year_df[year_df["COMPLAINT_MONTH"] == month]
		beat_df = year_month_df[year_month_df["BEAT"].map(lambda x: beat in x)]

	# Tabulate complaint category counts and convert to individual lists
	complaint_counts = beat_df["CURRENT_CATEGORY"].value_counts().to_frame()
	name = complaint_counts["CURRENT_CATEGORY"].index.tolist()
	count = complaint_counts["CURRENT_CATEGORY"].values.tolist()

	# Create output list
	output []
	loop_len = min(k, len(name))

	for i in range(loop_len):
		pair = (name[i], count[i])
		output.append(pair)

	return output


##### IPRA / COPRA COMPARISONS ####


