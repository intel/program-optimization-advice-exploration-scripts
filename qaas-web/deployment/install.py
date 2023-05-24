import os
import sys
import subprocess

script_dir=os.path.dirname(os.path.realpath(__file__))
qaas_web_dir = f'{script_dir}/repo/qaas-web'
apache_dir = f"/var/www/html"

database_url = 'mysql://qaas:qaas-password@localhost/test'



def install_packages():
    try:
        os.system("sudo apt-get update")
        #assume they already have these
        os.system("sudo apt-get install apache2")
        os.system("sudo apt-get install mariadb-server")
        os.system("sudo apt-get install python3-pip")
        os.system("pip3 install Flask")


        os.system("sudo apt-get install nodejs npm")
        os.system("sudo apt-get install git apache2 libapache2-mod-wsgi-py3")
        os.system("sudo a2enmod proxy")
        os.system("sudo a2enmod proxy_http")

        print("All packages installed successfully.")
    except Exception as e:
        print("Error installing packages:", e)
        sys.exit(1)

def get_source_code(repo_url, destination, branch, backend_dir):
    if os.path.exists(backend_dir):
        print("pull it")

        try:
            print(f"Pulling changes from branch {branch} in the existing Git repository at {backend_dir}")
            subprocess.run(f"cd {backend_dir} &&  git checkout {branch} &&   git pull", shell=True, check=True)
            print("Changes pulled successfully.")
        except subprocess.CalledProcessError as e:
            print("Error pulling changes from Git repository:", e)
            sys.exit(1)
    else:
        print("clone it")
        try:
            print(f"Cloning Git repository: {repo_url} (branch: {branch}) to {destination}")
            subprocess.run(f"  git clone --branch {branch} {repo_url} {destination}", shell=True, check=True)
            print("Git repository cloned successfully.")
        except subprocess.CalledProcessError as e:
            print("Error cloning Git repository:", e)
            sys.exit(1)

def install_backend_dependencies(backend_dir, apache_html_dir):
    try:
        print(f"Installing backend dependencies in {backend_dir}...")
        os.system(f"cd {backend_dir} && bash install_pip.sh")
        #also copy the config
        print("Backend dependencies installed successfully.")
        if os.path.exists(f"{apache_html_dir}/backend"):
            os.system(f"sudo rm -r {apache_backend_dir}/backend")

        os.system(f"sudo cp -r {backend_dir} {apache_html_dir}")
    except Exception as e:
        print("Error installing backend dependencies:", e)
        sys.exit(1)

def install_frontend_dependencies(frontend_dir, apache_html_dir):
    try:
        print(f"Installing frontend dependencies in {frontend_dir}...")
        os.system(f"cd {frontend_dir} && npm i --legacy-peer-deps")
        os.system(f"cd {frontend_dir} && npm run build")
        #check if there is already a dist
        if os.path.exists(f"{apache_html_dir}"):
            os.system(f"sudo rm -r {apache_html_dir}")

        os.system(f"sudo cp -r {frontend_dir}/dist {apache_html_dir}")
        print("Frontend dependencies installed successfully.")

        
    except Exception as e:
        print("Error installing frontend dependencies:", e)
        sys.exit(1)

def create_wsgi_file(backend_dir, apache_backend_dir):
    try:
        print("Creating WSGI file...")
        wsgi_content = f"""
import sys
sys.path.insert(0, {apache_backend_dir})

from server import create_app
import configparser
import os

script_dir=os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_dir, "../config/qaas-web.conf")
config = configparser.ConfigParser()
config.read(config_path)
application = create_app(config)

if __name__ == "__main__":
    application.run()
"""
        with open(f"{backend_dir}/server.wsgi", 'w') as f:
            f.write(wsgi_content.strip())

        # command = f"sudo cp {backend_dir}/server.wsgi {apache_backend_dir}"
        # process = subprocess.run(command, shell=True, check=True)
        
        print("WSGI file created successfully.")
 
    except Exception as e:
        print("Error creating WSGI file:", e)
        sys.exit(1)

def create_apache_config(apache_html_dir, apache_backend_dir):
    APACHE_CONFIG = f"""
<VirtualHost *:80>

	ServerAdmin webmaster@localhost
	DocumentRoot {apache_html_dir}/dist
        Alias /otter_html {apache_html_dir}/private/otter_html
        <Directory {apache_html_dir}/private/otter_html>
            Options Indexes FollowSymLinks
            AllowOverride None
            Require all granted
        </Directory>
        # Handle actual resources
        <Directory {apache_html_dir}/dist>
           Options -Indexes +FollowSymLinks
     	   AllowOverride All
    	   Require all granted
    	   FallbackResource /index.html
       </Directory>

	ErrorLog ${{APACHE_LOG_DIR}}/error.log
	CustomLog ${{APACHE_LOG_DIR}}/access.log combined

        WSGIDaemonProcess flaskapp user=www-data group=www-data threads=5 python-home={apache_backend_dir}/venv
        WSGIScriptAlias /api {apache_backend_dir}/server.wsgi

        <Directory {apache_backend_dir}>
            WSGIProcessGroup flaskapp
            WSGIApplicationGroup %{{GLOBAL}}
            Require all granted
        </Directory>
</VirtualHost>
"""
    try:
        print("Creating Apache configuration file...")
        config_content = APACHE_CONFIG
        os.system(f'echo "{config_content}" | sudo tee /etc/apache2/sites-available/000-default.conf')
        
        os.system("sudo systemctl reload apache2")
        print("Apache configuration file created successfully.")
    except Exception as e:
        print("Error creating Apache configuration file:", e)
        sys.exit(1)

def create_directory(directory):
    if not os.path.exists(directory):
        try:
            print(f"Creating directory: {directory}")
            os.makedirs(directory)
            print("Directory created successfully.")
        except Exception as e:
            print("Error creating directory:", e)
            sys.exit(1)

if __name__ == "__main__":
    git_repo_url = "git@gitlab.com:davidwong/qaas.git"
    git_branch = "ov_demo"
    destination = "repo"
    backend_dir = os.path.join(qaas_web_dir, "backend")
    frontend_dir = os.path.join(qaas_web_dir, "ov_frontend")
    apache_backend_dir = os.path.join(apache_dir, "backend")
    apache_frontend_dir = os.path.join(apache_dir, "dist")
    config_dir =  os.path.join(qaas_web_dir, "config")

    install_packages()

    # create_directory(destination)

    # get_source_code(git_repo_url, destination, git_branch, os.path.join(qaas_web_dir, "backend"))

    
    # install_backend_dependencies(backend_dir, apache_backend_dir)
    # install_frontend_dependencies(frontend_dir, apache_frontend_dir)

    # #create wsgi config
    # create_wsgi_file(backend_dir, apache_backend_dir)

    #also copy the config folder
    # os.system(f"sudo cp -r {config_dir} {apache_dir}")

    #permission for the www-data to wrtie to apache dir
 
    # create_apache_config( apache_frontend_dir, apache_backend_dir)
