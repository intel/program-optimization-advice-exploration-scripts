#!/bin/bash

proxy_host=$(echo $http_proxy | sed 's|http://||g' |cut -f1 -d:)
proxy_port=$(echo $http_proxy | sed 's|http://||g' |cut -f2 -d:)

mkdir -p ~/.subversion
cat <<- EOF > ~/.subversion/servers
[global]
# http-proxy-exceptions = *.exception.com, www.internal-site.org
http-proxy-host = ${proxy_host}
http-proxy-port = ${proxy_port}
# http-proxy-username = defaultusername
# http-proxy-password = defaultpassword
# http-compression = auto
# No http-timeout, so just use the builtin default.
# ssl-authority-files = /path/to/CAcert.pem;/path/to/CAcert2.pem
#
# Password / passphrase caching parameters:
# store-passwords = no
# store-ssl-client-cert-pp = no
EOF
