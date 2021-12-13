import requests
import os
import datetime
from pathlib import Path

# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>' or in PyCharm add  environment variable for the script Run/Debug configuration
# -> Edit Configuration -> Environment Variables
bearer_token = os.environ.get("BEARER_TOKEN")
search_url = "https://api.twitter.com/2/users/18899040/tweets"  # recent - return tweets for last 7 calendar days


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


def filter_tweets(tweet_id_text_dictionary):
    filtered_tweets = {}
    for key, value in tweet_id_text_dictionary.items():
        tweet_lower = value['text'].lower()
        if 'entwarnung' in tweet_lower:
            filtered_tweets[key] = value
        elif 'bauarbeiten' in tweet_lower:
            filtered_tweets[key] = value
        elif 'gesundheitsamt' in tweet_lower:
            filtered_tweets[key] = value
        elif 'leitungswasser' in tweet_lower:
            filtered_tweets[key] = value
        elif 'keime' in tweet_lower:
            filtered_tweets[key] = value
        elif 'qualitätsmängeln' in tweet_lower:
            filtered_tweets[key] = value

    return filtered_tweets


def write_meta_file(latest_processed_tweet_id):
    if os.path.exists("wasserbetriebe_twitter_bot_meta_info.txt"):  # clean up previous file
        os.remove("wasserbetriebe_twitter_bot_meta_info.txt")
    f = open("wasserbetriebe_twitter_bot_meta_info.txt", "x")
    f.write(latest_processed_tweet_id)
    f.close()


def prepare_query_parameters():
    wasserbetriebe_twitter_bot_meta_info = Path("wasserbetriebe_twitter_bot_meta_info.txt")
    #today = datetime.datetime.today()
    #week_ago = today - datetime.timedelta(weeks=1)
    #date_in_isoformat = week_ago.isoformat(timespec="seconds")
    query_params = {'start_time': '2021-08-01T00:00:00Z', 'tweet.fields': 'created_at', 'max_results': 100}
    if wasserbetriebe_twitter_bot_meta_info.is_file():
        with open(wasserbetriebe_twitter_bot_meta_info) as f:
            lines = f.readlines()
            latest_processed_tweet_id = lines[0]
            query_params['since_id'] = latest_processed_tweet_id
    else:
        print("Meta file does not exist")
    return query_params


def prepare_tweets_response(json_response):
    if json_response['meta']['result_count'] == 0:
        return {}

    if 'meta' in json_response and 'newest_id' in json_response['meta']:
        latest_processed_tweet_id = json_response['meta']['newest_id']
        write_meta_file(latest_processed_tweet_id)
    data_ = json_response['data']
    tweet_id_text_dictionary = {}
    for tweet in data_:
        tweet_info = {
            'text': tweet['text'],
            'date': tweet['created_at']
        }
        tweet_id_text_dictionary[tweet['id']] = tweet_info

    return tweet_id_text_dictionary


def fetch_tweets_from_last_week():
    query_params = prepare_query_parameters()
    json_response = search_tweets(query_params)
    tweet_id_text_dictionary = prepare_tweets_response(json_response)
    return tweet_id_text_dictionary


def show_tweets(tweets):
    tweet_number = 0
    for tweet_id, tweet_info in tweets.items():
        tweet_number += 1
        print(f"Tweet: {tweet_number} \n https://twitter.com/wasserbetriebe/status/{tweet_id}: \n {tweet_info['date']} \n {tweet_info['text']}")
    if tweet_number == 0:
        print("No new tweets found")


def main():
    tweet_id_text_dictionary = fetch_tweets_from_last_week()
    filtered_tweets = filter_tweets(tweet_id_text_dictionary)
    show_tweets(filtered_tweets)


if __name__ == "__main__":
    main()