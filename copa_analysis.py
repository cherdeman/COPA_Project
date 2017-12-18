# Preliminary analysis of COPA's Summary Case data
# Each row is a complaint, the summary data does not include names of
# complainants or officers

import os
import pandas
import re

def load_full_dataset(filename):
	'''
	Load data from specified file. This loads the full dataset with an added
	"YEAR" column

	Inputs:
	    filename: (string) filename for the copa file

	Returns: pandas dataframe
	'''
	full_df = pd.read_csv(filename, index_col = 0)

	# Remove timestamp from date string
	full_df["SIMPLE_DATE"] = full_df["COMPLAINT_DATE"].str.split(" ").str[0]

	# Extract year from SIMPLE_DATE
	full_df["COMPLAINT_YEAR"] = full_df["SIMPLE_DATE"].str.split("/").str[2]

	# Drop SIMPLE_DATE and reorder columns
	full_df.drop("SIMPLE_DATE", axis = 1)
	cols = full_df.columns.tolist()
	cols = [cols[0]] + [cols[-1]] + cols[1:len(cols)-2]
	full_df = full_df[cols]

	# Split all columns that may have multiple values
	full_df["BEAT"] = full_df["BEAT"].str.split("|")
	
	full_df["RACE_OF_COMPLAINANTS"] = full_df["RACE_OF_COMPLAINANTS"].str.split("|")
	full_df["SEX_OF_COMPLAINANTS"] = full_df["SEX_OF_COMPLAINANTS"].str.split("|")
	full_df["AGE_OF_COMPLAINANTS"] = full_df["AGE_OF_COMPLAINANTS"].str.split("|")
    
	full_df["RACE_OF_INVOLVED_OFFICERS"] = full_df["RACE_OF_INVOLVED_OFFICERS"].str.split("|")
	full_df["SEX_OF_INVOLVED_OFFICERS"] = full_df["SEX_OF_INVOLVED_OFFICERS"].str.split("|")
	full_df["AGE_OF_INVOLVED_OFFICERS"] = full_df["AGE_OF_INVOLVED_OFFICERS"].str.split("|")
	full_df["YEARS_ON_FORCE_OF_INVOLVED_OFFICERS"] = full_df["YEARS_ON_FORCE_OF_INVOLVED_OFFICERS"].str.split("|")
	
	# HIGH LEVEL SUMMARY STATISTICS
	# Total complaints
	num_complaints = full_df.shape[0]

	# Year range
	min_year = full_df["COMPLAINT_YEAR"].min()
	max_year = full_df["COMPLAINT_YEAR"].max()

	# Complaints by year
	year = full_df.groupby("COMPLAINT_YEAR").size().to_frame()

	# Complaints by assignment
	assignment = full_df["ASSIGNMENT"].value_counts().to_frame()

	# Print Statements
	print()
	print("There were ", num_complaints, "reported complaints against CPD ", 
		"officers between ", min_year, " and ", max_year, ".")
	print()
	print("Below are the complaint breakdowns by year, jurisdictional", 
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

	return full_df

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
		"complaints were under IPRA or COPA jurisdiction beat between ", 
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


