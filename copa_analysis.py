# Preliminary analysis of COPA's Summary Case data
# Each row is a complaint, the summary data does not include names of
# complainants or officers

import os
import pandas as pd
import matplotlib.pyplot as plt

##### CATEGORIES #####

categories = [race_cat, sex_cat, age_cat, force_yrs]

race_cat = ['African American / Black', 'American Indian or Alaskan Native', 
'Asian or Pacific Islander', 'Hispanic', 'Unknown', 'White']

sex_cat = ['Female', 'Male', 'Unknown']

age_cat = ['0-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70+', 'Unknown']

force_yrs = ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30+', 'Unknown']

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

	# Extract COPA and IPRA assignments
	copa_ipra_df = full_df[full_df["ASSIGNMENT"].str.contains("IPRA")
	 | full_df["ASSIGNMENT"].str.contains("COPA")]

	# Create category counts for all variables - Simplify this
	for race in race_cat:
		copa_ipra_df[" ".join(("Complaint_Count_Race:", race))] = copa_ipra_df["RACE_OF_COMPLAINANTS"].str.count(race)

	for sex in sex_cat:
		copa_ipra_df[" ".join(("Complaint_Count_Sex:", sex))] = copa_ipra_df["SEX_OF_COMPLAINANTS"].str.count(sex)

	for age in age_cat:
		copa_ipra_df[" ".join(("Complaint_Count_Age:", age))] = copa_ipra_df["AGE_OF_COMPLAINANTS"].str.count(age)

	# Calculate Total
	comp_lst = [col for col in list(copa_ipra_df.columns) if "Complaint_Count_Age" in col]
	copa_ipra_df["Complaint_Count: Total"] = copa_ipra_df[comp_lst].sum(axis = 1)

	for race in race_cat:
		copa_ipra_df[" ".join(("Officer_Count_Race:", race))] = copa_ipra_df["RACE_OF_INVOLVED_OFFICERS"].str.count(race)

	for sex in sex_cat:
		copa_ipra_df[" ".join(("Officer_Count_Sex:", sex))] = copa_ipra_df["SEX_OF_INVOLVED_OFFICERS"].str.count(sex)

	for age in age_cat:
		copa_ipra_df[" ".join(("Officer_Count_Age:", age))] = copa_ipra_df["AGE_OF_INVOLVED_OFFICERS"].str.count(age)

	for yrs in force_yrs:
		copa_ipra_df[" ".join(("Officer_Count_Yrs:", yrs))] = copa_ipra_df["YEARS_ON_FORCE_OF_INVOLVED_OFFICERS"].str.count(yrs)

	# Calculate Total
	off_lst = [col for col in list(copa_ipra_df.columns) if "Officer_Count_Yrs" in col]
	copa_ipra_df["Officer_Count: Total"] = copa_ipra_df[off_lst].sum(axis = 1)

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
	
	# Subset dataframe by date
	date_df = date_subset(copa_ipra_df, year, month)

	#Subset dataframe by beat
	beat_df = date_df[date_df["BEAT"].map(lambda x: beat in x)]

	# Tabulate complaint category counts and convert to individual lists
	complaint_counts = beat_df["CURRENT_CATEGORY"].value_counts().to_frame()
	name = complaint_counts["CURRENT_CATEGORY"].index.tolist()
	count = complaint_counts["CURRENT_CATEGORY"].values.tolist()

	# Create output list
	output = []
	loop_len = min(k, len(name))

	for i in range(loop_len):
		pair = (name[i], count[i])
		output.append(pair)

	return output


def volume_by_complainant_char(copa_ipra_df, characteristic, year = None, month = None):
	'''
	Find the total volume of complaints by age, sex, or gender of the
	complainants. Note that since some complaints have multiple complainants,
	the total volume will be greater than the total complaint volume.

	Inputs:
		copa_ipra_df: (pandas dataframe) dataframe that excludes BIA cases
		characteristic: (string) represents characteristic of interest, must
			be age, sex, or race

	Returns:
		List of tuples representing characteristic, volume pairs
	'''
	# Choose characteristic category
	char_cat = complainant_category(characteristic)

	# Subset dataframe by date
	date_df = date_subset(copa_ipra_df, year, month)
	
	# Process data
	col_list = list(copa_ipra_df.columns)
	output = []

	for char in char_cat:
		col = [x for x in col_list if "Complaint" in x and char in x]
		vol = date_df[col].sum().iloc[0]
		pair = (char, vol)
		output.append(pair)

	return output


def volume_by_officer_char(copa_ipra_df, characteristic, year = None, month = None):
	'''
	Find the total volume of complaints by age, sex, gender, or years on the 
	force of the officers. Note that since some complaints have multiple 
	officers, the total volume will be greater than the total complaint 
	volume.

	Inputs:
		copa_ipra_df: (pandas dataframe) dataframe that excludes BIA cases
		characteristic: (string) represents characteristic of interest, must
			be age, sex, race, or years
		year: (int) optional year of interest
		month: (int) optional month of interest

	Returns:
		List of tuples representing characteristic, volume pairs
	'''
	# Choose characteristic category
	char_cat = officer_category(characteristic)

	# Subset dataframe by date
	date_df = date_subset(copa_ipra_df, year, month)

	# Process data
	col_list = list(copa_ipra_df.columns)
	output = []

	for char in char_cat:
		col = [x for x in col_list if "Officer" in x and char in x]
		vol = date_df[col].sum().iloc[0]
		pair = (char, vol)
		output.append(pair)

	return output


def volume_by_officer_complainant_char(copa_ipra_df, off_char, comp_char, year = None, month = None):
	'''
	'''


##### IPRA / COPRA COMPARISONS #####


##### HELPER FUNCTIONS #####

def date_subset(copa_ipra_df, year = None, month = None):
	'''
	Subsets dataset to include only specified year and/or months

	Inputs:
		copa_ipra_df: (pandas dataframe) dataframe that excludes BIA cases
		year: (int) optional year of interest
		month: (int) optional month of interest

	Returns: Pandas dataframe
	'''
	if year == None and month == None:
		date_df = copa_ipra_df
	elif year != None and month == None:
		date_df = copa_ipra_df[copa_ipra_df["COMPLAINT_YEAR"] == year]
	elif year == None and month != None:
		date_df = copa_ipra_df[copa_ipra_df["COMPLAINT_MONTH"] == month]
	else:
		year_df = copa_ipra_df[copa_ipra_df["COMPLAINT_YEAR"] == year]
		date_df = year_df[year_df["COMPLAINT_MONTH"] == month]

	return date_df

def complainant_category(characteristic):
	'''
	'''
	if characteristic == "sex":
		char_cat = sex_cat
	elif characteristic == "race":
		char_cat = race_cat
	else:
		char_cat = age_cat

	return char_cat


def officer_category(characteristic):
	'''
	'''
	if characteristic == "sex":
		char_cat = sex_cat
	elif characteristic == "race":
		char_cat = race_cat
	elif characteristic == "age":
		char_cat = age_cat
	else:
		char_cat = force_yrs

	return char_cat


def show_barchart(output):
	'''
	Inputs:
		output: (list of tuples)
	'''
	categories = []
	values = []

	for tup in output:
		categories.append(tup[0])
		values.append(tup[1])

	plt.bar(categories, values, align = "center", alpha = 0.5)

	plt.show()



