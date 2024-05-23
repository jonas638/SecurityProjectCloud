#!/bin/bash
USER="Administrator"
PASSWORD=""
HOST=""
REMOTE_PATH="/C:/Users/Administrator/Desktop"
LOCAL_PATH="/home/clari-group6"
FILES=("20240512212147_Bloodhound.zip","ad_hc_project.local.html", azure-output.json)

for FILE in "${FILES[@]}"; do
        sshpass -p "$PASSWORD" scp "$USER@$HOST:$REMOTE_PATH/$FILE" "$LOCAL_PATH"
done