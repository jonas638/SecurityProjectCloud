import json
import sys
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

index_template = {
    "index_patterns": ["audit_logs_*"],
    "data_stream": {},
    "template": {
        "settings": {
            "index.lifecycle.name": "data_stream_lifecycle",
            "index.lifecycle.rollover_alias": "audit_logs_stream"
        }
    }
}


es = Elasticsearch(
        config['elasticsearch_host'],
        basic_auth=(config['security-onion_username'], config['security-onion_password']),
        verify_certs=False
    )

try:
    es.indices.put_index_template(name="audit_logs_template", body=index_template)
    print("Index template 'audit_logs_template' created successfully.")
    es.indices.create_data_stream(name="audit_logs_stream")
    print("Data stream 'audit_logs_stream' created successfully.")
except Exception as e:
    print(f"Error creating index template or data stream: {e}")
    sys.exit(1)
