import requests
import os
import json
import datetime
import math
import time
import json_to_csv

# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
bearer_token = os.environ.get("BEARER_TOKEN")


#specify the start time for the period we want to collect tweet info from
#datetime object (year, month, day, hour, minute, second, microsecond, tzinfo)
#Group began gathering on january 5th for capital riots
start_time = datetime.datetime(2021, 1, 17, 0, 0, 0, 0, datetime.timezone.utc)
#End time is about two weeks after the end of the riots
end_time = datetime.datetime(2021, 1, 18, 0, 0, 0, 0, datetime.timezone.utc)

search_url = "https://api.twitter.com/2/tweets/search/all"


EXPANSIONS = [
    "author_id",
    "in_reply_to_user_id",
    "referenced_tweets.id",
    "referenced_tweets.id.author_id",
    "entities.mentions.username",
    "attachments.poll_ids",
    "attachments.media_keys",
    "geo.place_id",
]

USER_FIELDS = [
    "created_at",
    "description",
    "entities",
    "id",
    "location",
    "name",
    "pinned_tweet_id",
    "profile_image_url",
    "protected",
    "public_metrics",
    "url",
    "username",
    "verified",
    "withheld",
]

TWEET_FIELDS = [
    "attachments",
    "author_id",
    "context_annotations",
    "conversation_id",
    "created_at",
    "entities",
    "geo",
    "id",
    "in_reply_to_user_id",
    "lang",
    "public_metrics",
    "text",
    "possibly_sensitive",
    "referenced_tweets",
    "reply_settings",
    "source",
    "withheld",
]

MEDIA_FIELDS = [
    "alt_text",
    "duration_ms",
    "height",
    "media_key",
    "preview_image_url",
    "type",
    "url",
    "width",
    "public_metrics",
]

POLL_FIELDS = ["duration_minutes", "end_datetime", "id", "options", "voting_status"]

PLACE_FIELDS = [
    "contained_within",
    "country",
    "country_code",
    "full_name",
    "geo",
    "id",
    "name",
    "place_type",
]


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FullArchiveSearchPython"
    return r


def connect_to_endpoint(url, params):
    response = requests.request("GET", search_url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

#combines two tweet json response objects, adds entries from add_from into add_to json object'
def combine_json_responses(add_to, add_from):
    #update meta dictionary so that next_token from the newer json
    #is in the object after combining them
    add_to['meta'] = add_from['meta']

    reformat_response(add_from)

    #data entry is a list of dictionaries containing data from different tweets' fields
    add_to['data'].extend(add_from['data'])

def reformat_response(json_response):
    #adds all place object data from the 'includes' json dictionary into the json
    #'data' dictionary of the corresponding tweet.
    for entry in json_response['data']:
        flag = False
        for place_obj in json_response['includes']['places']:
            try:
                if (place_obj['id'] == entry['geo']['place_id']):
                    entry['geo'].update(place_obj.items())
                    flag = True
            except:
                pass

            if flag:
                #exit the inner loop after we have added the pertinent geo data
                break

    #removes the 'includes' dict from the json object after all pertinent
    #data has been added to the 'data' list in the json. the 'includes dictionary is
    #what contains the data scraped from various fields. place field data was already
    #added to the json_response at this point, so we through out the includes dict
    json_response.pop('includes')

    #does not modify the 'meta' dict in the json object

def main():
    
    #this variable indicates the maximum number of tweets that will be pulled per day
    NUM_TWEETS = 9500
    #max_results is the number of tweets to pull per api request
    max_results = 500 #this can max out to 500

    #start pulling tweets from one day increments starting with January <start_date> 2021
    start_date = 5
    #num_days is the number of days to pull tweets from:
    num_days = 14
    #Note: Not setup to pull tweets past JAN31 or num days cannot exceed 31 - start_date
    #^^This will generate a ValueError: day is out of range for month

    # Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
    # expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
    query_params = {
        'query': '(capital riot OR #capital riot OR sedition OR patriot OR proud boys OR national guard OR incite OR extremists OR #impeachtrumpnow) has:geo -is:retweet lang:en place_country:US',
        'expansions' : 'geo.place_id',
        'tweet.fields' : 'geo',
        'place.fields' : 'country_code,geo',
        'start_time': None,
        'end_time' : None,
        'max_results' : max_results,
        'next_token' : None
    }
    #a lot of tweets have the content: Just posted a photo @ Washington D.C. <url>...

    # Possible Query Keywords:
    # sedition 
    # proud boys 
    # #impeachtrumpnow
    # national guard 
    # incite OR inciting
    # extremists

    for start_day in range(start_date, num_days + start_date):
        start_time = datetime.datetime(2021, 1, start_day, 0, 0, 0, 0, datetime.timezone.utc)
        end_time = datetime.datetime(2021, 1, start_day+1, 0, 0, 0, 0, datetime.timezone.utc)
        
        query_params['start_time'] = start_time.isoformat()
        query_params['end_time'] = end_time.isoformat()

        out_csv_filename = 'jan_' + str(start_time.day) + '-' + str(end_time.day) + '_test_tweet_set.csv'#'test_tweet_ds.csv'
        next_token_filename = 'next_token_'+ str(start_time.day) + '-' + str(end_time.day) + '.txt'

        query_params['next_token'] = None

        for i in range(0, math.ceil(NUM_TWEETS / max_results)):
    
            json_response = connect_to_endpoint(search_url, query_params)
            made_call = time.monotonic()

            #print(f'json_response = {json_response}')

            #reformat the json before adding it to the csv
            reformat_response(json_response)
        

            #print the json response to a csv file
            json_to_csv.add_json_to_csv(json_obj = json_response, out_file_str = out_csv_filename)

            try:
                #set the next_token query param to be the next token in the meta field of 
                # the previous json resposnse so that the next response will be the next
                # tweets in the query.
                query_params['next_token'] = json_response['meta']['next_token']
                next_tok_msg = json_response['meta']['next_token']
            except KeyError:
                #entering this case means there are no more tweets that can be taken with this particular query
                next_tok_msg = 'no next token for query (tweet count reached for this query): ' + query_params['query']
                #break out of the loop searching tweets for this particular date after 
                #sleeping to prevent exceeding the request rate limit.
                time.sleep(max(0, 1.05 - (time.monotonic() - made_call)))
                with open(next_token_filename, 'w') as next_tok_file:
                    next_tok_file.write(next_tok_msg)
                break
        
            #writes the current next token to a file so that scraping tweets from multiple runs
            #of this function can pick up where it left off.
            with open(next_token_filename, 'w') as next_tok_file:
                next_tok_file.write(next_tok_msg)

            #avoid exception for Too Many Requests (exceeding request rate limit of 1 request per second)
            #(Code taken from twarc/client2.py at https://github.com/DocNow/twarc/blob/main/twarc/client2.py):
            time.sleep(max(0, 1.05 - (time.monotonic() - made_call)))


if __name__ == "__main__":
    main()