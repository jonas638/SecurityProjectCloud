import json
import os
import sys
import requests
import warnings
from datetime import datetime, timezone, timedelta
from urllib3.exceptions import InsecureRequestWarning
from elasticsearch import Elasticsearch

# Suppress only the specific warning
warnings.filterwarnings("ignore", category=InsecureRequestWarning)

def load_config():
    config_path = '/home/admin/PythonElasticsearchScripts/config.json'
    
    if not os.path.exists(config_path):
        print(f"Configuration file {config_path} does not exist.")
        sys.exit(1)
    
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    
    required_keys = ['elasticsearch_host', 'graph_api_audit_endpoint', 'tenant_secret', 'client_id', 'tenant_id', 'security-onion_username', 'security-onion_password']

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

def fetch_audit_logs(config, access_token, start_time=None):
    graph_api_endpoint = config['graph_api_audit_endpoint']
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    params = {}
    if start_time:
        start_datetime = start_time.isoformat()
        params['$filter'] = f"activityDateTime ge {start_datetime}"

    response = requests.get(graph_api_endpoint, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def update_last_query_time(last_query_time):
    with open('/home/admin/PythonElasticsearchScripts/tokens/audit_token.txt', 'w') as file:
        file.write(last_query_time.isoformat().replace("+00:00", "Z"))

def read_last_query_time():
    try:
        with open('/home/admin/PythonElasticsearchScripts/tokens/audit_token.txt', 'r') as file:
            last_query_time_str = file.read().strip()
            last_query_time = datetime.fromisoformat(last_query_time_str.rstrip('Z')).replace(tzinfo=timezone.utc)
            return last_query_time
    except FileNotFoundError:
        return None

def save_audit_logs_to_datastream(audit_logs, es, datastream_name):
    max_datetime_str = None

    for audit_log in audit_logs['value']:
        activity_datetime_str = audit_log["activityDateTime"]
        
        if not max_datetime_str or activity_datetime_str > max_datetime_str:
            max_datetime_str = activity_datetime_str

        audit_log["@timestamp"] = activity_datetime_str
        es.index(index=datastream_name, body=audit_log)
    
    if max_datetime_str:
        update_last_query_time(datetime.fromisoformat(max_datetime_str.replace("Z", "+00:00")).replace(tzinfo=timezone.utc))

config = load_config()

if __name__ == "__main__":
    access_token = get_access_token(config['tenant_id'], config['client_id'], config['tenant_secret'])

    es = Elasticsearch(
        config['elasticsearch_host'],
        basic_auth=(config['security-onion_username'], config['security-onion_password']),
        verify_certs=False
    )

    datastream_name = "audit_logs_stream"

    last_query_time_saved = read_last_query_time()

    try:
        if last_query_time_saved:
            audit_logs = fetch_audit_logs(config, access_token, start_time=last_query_time_saved)
            if audit_logs['value']:
                save_audit_logs_to_datastream(audit_logs, es, datastream_name)
                print(f"Fetched and indexed {len(audit_logs['value'])} new audit logs.")
            else:
                print("No new audit logs to fetch.")
        else:
            audit_logs = fetch_audit_logs(config, access_token)
            if audit_logs['value']:
                save_audit_logs_to_datastream(audit_logs, es, datastream_name)
                print(f"Fetched initial audit logs and indexed {len(audit_logs['value'])} audit logs.")
            else:
                print("No initial audit logs fetched. Exiting.")
                sys.exit(1)
    except Exception as e:
        print(f"Error fetching or indexing audit logs: {str(e)}")
        sys.exit(1)
