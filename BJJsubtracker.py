# importing modules
import time
from datetime import date
from googleapiclient.discovery import build
from google.oauth2 import service_account
import matplotlib.pyplot as mpl
import numpy as np
import os
import copy
import csv


# creating class to organize data in
class SheetRow:
    SubName = ""                # submission name
    NumberAgainstOthers = 0     # number of times you used submission on others
    NumberAgainstYou = 0        # number of times others used submission on you


# initialization statement
print("BJJ SUBMISSION TRACKER INITIALIZING...")
time.sleep(0)

# GOOGLE SHEET IMPORT
# setting up variables for .json credentials and scope
SERVICE_ACCOUNT_FILE = 'bjjservicecredential.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# setting up credential variable for accessing Google Sheet
credentials_variable = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# The ID of the Google Sheet we are accessing
SPREADSHEET_ID = '12O20L6V5L3BRvl6hd1uOkOV880oxpb-dFybyZKbvMNw'

# initializing service variable
service = build('sheets', 'v4', credentials=credentials_variable)

# Call the Sheets API, store all data in values array
sheet = service.spreadsheets()


found = 0
found_index = 1
range_string_initial = "submissions!A"
row_start_index = 2
row_end_index = 27
while found == 0:  # try chunks of 25, checking all, then making another API call with the next 25
    range_string = range_string_initial + str(row_start_index) + ":C" + str(row_end_index)
    check_result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=range_string).execute()
    check_values = check_result.get('values', [])
    for i in check_values:
        if i[1].isnumeric():  # has to be done by letter
            found_index += 1
            continue
    found = 1

range_string_import = "submissions!A1:C" + str(found_index)
result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="submissions!A1:C25").execute()  # "submissions!A1:C25"
values = result.get('values', [])


# initializing arrays for graphs
SheetsSubNames = []
SheetsSubsSuccessful = []
SheetsSubmittedBy = []

SheetsSubmissions = []

LTDSubsSuccessful = []
LTDSubmittedBy = []

# transferring data from values into proper sub-arrays
for i in values:
    if i[0] != "":
        temp = SheetRow()
        temp.SubName = i[0]
        temp.NumberAgainstOthers = int(i[1])
        temp.NumberAgainstYou = int(i[2])
        SheetsSubmissions.append(temp)

for i in SheetsSubmissions:
    SheetsSubNames.append(i.SubName)


# IMPORT LONG TERM DATA
# importing long term data from .csv file
if os.path.isfile("LongTermJJSData.csv"):
    LTD = open("LongTermJJSData.csv", "r")  # opens for read if file does exist
else:
    LTD = open("LongTermJJSData.csv", "x")  # creates if file does not previously exist

LTD_read_string = LTD.read()  # reading from file
LTD.close()  # closing file
RowList = LTD_read_string.strip().split('\n')  # delimiting at newline characters
LTD_import_Submissions = []

# turning data read from .csv into usable class types
for i in RowList:
    IndividualRow = i.strip().split(',')  # delimiting each value for that row entry
    tempRow = SheetRow()
    tempRow.SubName = IndividualRow[0]
    tempRow.NumberAgainstOthers = int(IndividualRow[1])
    tempRow.NumberAgainstYou = int(IndividualRow[2])
    LTD_import_Submissions.append(tempRow)


# COPYING SHEET IMPORT DATA
SheetsSubmissionsCopy = copy.deepcopy(SheetsSubmissions)  # creating deep copy of submissions from google sheet import


# UPDATING SHEET IMPORT WITH LONG TERM DATA
LTD_Subs_Not_Updated = []

# updating values from import with long term data, has potential for O(n^2) but generally will be n
for i in LTD_import_Submissions:
    i_updated_bool = 0
    for k in SheetsSubmissionsCopy:
        if i.SubName == k.SubName:
            k.NumberAgainstOthers = i.NumberAgainstOthers + k.NumberAgainstOthers
            k.NumberAgainstYou = i.NumberAgainstYou + k.NumberAgainstYou
            i_updated_bool = 1
            break  # early k loop exit, since i has updated k
    if i_updated_bool == 0:
        LTD_Subs_Not_Updated.append(i)

# any rows that were not present in Google Sheets import have been added back on
if len(LTD_Subs_Not_Updated) != 0:
    for i in LTD_Subs_Not_Updated:
        SheetsSubmissionsCopy.append(i)


# SORTING DATA INTO ALPHABETICAL ORDER
# initializing alphabetical list but just adding the submission names that we stored right after we imported data
# from Google Sheets, not yet alphabetically sorted
Submission_Name_List_Alphabetical = []
for i in SheetsSubmissionsCopy:
    Submission_Name_List_Alphabetical.append(i.SubName)

# initializing lists for alphabetically sorted results
SheetsSubmissionsUpdatedSorted = []
SheetsSubmissionsSorted = []

# sorting the names into alphabetical order, which we will use to properly add the data rows (data structure)
Submission_Name_List_Alphabetical = sorted(Submission_Name_List_Alphabetical)
SheetsSubNamesAlphabetical = sorted(SheetsSubNames)

