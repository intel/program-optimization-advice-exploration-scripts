import os
import sys
import subprocess

from urllib.parse import urlparse




def install_packages():
    try:
        os.system("sudo apt-get update")
        #assume they already have these
        os.system("sudo apt-get install -y apache2")
        os.system("sudo apt-get install -y mariadb-server")
        os.system("sudo apt-get install -y python3-pip")
        os.system("sudo apt-get install -y libmysqlclient-dev")
        os.system("sudo apt-get install -y libmariadbclient-dev")
        os.system('sudo apt-get install curl')
        os.system("curl -fsSL https://deb.nodesource.com/setup_14.x | sudo -E bash -")

        os.system("sudo apt-get install -y nodejs")
        os.system("sudo apt-get install -y git libapache2-mod-wsgi-py3")
        os.system("sudo apt-get install -y python3.8-venv")
        os.system("sudo a2enmod proxy")
        os.system("sudo a2enmod proxy_http")
        

        print("All packages installed successfully.")
    except Exception as e:
        print("Error installing packages:", e)
        sys.exit(1)
def set_node_proxy(proxyserver, port):
    try:
        os.system(f'npm config set proxy http://{proxyserver}:{port}')
        os.system(f'npm config set https-proxy http://{proxyserver}:{port}')
        print("Node.js/npm proxy configuration set successfully.")
    except Exception as e:
        print("Error setting Node.js/npm proxy configuration:", e)
def set_proxy(proxy_server, proxy_port):
    # Set environment variables for the proxy
    os.environ['http_proxy'] = f'http://{proxy_server}:{proxy_port}'
    os.environ['https_proxy'] = f'http://{proxy_server}:{proxy_port}'

# def set_git_proxy(proxyserver, port):
#     try:
#         os.system(f'git config --global http.proxy http://{proxyserver}:{port}')
#         os.system(f'git config --global https.proxy http://{proxyserver}:{port}')
#         print("Git proxy configuration set successfully.")
#     except Exception as e:
#         print("Error setting Git proxy configuration:", e)

# def get_source_code(repo_url, destination, branch):
#     set_git_proxy('proxy-chain.intel.com', 911)
#     if os.path.exists(destination):
#         print("pull it")

#         try:
#             print(f"Pulling changes from branch {branch} in the existing Git repository at {destination}")
#             subprocess.run(f"cd {destination} &&  git checkout {branch} && git pull {repo_url}", shell=True, check=True)
#             print("Changes pulled successfully.")
#         except subprocess.CalledProcessError as e:
#             print("Error pulling changes from Git repository:", e)
#             sys.exit(1)
#     else:
#         print("clone it")
#         create_directory(destination)
#         try:
#             print(f"Cloning Git repository: {repo_url} (branch: {branch}) to {destination}")
#             subprocess.run(f"  git clone --branch {branch} {repo_url} {destination}", shell=True, check=True)
#             print("Git repository cloned successfully.")
#         except subprocess.CalledProcessError as e:
#             print("Error cloning Git repository:", e)
#             sys.exit(1)

def install_backend_dependencies(backend_dir, apache_html_dir):
    try:
        print(f"Installing backend dependencies in {backend_dir}...")
        os.system(f"cd {backend_dir} && bash install_pip.sh")
        #also copy the config
        print("Backend dependencies installed successfully.")
       
        os.system(f"sudo rm -rf {apache_html_dir}/backend")
        os.system(f"sudo cp -r {backend_dir} {apache_html_dir}/")
      
    except Exception as e:
        print("Error installing backend dependencies:", e)
        sys.exit(1)

def install_frontend_dependencies(frontend_dir, apache_html_dir):
    try:
        print(f"Installing frontend dependencies in {frontend_dir}...")
        os.system(f"cd {frontend_dir} && npm i --legacy-peer-deps")
        os.system(f"cd {frontend_dir} && npm run build")
      
        os.system(f"sudo rm -rf {apache_html_dir}/dist")
        os.system(f"sudo cp -r {frontend_dir}/dist {apache_html_dir}/") 
        print("Frontend dependencies installed successfully.")

        
    except Exception as e:
        print("Error installing frontend dependencies:", e)
        sys.exit(1)


