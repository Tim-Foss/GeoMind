import requests
import os
import json
import datetime
import math
import time

# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
bearer_token = os.environ.get("BEARER_TOKEN")


#specify the start time for the period we want to collect tweet info from
#datetime object (year, month, day, hour, minute, second, microsecond, tzinfo)
#Group began gathering on january 5th for capital riots
start_time = datetime.datetime(2021, 1, 5, 0, 0, 0, 0, datetime.timezone.utc)
#End time is about two weeks after the end of the riots
end_time = datetime.datetime(2021, 1, 19, 0, 0, 0, 0, datetime.timezone.utc)

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

    # "expansions": ",".join(EXPANSIONS),
    # "user.fields": ",".join(USER_FIELDS),
    # "tweet.fields": ",".join(TWEET_FIELDS),
    # "media.fields": ",".join(MEDIA_FIELDS),
    # "poll.fields": ",".join(POLL_FIELDS),
    # "place.fields": ",".join(PLACE_FIELDS),


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
    #data has been added to the 'data' list in the json
    json_response.pop('includes')

    #does not modify the 'meta' dict in the json object

def main():
    NUM_TWEETS = 2000
    max_results = 500 #this can max out to 500

    cumulative_json = None

    # Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
    # expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
    query_params = {
        'query': '(capital riot OR Washington D.C. OR #capitalriot) has:geo -is:retweet lang:en place_country:US',
        'expansions' : 'geo.place_id',
        'tweet.fields' : 'geo',
        'place.fields' : 'country_code,geo',
        'start_time': start_time.isoformat(),
        'end_time' : end_time.isoformat(),
        'max_results' : max_results,
        'next_token' : None
    }

    made_call = time.monotonic()

    for i in range(0, math.ceil(NUM_TWEETS / max_results)):
    
        json_response = connect_to_endpoint(search_url, query_params)

        if cumulative_json:
            combine_json_responses(cumulative_json, json_response)
        else:
            reformat_response(json_response)
            cumulative_json = json_response  

        query_params['next_token'] = json_response['meta']['next_token']

        #avoid exception for Too Many Requests (exceeding request rate limit of 1 request per second)
        #(Code taken from twarc/client2.py at https://github.com/DocNow/twarc/blob/main/twarc/client2.py):
        time.sleep(max(0, 3 - time.monotonic() - made_call))
        made_call = time.monotonic()

    out_file_name = 'offic_search_tweets_test9.txt'

    with open(out_file_name, 'a+') as file_obj:
        file_obj.write('%s\n' % json.dumps(cumulative_json, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()