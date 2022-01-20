# Dataset Construction:

## Files:

## Tweet_Collection.py

This file queries tweets related to the 06JAN21 United States Capitol Riots using the Twitter API. 

NOTE: use of this app requires an API BEARER TOKEN to be added to the user's environmental variables. To set environment variables, run the following line in a terminal:
export 'BEARER_TOKEN'='<your_bearer_token>'

This script calls json_to_csv.py's 'add_json_to_csv' function to append the Tweet content into a csv file. 

This file allows for specification of a start day in January to begin pulling tweets from. This date is specified by the 'start_date' variable in the main function. The number of days in January after the start date to pull tweets for is also specifiable by the 'num_days' variable in the main function. 

For each day specified to collect Tweets for, this script will pull tweets up to a maximum value indicated by the 'NUM_TWEETS' variable in the main function. 

## json_to_csv.py

This file is called from Tweet_Collection.py. It writes Tweet json objects formatted by Tweet_Collection.py to a csv file given the json object and optionally the file name.