#!/bin/bash

python3 /home/admin/PythonElasticsearchScripts/datastreams/datastream_audit_logs.py
python3 /home/admin/PythonElasticsearchScripts/datastreams/datastream_sec_score.py
python3 /home/admin/PythonElasticsearchScripts/datastreams/datastream_signIns.py


(crontab -l | grep -v 'initial_streams.sh') | crontab -