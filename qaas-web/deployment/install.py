import os
import sys
import subprocess

from urllib.parse import urlparse



script_dir=os.path.dirname(os.path.realpath(__file__))

def install_packages():
    try:
        http_proxy, https_proxy = get_proxy()
        set_apt_proxy(http_proxy, https_proxy)
        os.system("sudo apt-get update")
        #assume they already have these
        os.system("sudo apt-get install -y apache2")
        os.system("sudo apt-get install -y mariadb-server")
        os.system("sudo apt-get install -y python3-pip")
        os.system("sudo apt-get install -y libmysqlclient-dev")
        os.system("sudo apt-get install -y libmariadbclient-dev")
        os.system("sudo apt-get install -y python3-certbot-apache")
        os.system('sudo apt-get install -y curl')
        os.system("curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -")

        os.system("sudo apt-get install -y nodejs")
        os.system("sudo apt-get install -y git libapache2-mod-wsgi-py3")
        os.system("sudo a2enmod proxy")
        os.system("sudo a2enmod proxy_http")
        

        print("All packages installed successfully.")
    except Exception as e:
        print("Error installing packages:", e)
        sys.exit(1)

def set_apt_proxy(http_proxy, https_proxy):
    try:
        os.system(f'echo \'Acquire::http::Proxy "{http_proxy}";\' | sudo tee -a /etc/apt/apt.conf')
        os.system(f'echo \'Acquire::https::Proxy "{https_proxy}";\' | sudo tee -a /etc/apt/apt.conf')
        
        print("APT proxy configuration set successfully.")
    except Exception as e:
        print("Error setting APT proxy configuration:", e)

def set_node_proxy(http_proxy, https_proxy):
    try:
        os.system(f'npm config set proxy {http_proxy}')
        os.system(f'npm config set https-proxy {https_proxy}')
        os.system(f'npm config set registry https://registry.npmjs.org/')
        print("Node.js/npm proxy configuration set successfully.")
    except Exception as e:
        print("Error setting Node.js/npm proxy configuration:", e)
def set_proxy(proxy_server, proxy_port):
    # Set environment variables for the proxy
    os.environ['http_proxy'] = f'http://{proxy_server}:{proxy_port}'
    os.environ['https_proxy'] = f'http://{proxy_server}:{proxy_port}'

def get_proxy():
    # Get environment variables for the proxy
    return os.environ.get('http_proxy'), os.environ.get('https_proxy')

def install_common_dependencies(apache_common_dir):
    os.system(f"sudo rm -rf {apache_common_dir}")
    apache_parent_dir = os.path.dirname(apache_common_dir)
    os.system(f"sudo cp -r {script_dir}/../common {apache_parent_dir}/") 

def install_backend_dependencies(backend_dir, apache_html_dir):
    try:
        print(f"Installing backend dependencies in {backend_dir}...")
        os.system(f"cd {backend_dir} && bash install_pip.sh")
        #also copy the config
        print("Backend dependencies installed successfully.")
       
        target_cp_path = os.path.join(apache_html_dir, 'backend')
        create_directory(target_cp_path)

        os.system(f"sudo rm -rf {target_cp_path}")
        os.system(f"sudo cp -r {backend_dir} {target_cp_path}")
      
    except Exception as e:
        print("Error installing backend dependencies:", e)
        sys.exit(1)

def install_frontend_dependencies(frontend_dir, apache_html_dir):
    try:
        print(f"Installing frontend dependencies in {frontend_dir}...")
        os.system(f"cd {frontend_dir} && npm i --legacy-peer-deps")
        os.system(f"cd {frontend_dir} && npm run build")
      
        target_cp_path = os.path.join(apache_html_dir, 'dist')
        create_directory(target_cp_path)

        os.system(f"sudo rm -rf {target_cp_path}")
        os.system(f"sudo cp -r {frontend_dir}/dist {target_cp_path}") 



        print("Frontend dependencies installed successfully.")

        
    except Exception as e:
        print("Error installing frontend dependencies:", e)
        sys.exit(1)


def create_apache_config():
    try:
        with open('000-default.conf', 'r') as file:
            config_content = file.read()
            os.system(f'echo "{config_content}" | sudo tee /etc/apache2/sites-available/000-default.conf')
            os.system("sudo a2ensite 000-default.conf")

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

def install_web_dependencies(backend_dir, frontend_dir, apache_dir):
    install_backend_dependencies(backend_dir, apache_dir)
    install_frontend_dependencies(frontend_dir, apache_dir)



if __name__ == "__main__":
    apache_dir = f"/var/www/html"
   
    target_qaas_dir = os.path.join(script_dir, '..',)
    config_dir =  os.path.join(target_qaas_dir, "config")

    ov_backend_dir = os.path.join(target_qaas_dir, 'oneview',"backend")
    ov_frontend_dir = os.path.join(target_qaas_dir,'oneview', "frontend")
    qaas_backend_dir = os.path.join(target_qaas_dir, 'qaas',"backend")
    qaas_frontend_dir = os.path.join(target_qaas_dir,'qaas', "frontend")
    common_frontend_dir = os.path.join(target_qaas_dir,'common','landing')

    ov_apache_dir = os.path.join(apache_dir, 'merge', 'oneview')
    qaas_apache_dir = os.path.join(apache_dir, 'merge', 'qaas')
    common_apache_dir = os.path.join(apache_dir, 'common','landing')

    output_dir = os.path.join(apache_dir, 'private')
    create_directory(output_dir)
    maqao_package_dir = os.path.join(target_qaas_dir, 'maqao_package')

    # install_packages()

    # http_proxy, https_proxy = get_proxy()
    # set_node_proxy(http_proxy, https_proxy)


    # install_web_dependencies(ov_backend_dir, ov_frontend_dir, ov_apache_dir)
    install_web_dependencies(qaas_backend_dir, qaas_frontend_dir, qaas_apache_dir)
    # install_frontend_dependencies(common_frontend_dir, common_apache_dir)

    # # # # # #also copy the config folder
    # os.system(f"sudo cp -r {config_dir} {apache_dir}")

    # # # # # #also copy maqao package to output folder
    # os.system(f"sudo cp -r {os.path.join(maqao_package_dir, 'lib')} {os.path.join(maqao_package_dir, 'bin')} {output_dir}")
 

    # # # # # #set the environment path
    # os.environ["PATH"] = f"{os.path.join(output_dir, 'bin')}" + os.pathsep + os.environ["PATH"]
    # os.environ["LD_LIBRARY_PATH"] = f"{os.path.join(output_dir, 'lib')}"


    # # # # # #permission for the www-data to wrtie to apache dir
 
    # create_apache_config()

    # # # # #give permissions
    # os.system(f"sudo a2enmod wsgi")
    # os.system(f"sudo a2enmod rewrite")
    # give_permission(output_dir, 'www-data')
    # give_permission(apache_dir, 'www-data')
    # give_permission('/etc/apache2/auth', 'www-data')

    # # # #setup database
    # database_url = 'mysql://qaas:qaas-password@localhost/test'

    # setup_database(database_url)

    # # # #delete default index html
    # delete_index_html(apache_dir)
