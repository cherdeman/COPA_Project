# Preliminary analysis of COPA's Summary Case data
# Each row is a complaint, the summary data does not include names of
# complainants or officers

import os
import pandas as pd

##### CATEGORIES #####

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

	# Create category counts for all variables
	for race in race_cat:
		copa_ipra_df[" ".join(("Complaint_Count:", race))] = copa_ipra_df["RACE_OF_COMPLAINANTS"].str.count(race)

	for sex in sex_cat:
		copa_ipra_df[" ".join(("Complaint_Count:", sex))] = copa_ipra_df["SEX_OF_COMPLAINANTS"].str.count(sex)

	for age in age_cat:
		copa_ipra_df[" ".join(("Complaint_Count:", age))] = copa_ipra_df["AGE_OF_COMPLAINANTS"].str.count(age)

	for race in race_cat:
		copa_ipra_df[" ".join(("Officer_Count:", race))] = copa_ipra_df["RACE_OF_INVOLVED_OFFICERS"].str.count(race)

	for sex in sex_cat:
		copa_ipra_df[" ".join(("Officer_Count:", sex))] = copa_ipra_df["SEX_OF_INVOLVED_OFFICERS"].str.count(sex)

	for age in age_cat:
		copa_ipra_df[" ".join(("Officer_Count:", age))] = copa_ipra_df["AGE_OF_INVOLVED_OFFICERS"].str.count(age)

	for yrs in force_yrs:
		copa_ipra_df[" ".join(("Officer_Count:", yrs))] = copa_ipra_df["YEARS_ON_FORCE_OF_INVOLVED_OFFICERS"].str.count(yrs)

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
	output = []
	loop_len = min(k, len(name))

	for i in range(loop_len):
		pair = (name[i], count[i])
		output.append(pair)

	return output


def complaint_volume_race(copa_ipra_df, year = None, month = None):
	'''
	'''
	pass 

##### IPRA / COPRA COMPARISONS ####


