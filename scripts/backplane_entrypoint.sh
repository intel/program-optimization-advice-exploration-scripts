#!/bin/bash

# Navigate to the script directory
script_dir="$(dirname "$0")"
cd $script_dir


# # # # Run install.py
#python3 install.py
#readlink -f install.py > /tmp/readlink.txt

# Only start server if web folder is set up
sudo service ssh start
echo "Current script PID entrypoint: $$"
exec su qaas
# # # # start apache
# exec apachectl -D FOREGROUND
