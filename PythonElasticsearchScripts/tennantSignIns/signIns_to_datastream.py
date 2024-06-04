import json
import os
import sys
import requests
from datetime import datetime, timedelta
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

def fetch_sign_ins(config, access_token, start_time=None):
    graph_api_endpoint = config['graph_api_sign_ins_endpoint']
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

def save_sign_ins_to_elasticsearch(sign_ins, es, index_name):
    for sign_in in sign_ins['value']:
        es.index(index=index_name, body=sign_in)

def update_last_query_time(last_query_time):
    with open('/home/admin/PythonElasticsearchScripts/tokens/signIns_token.txt', 'w') as file:
        file.write(last_query_time.isoformat())

config = load_config()


access_token = get_access_token(config['tenant_id'], config['client_id'], config['tenant_secret'])



def save_sign_ins_to_file(sign_ins, filename):
    with open(filename, 'w') as file:
        json.dump(sign_ins, file, indent=4)

def save_sign_ins_to_datastream(sign_ins, es, datastream_name):
    for sign_in in sign_ins['value']:
        if 'createdDateTime' in sign_in:
            sign_in['@timestamp'] = sign_in['createdDateTime']
        es.index(index=datastream_name, body=sign_in)

if __name__ == "__main__":
    
    es = Elasticsearch(
        config['elasticsearch_host'],
        basic_auth=(config['security-onion_username'], config['security-onion_password']),
        verify_certs=False
    )
    datastream_name = "sign_ins_stream"
    
    last_query_time = None
    try:
        with open('/home/admin/PythonElasticsearchScripts/tokens/signIns_token.txt', 'r') as file:
            last_query_time_str = file.read().strip()
            last_query_time = datetime.fromisoformat(last_query_time_str)
    except FileNotFoundError:
        pass 

    if last_query_time:
        try:
            sign_ins = fetch_sign_ins(config, access_token, start_time=last_query_time)
            print(sign_ins)
            if sign_ins['value']:
                last_sign_in_time_str = max(sign_in['createdDateTime'] for sign_in in sign_ins['value'])
                last_sign_in_time = datetime.fromisoformat(last_sign_in_time_str.replace("Z", "+00:00"))

                if last_sign_in_time > last_query_time:
                    save_sign_ins_to_datastream(sign_ins, es, datastream_name)
                    update_last_query_time(last_sign_in_time)
            else:
                print("No new sign ins")
        except Exception as e:
            print(f"Error fetching or indexing sign-ins: {str(e)}")
    else:
        try:
            sign_ins = fetch_sign_ins(config, access_token)
            if sign_ins['value']:
                initial_index_name = f"sign_ins_initial"
                save_sign_ins_to_datastream(sign_ins, es, datastream_name)
                last_sign_in_time = max(sign_in['createdDateTime'] for sign_in in sign_ins['value'])
                last_query_time = datetime.fromisoformat(last_sign_in_time.replace("Z", "+00:00"))
                update_last_query_time(last_query_time)
                print(f"Fetched initial sign-ins and indexed {len(sign_ins['value'])} sign-ins.")
            else:
                print("No initial sign-ins fetched. Exiting.")
                sys.exit(1)
        except Exception as e:
            print(f"Error fetching initial sign-ins: {str(e)}")
            sys.exit(1)