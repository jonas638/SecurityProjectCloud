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


config = load_config()

# Define index template settings
index_template = {
    "index_patterns": ["sign_ins_*"],
    "data_stream": {},
    "template": {
        "settings": {
            "index.lifecycle.name": "data_stream_lifecycle",
            "index.lifecycle.rollover_alias": "sign_ins_stream",
        },
        "mappings": {
            "properties": {
                "resourceDisplayName": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "ignore_above": 256,
                            "type": "keyword"
                        }
                    }
                },
                "resourceId": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "ignore_above": 256,
                            "type": "keyword"
                        }
                    }
                },
                "deviceDetail": {
                    "type": "object",
                    "properties": {
                        "displayName": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "ignore_above": 256,
                                    "type": "keyword"
                                }
                            }
                        },
                        "browser": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "ignore_above": 256,
                                    "type": "keyword"
                                }
                            }
                        },
                        "trustType": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "ignore_above": 256,
                                    "type": "keyword"
                                }
                            }
                        },
                        "deviceId": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "ignore_above": 256,
                                    "type": "keyword"
                                }
                            }
                        },
                        "operatingSystem": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "ignore_above": 256,
                                    "type": "keyword"
                                }
                            }
                        },
                        "isCompliant": {
                            "type": "boolean"
                        },
                        "isManaged": {
                            "type": "boolean"
                        }
                    }
                },
                "appDisplayName": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "ignore_above": 256,
                            "type": "keyword"
                        }
                    }
                },
                "isInteractive": {
                    "type": "boolean"
                },
                "riskLevelDuringSignIn": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "ignore_above": 256,
                            "type": "keyword"
                        }
                    }
                },
                "conditionalAccessStatus": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "ignore_above": 256,
                            "type": "keyword"
                        }
                    }
                },
                "ipAddress": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "ignore_above": 256,
                            "type": "keyword"
                        }
                    }
                },
                "clientAppUsed": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "ignore_above": 256,
                            "type": "keyword"
                        }
                    }
                },
                "createdDateTime": {
                    "type": "date"
                },
                "userDisplayName": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "ignore_above": 256,
                            "type": "keyword"
                        }
                    }
                },
                "riskLevelAggregated": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "ignore_above": 256,
                            "type": "keyword"
                        }
                    }
                },
                "userId": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "ignore_above": 256,
                            "type": "keyword"
                        }
                    }
                },
                "riskDetail": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "ignore_above": 256,
                            "type": "keyword"
                        }
                    }
                },
                "appId": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "ignore_above": 256,
                            "type": "keyword"
                        }
                    }
                },
                "correlationId": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "ignore_above": 256,
                            "type": "keyword"
                        }
                    }
                },
                "location": {
                    "type": "object",
                    "properties": {
                        "countryOrRegion": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "ignore_above": 256,
                                    "type": "keyword"
                                }
                            }
                        },
                        "city": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "ignore_above": 256,
                                    "type": "keyword"
                                }
                            }
                        },
                        "geoCoordinates": {
                            "type": "object",
                            "properties": {
                                "latitude": {
                                    "type": "float"
                                },
                                "longitude": {
                                    "type": "float"
                                }
                            }
                        },
                        "state": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "ignore_above": 256,
                                    "type": "keyword"
                                }
                            }
                        }
                    }
                },
                "id": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "ignore_above": 256,
                            "type": "keyword"
                        }
                    }
                },
                "riskState": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "ignore_above": 256,
                            "type": "keyword"
                        }
                    }
                },
                "userPrincipalName": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "ignore_above": 256,
                            "type": "keyword"
                        }
                    }
                },
                "status": {
                    "type": "object",
                    "properties": {
                        "failureReason": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "ignore_above": 256,
                                    "type": "keyword"
                                }
                            }
                        },
                        "errorCode": {
                            "type": "long"
                        },
                        "additionalDetails": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "ignore_above": 256,
                                    "type": "keyword"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}


es = Elasticsearch(
    config['elasticsearch_host'],
    basic_auth=(config['security-onion_username'], config['security-onion_password']),
    verify_certs=False
)


try:
    es.indices.put_index_template(name="sign_ins_template", body=index_template)
    print("Index template 'sign_ins_template' created successfully.")

    es.indices.create_data_stream(name="sign_ins_stream")
    print("Data stream 'sign_ins_stream' created successfully.")
except Exception as e:
    print(f"Error creating index template or data stream: {e}")
    sys.exit(1)