# for loop to add updated submissions in correct order for combined data
for i in Submission_Name_List_Alphabetical:
    for k in SheetsSubmissionsCopy:
        if i == k.SubName:
            SheetsSubmissionsUpdatedSorted.append(k)
            break  # early k loop exit, since k has been appended

for i in SheetsSubmissionsUpdatedSorted:
    LTDSubsSuccessful.append(int(i.NumberAgainstOthers))
    LTDSubmittedBy.append(int(i.NumberAgainstYou))

# for loop to add submissions in correct order for Google Sheet import data
for i in SheetsSubNamesAlphabetical:
    for k in SheetsSubmissions:
        if i == k.SubName:
            SheetsSubmissionsSorted.append(k)
            break  # early k loop exit, since k has been appended


# adding to lists necessary for graphing of Google Sheet Import
for i in SheetsSubmissionsSorted:
    SheetsSubsSuccessful.append(int(i.NumberAgainstOthers))
    SheetsSubmittedBy.append(int(i.NumberAgainstYou))


# STORING UPDATED DATA
with open('LongTermJJSData.csv', 'w', encoding='UTF8', newline='') as file:
    writer = csv.writer(file)

    temp_Row = []

    for i in SheetsSubmissionsUpdatedSorted:
        temp_Row = [i.SubName, i.NumberAgainstOthers, i.NumberAgainstYou]
        writer.writerow(temp_Row)

# GRAPHING
barWidth = 0.25
current_date = date.today().strftime("%m/%d/%y")
current_date_underscore = date.today().strftime("%m_%d_%y")

# graph 1 (Daily)
mpl.subplots(figsize=(12, 8))

br1 = np.arange(len(SheetsSubsSuccessful))  # look into why use np
br2 = [x + barWidth for x in br1]


mpl.bar(br1, SheetsSubsSuccessful, color='g', width=barWidth, label='# of Successful Submissions')
mpl.bar(br2, SheetsSubmittedBy, color='r', width=barWidth, label='# of Times Submitted')

mpl.xlabel("Submission Names")
mpl.ylabel("# of times submission used by you/used by others")
mpl.xticks([r + barWidth for r in range(len(SheetsSubsSuccessful))], SheetsSubNamesAlphabetical, ha='right',
           rotation=45,
           fontsize=8)

graph_title_string = "Comparison of number of successful submissions and number of times submitted (DAILY AMOUNT - " \
                     + current_date + ")"
mpl.title(graph_title_string)
mpl.legend()
mpl.yticks(np.arange(min(SheetsSubsSuccessful), max(SheetsSubsSuccessful) + 1, 1))
mpl.gcf().subplots_adjust(bottom=0.15)

# save graph onto computer
mpl.savefig("C:/Users/parke/Desktop/Desktop/Applications/BJJ_Statistics/" + current_date_underscore + "_graph.png")

# graph 2 (Long Term Data)
mpl.subplots(figsize=(12, 8))


br1 = np.arange(len(SheetsSubsSuccessful))  # look into why use np
br2 = [x + barWidth for x in br1]


mpl.bar(br1, LTDSubsSuccessful, color='g', width=barWidth, label='# of Successful Submissions')
mpl.bar(br2, LTDSubmittedBy, color='r', width=barWidth, label='# of Times Submitted')

mpl.xlabel("Submission Names")
mpl.ylabel("# of times submission used by you/used by others")
mpl.xticks([r + barWidth for r in range(len(LTDSubsSuccessful))], Submission_Name_List_Alphabetical, ha='right',
           rotation=45,
           fontsize=8)

graph_title_string = "Comparison of number of successful submissions and number of times submitted (LONG TERM DATA)"
mpl.title(graph_title_string)
mpl.legend()
mpl.yticks(np.arange(min(LTDSubsSuccessful), max(LTDSubsSuccessful) + 1, 1))
mpl.gcf().subplots_adjust(bottom=0.15)
mpl.locator_params(axis='y', nbins=10)

# save graph onto computer
mpl.savefig("C:/Users/parke/Desktop/Desktop/Applications/BJJ_Statistics/LongTermData_graph.png")


# RESETTING DATA IN GOOGLE SHEETS
zeroes_list = []
for i in range(len(Submission_Name_List_Alphabetical)):
    zeroes_list.append(0)
zeroes = [
    zeroes_list,
]
Submission_Name_List_Alphabetical_List = [
    Submission_Name_List_Alphabetical
]
update_name_values = {
    'values': Submission_Name_List_Alphabetical_List,
    'majorDimension': 'COLUMNS'
}
update_you_values = {
    'values': zeroes,
    'majorDimension': 'COLUMNS',
}
update_others_values = {
    'values': zeroes,
    'majorDimension': 'COLUMNS',
}
result1 = service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range="submissions!A2:A50",
                                                 valueInputOption='RAW', body=update_name_values).execute()
result = service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range="submissions!B2:B50",
                                                valueInputOption='RAW', body=update_you_values).execute()
result2 = service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range="submissions!C2:C50",
                                                 valueInputOption='RAW', body=update_others_values).execute()

# program end confirmation message
time.sleep(0)
print("BJJ SUBMISSION TRACKER SHUTTING DOWN...")
