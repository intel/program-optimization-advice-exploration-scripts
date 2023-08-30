#!/bin/bash

# Navigate to the script directory
cd "$(dirname "$0")"

echo "test hello world"


# # # # Run install.py
python3 install.py

python3 start_server.py

exec su qaas
# # # # start apache
# exec apachectl -D FOREGROUND