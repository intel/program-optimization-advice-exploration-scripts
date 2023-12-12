#!/bin/bash

# Navigate to the script directory
script_dir="$(dirname "$0")"
cd $script_dir

echo "test hello world"


# # # # Run install.py
#python3 install.py
#readlink -f install.py > /tmp/readlink.txt

# Only start server if web folder is set up
if [ -e /var/www/html/config/qaas-web.conf ]; then
  python3 start_server.py

  ov_dir=${script_dir}/../oneview
  ov_backend_dir=${ov_dir}/backend
  # cd ${ov_backend_dir}; su qaas ./run_server.sh &
  # ov_frontend_dir=${ov_dir}/frontend
  # cd ${ov_frontend_dir}; su qaas -c "npm start" &
fi

exec su qaas
# # # # start apache
# exec apachectl -D FOREGROUND