def create_apache_config(apache_frontend_dir, apache_backend_dir, apache_dir):
    otter_dir = os.path.join(apache_dir, 'private', 'otter_html')
    APACHE_CONFIG = f"""
<VirtualHost *:80>
        ServerAdmin webmaster@localhost
        DocumentRoot {apache_frontend_dir}
        Alias /otter_html {otter_dir}
        <Directory {otter_dir}>
            Options Indexes FollowSymLinks
            AllowOverride None
            Require all granted
        </Directory>
        # Handle actual resources
        <Directory {apache_frontend_dir}>
           Options -Indexes +FollowSymLinks
           AllowOverride All
           Require all granted
           FallbackResource /index.html
       </Directory>

           ErrorLog /var/log/apache2/error.log
       CustomLog /var/log/apache2/access.log combined

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
        
        # os.system("sudo systemctl reload apache2")
        print("Apache configuration file created successfully.")
    except Exception as e:
        print("Error creating Apache configuration file:", e)
        sys.exit(1)

def create_directory(directory):
    if not os.path.exists(directory):
        try:
            print(f"Creating directory: {directory}")
            os.system(f"sudo mkdir -p {directory}")
            print("Directory created successfully.")
        except Exception as e:
            print("Error creating directory:", e)
            sys.exit(1)


def give_permission(folder, user):
    os.system(f"sudo chown -R {user}:{user} {folder}")
    os.system(f"sudo chmod -R 755 {folder}")



def setup_database(database_url):
    try:
        print("Setting up the database...")
        os.system("sudo service mysql start")
        # Parse the database URL
        result = urlparse(database_url)
        username = result.username
        password = result.password
        database_name = result.path[1:]  # remove the leading '/'
        
        print(username, password, database_name)
        # Check if the user alread,y exists
        user_exists = subprocess.check_output(f"sudo mysql -u root -e \"SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = '{username}');\"", shell=True).decode().strip()

        # If the user doesn't exist, create it
        # if user_exists == '0':
        os.system(f"sudo mysql -u root -e \"CREATE USER '{username}'@'localhost' IDENTIFIED BY '{password}';\"")

        # Check if the database already exists
        db_exists = subprocess.check_output(f"sudo mysql -u root -e \"SHOW DATABASES LIKE '{database_name}';\"", shell=True).decode().strip()

        # If the database doesn't exist, create it
        # if not db_exists:
        os.system(f"sudo mysql -u root -e \"CREATE DATABASE {database_name};\"")
        os.system(f"sudo mysql -u root -e \"GRANT ALL PRIVILEGES ON {database_name}.* TO '{username}'@'localhost';\"")

        os.system("sudo mysql -u root -e \"FLUSH PRIVILEGES;\"")

        print("Database set up successfully.")
    except Exception as e:
        print("Error setting up database:", e)
        sys.exit(1)

def delete_index_html(apache_dir):
    index_file = os.path.join(apache_dir, 'index.html')
    if os.path.exists(index_file):
        try:
            print(f"Deleting file: {index_file}")
            subprocess.check_call(['sudo', 'rm', index_file])
            print("index.html deleted successfully.")
        except Exception as e:
            print("Error deleting index.html:", e)
            sys.exit(1)
if __name__ == "__main__":
    script_dir=os.path.dirname(os.path.realpath(__file__))
    apache_dir = f"/var/www/html"
    # set_proxy('proxy-chain.intel.com', 911)


    database_url = 'mysql://qaas:qaas-password@localhost/test'
    # git_repo_url = "git@gitlab.com:davidwong/qaas.git"
    # git_branch = "ov_deployment"
    target_qaas_dir = os.path.join(script_dir, '..',)

    # get_source_code(git_repo_url, target_qaas_dir, git_branch)

    backend_dir = os.path.join(target_qaas_dir, "backend")
    frontend_dir = os.path.join(target_qaas_dir, "frontend")
    config_dir =  os.path.join(target_qaas_dir, "config")

    apache_backend_dir = os.path.join(apache_dir, "backend")
    apache_frontend_dir = os.path.join(apache_dir, "dist")

    output_dir = os.path.join(apache_dir, 'private')
    create_directory(output_dir)
    maqao_package_dir = os.path.join(target_qaas_dir, 'maqao_package')

    install_packages()



    install_backend_dependencies(backend_dir, apache_dir)
    # set_node_proxy('proxy-chain.intel.com', 911)
    install_frontend_dependencies(frontend_dir, apache_dir)

    

    # #also copy the config folder
    os.system(f"sudo cp -r {config_dir} {apache_dir}")

    # #also copy maqao package to output folder
    os.system(f"sudo cp -r {os.path.join(maqao_package_dir, 'lib')} {os.path.join(maqao_package_dir, 'bin')} {output_dir}")
 

    # #set the environment path
    os.environ["PATH"] = f"{os.path.join(output_dir, 'bin')}" + os.pathsep + os.environ["PATH"]
    os.environ["LD_LIBRARY_PATH"] = f"{os.path.join(output_dir, 'lib')}"


    # #permission for the www-data to wrtie to apache dir
 
    create_apache_config( apache_frontend_dir, apache_backend_dir, apache_dir)

    # #give permissions
    os.system(f"sudo a2enmod wsgi")
    os.system(f"sudo a2enmod rewrite")
    give_permission(output_dir, 'www-data')

    #setup database
    setup_database(database_url)

    #delete default index html
    delete_index_html(apache_dir)