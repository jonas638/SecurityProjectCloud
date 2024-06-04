import json
import os
import sys
import requests
from datetime import datetime, timedelta
from dateutil.parser import parse as date_parse
from elasticsearch import Elasticsearch

def load_config():
    config_path = '/home/admin/PythonElasticsearchScripts/config.json'
    
    if not os.path.exists(config_path):
        print(f"Configuration file {config_path} does not exist.")
        sys.exit(1)
    
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    
    required_keys = ['elasticsearch_host','graph_api_security_endpoint','tenant_secret','client_id','tenant_id','security-onion_username','security-onion_password']

    for key in required_keys:
        if key not in config or not config[key]:
            print(f"Missing or empty value for required key '{key}' in configuration file.")
            sys.exit(1)
    
    return config

def get_access_token(tenant_id, client_id, client_secret):
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    token_url = f"{authority}/oauth2/v2.0/token"
    token_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials"
    }
    token_response = requests.post(token_url, data=token_data)
    token_response.raise_for_status()
    return token_response.json()['access_token']

def fetch_security_scores(config, access_token, start_time=None):
    graph_api_endpoint = config['graph_api_security_endpoint']
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    params = {}
    if start_time:
        start_datetime = (start_time + timedelta(seconds=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
        params['$filter'] = f"createdDateTime ge {start_datetime}"

    url = f"{graph_api_endpoint}"
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def update_last_query_time(last_query_time):
    with open('/home/admin/PythonElasticsearchScripts/tokens/score_token.txt', 'w') as file:
        file.write(last_query_time.isoformat())

def read_last_query_time():
    try:
        with open('/home/admin/PythonElasticsearchScripts/tokens/score_token.txt', 'r') as file:
            last_query_time_str = file.read().strip()
            last_query_time = datetime.fromisoformat(last_query_time_str)
            return last_query_time
    except FileNotFoundError:
        return None

def save_security_scores_to_datastream(scores, es, datastream_name):
    for score in scores['value']:
        score["@timestamp"] = score["createdDateTime"]
        es.index(index=datastream_name, body=score)

config = load_config()
if __name__ == "__main__":
    access_token = get_access_token(config['tenant_id'], config['client_id'], config['tenant_secret'])

    es = Elasticsearch(
        config['elasticsearch_host'],
        basic_auth=(config['security-onion_username'], config['security-onion_password']),
        verify_certs=False
    )

    datastream_name = "security_scores_stream"

    last_query_time_saved = read_last_query_time()

    try:
        if last_query_time_saved:
            scores = fetch_security_scores(config, access_token, start_time=last_query_time_saved)
            if scores['value']:
                last_score_time_str = max(score['createdDateTime'] for score in scores['value'])
                last_score_time = datetime.fromisoformat(last_score_time_str.replace("Z", "+00:00"))

                if last_score_time > last_query_time_saved:
                    save_security_scores_to_datastream(scores, es, datastream_name)
                    update_last_query_time(last_score_time)
                    print(f"Fetched and indexed {len(scores['value'])} new security scores.")
                else:
                    print("No new security scores to fetch.")
            else:
                print("No new security scores to fetch.")
        else:
            scores = fetch_security_scores(config, access_token)
            if scores['value']:
                save_security_scores_to_datastream(scores, es, datastream_name)
                last_score_time_str = max(score['createdDateTime'] for score in scores['value'])
                last_query_time_saved = datetime.fromisoformat(last_score_time_str.replace("Z", "+00:00"))
                update_last_query_time(last_query_time_saved)
                print(f"Fetched initial security scores and indexed {len(scores['value'])} security scores.")
            else:
                print("No initial security scores fetched. Exiting.")
                sys.exit(1)
    except Exception as e:
        print(f"Error fetching or indexing security scores: {str(e)}")
        sys.exit(1)
