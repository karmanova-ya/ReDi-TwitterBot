from pprint import pprint

import requests
import os
import json
from pathlib import Path

# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>' or in PyCharm add  environment variable for the script Run/Debug configuration
# -> Edit Configuration -> Environment Variables
bearer_token = os.environ.get("BEARER_TOKEN")
# search_url = "https://api.twitter.com/2/tweets/search/recent"       # recent - return tweets for last 7 calendar days
search_url = "https://api.twitter.com/2/users/18899040/tweets"  # recent - return tweets for last 7 calendar days


# Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
# expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
# https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-recent
# query_params = {'query': 'from:wasserbetriebe', 'tweet.fields': 'created_at',
#                 'end_time': '2021-12-08T04:59:59Z'}  # here end_time should be calculated dynamically


# or switch to "since_id" optional parameter. In this case we need to store id of the latest processed tweet or pass start_time

def bearer_authorization(request):
    # Method required by bearer token authentication.
    request.headers["Authorization"] = f"Bearer {bearer_token}"
    request.headers["User-Agent"] = "v2RecentSearchPython"
    return request


def search_tweets(query_params):
    response = requests.get(search_url, auth=bearer_authorization, params=query_params)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def filter_tweets(tweets):
    filtered_tweets = []
    for tweet in tweets:
        tweet_lower = tweet.lower()
        if 'trinkwasser' in tweet_lower:
            filtered_tweets.append(tweet)
        elif 'h20' in tweet_lower:
            filtered_tweets.append(tweet)
        elif 'wastewater' in tweet_lower:
            filtered_tweets.append(tweet)
        elif 'wasserkreislauf' in tweet_lower:
            filtered_tweets.append(tweet)

    return filtered_tweets


def filter_tweets_v2(tweet_id_text_dictionary):
    filtered_tweets = {}
    for key, value in tweet_id_text_dictionary.items():
        tweet_lower = value.lower()
        if 'trinkwasser' in tweet_lower:
            filtered_tweets[key] = value
        elif 'h20' in tweet_lower:
            filtered_tweets[key] = value
        elif 'wastewater' in tweet_lower:
            filtered_tweets[key] = value
        elif 'wasserkreislauf' in tweet_lower:
            filtered_tweets[key] = value
    return filtered_tweets


def write_meta_file(latest_processed_tweet_id):
    if os.path.exists("wasserbetriebe_twitter_bot_meta_info.txt"):  # clean up previous file
        os.remove("wasserbetriebe_twitter_bot_meta_info.txt")
    f = open("wasserbetriebe_twitter_bot_meta_info.txt", "x")
    f.write(latest_processed_tweet_id)
    f.close()


def search_next_page(next_page_token):
    query_params = {'pagination_token': next_page_token}
    response = requests.get(search_url, auth=bearer_authorization, params=query_params)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def main():
    wasserbetriebe_twitter_bot_meta_info = Path("wasserbetriebe_twitter_bot_meta_info.txt")
    query_params = {'start_time': '2021-12-01T00:00:00Z', 'tweet.fields': 'created_at', 'max_results': 100}
    if wasserbetriebe_twitter_bot_meta_info.is_file():
        with open(wasserbetriebe_twitter_bot_meta_info) as f:
            lines = f.readlines()
            latest_processed_tweet_id = lines[0]
            query_params['since_id'] = latest_processed_tweet_id
    else:
        print("Meta file does not exist")
    json_response = search_tweets(query_params)

    if 'meta' in json_response and 'newest_id' in json_response['meta']:
        latest_processed_tweet_id = json_response['meta']['newest_id']
        write_meta_file(latest_processed_tweet_id)
    data_ = json_response['data']
    tweet_id_text_dictionary = {}
    for tweet in data_:
        tweet_id_text_dictionary[tweet['id']] = tweet['text']
    filtered_tweets = filter_tweets_v2(tweet_id_text_dictionary)
    print(filtered_tweets)
    # print(json.dumps(json_response, indent=4, sort_keys=True))        # parse, format and sort response Json text
    # pprint(json_response)  # does the same as previous code line, but less pretty


if __name__ == "__main__":
    main()
