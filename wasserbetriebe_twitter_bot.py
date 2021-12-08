from pprint import pprint

import requests
import os
import json

# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>' or in PyCharm add  environment variable for the script Run/Debug configuration
# -> Edit Configuration -> Environment Variables
bearer_token = os.environ.get("BEARER_TOKEN")
search_url = "https://api.twitter.com/2/tweets/search/recent"       # recent - return tweets for last 7 calendar days

# Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
# expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
# https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-recent
query_params = {'query': 'from:wasserbetriebe', 'tweet.fields': 'created_at',
                'end_time': '2021-12-08T04:59:59Z'}  # here end_time should be calculated dynamically


# or switch to "since_id" optional parameter. In this case we need to store id of the latest processed tweet or pass start_time

def bearer_authorization(request):
    # Method required by bearer token authentication.
    request.headers["Authorization"] = f"Bearer {bearer_token}"
    request.headers["User-Agent"] = "v2RecentSearchPython"
    return request


def search_tweets():
    response = requests.get(search_url, auth=bearer_authorization, params=query_params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def main():
    json_response = search_tweets()
    # print(json.dumps(json_response, indent=4, sort_keys=True))        # parse, format and sort response Json text
    pprint(json_response)  # does the same as previous code line, but less pretty


if __name__ == "__main__":
    main()
