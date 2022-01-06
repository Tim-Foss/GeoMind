#Dataset Construction:

##Files:

###Tweet_Scraping.py

This file queries tweets related to the 06JAN21 United States Capitol Riots. Writes a json object containing all tweet content into a text file.

###json_to_csv.py

This file converts the json file outputted by Tweet_Scraping.py into a csv format, by taking all relevant location related tweet fields for each tweet contained within the json object. The in_file_str variable in this file should be the same path/filename as the out_file_name variable in Tweet_Scraping.py.