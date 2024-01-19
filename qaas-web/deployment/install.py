import os
import sys
import subprocess
import configparser

from urllib.parse import urlparse

from update_web import update_web, create_directory

script_dir=os.path.dirname(os.path.realpath(__file__))

# def install_packages():
#     try:
#         http_proxy, https_proxy = get_proxy()
#         set_apt_proxy(http_proxy, https_proxy)
#         #os.system("sudo apt-get update")
#         #assume they already have these
#         #os.system("sudo apt-get install -y apache2")
#         #os.system("sudo apt-get install -y mariadb-server")
#         #os.system("sudo apt-get install -y python3-pip")
#         #os.system("sudo apt-get install -y libmysqlclient-dev")
#         #os.system("sudo apt-get install -y libmariadbclient-dev")
#         #os.system("sudo apt-get install -y python3-certbot-apache")
#         #os.system('sudo apt-get install -y curl')
#         #os.system("curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -")

#         #os.system("sudo apt-get install -y nodejs")
#         #os.system("sudo apt-get install -y git libapache2-mod-wsgi-py3")
#         #os.system("sudo a2enmod proxy")
#         #os.system("sudo a2enmod proxy_http")
        

#         print("All packages installed successfully.")
#     except Exception as e:
#         print("Error installing packages:", e)
#         sys.exit(1)

def set_apt_proxy(http_proxy, https_proxy):
    try:
        os.system(f'echo \'Acquire::http::Proxy "{http_proxy}";\' | sudo tee -a /etc/apt/apt.conf')
        os.system(f'echo \'Acquire::https::Proxy "{https_proxy}";\' | sudo tee -a /etc/apt/apt.conf')
        
        print("APT proxy configuration set successfully.")
    except Exception as e:
        print("Error setting APT proxy configuration:", e)

def set_proxy(proxy_server, proxy_port):
    # set environment variables for the proxy
    os.environ['http_proxy'] = f'http://{proxy_server}:{proxy_port}'
    os.environ['https_proxy'] = f'http://{proxy_server}:{proxy_port}'


def install_common_dependencies(apache_common_dir):
    os.system(f"sudo rm -rf {apache_common_dir}")
    apache_parent_dir = os.path.dirname(apache_common_dir)
    os.system(f"sudo cp -r {script_dir}/../common {apache_parent_dir}/") 




def setup_database(database_url):
    try:
        # Parse the database URL
        result = urlparse(database_url)
        username = result.username
        password = result.password
        database_name = result.path[1:]  # remove the leading '/'
        
        # check if the user alread,y exists
        user_exists = subprocess.check_output(f"sudo mysql -u root -e \"SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = '{username}');\"", shell=True).decode().strip()
        user_exists_lines = user_exists.split('\n')
        # Drop the query and result is second line
        user_exist_result = user_exists_lines[1]

        #  user doesn't exist, create it
        if user_exist_result == '0':
            print(f'Creating user "{username}"...')
            os.system(f"sudo mysql -u root -e \"CREATE USER '{username}'@'localhost' IDENTIFIED BY '{password}';\"")
        else:
            print(f'User "{username}" already exists, skipping creation of {username} user.')

        # check if the database already exists
        #db_exists = subprocess.check_output(f"sudo mysql -u root -e \"SHOW DATABASES LIKE '{database_name}_';\"", shell=True).decode().strip()
        db_exists = subprocess.check_output(f"sudo mysql -u root -e \"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME='{database_name}';\"", shell=True).decode().strip()

        # if the database doesn't exist, create it
        if not db_exists:
            print(f'Creating database "{database_name}"...')
            os.system(f"sudo mysql -u root -e \"CREATE DATABASE {database_name};\"")
            os.system(f"sudo mysql -u root -e \"GRANT ALL PRIVILEGES ON {database_name}.* TO '{username}'@'localhost';\"")
            os.system("sudo mysql -u root -e \"FLUSH PRIVILEGES;\"")
        else:
            print(f'Database "{database_name}" already exists, skipping creation of "{database_name}" database.')
        
        print(f'Database "{database_name}" set up successfully.')
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
    #apache_dir = f"/var/www/html"
   
    qaas_web_dir = os.path.join(script_dir, '..',)
    config_dir =  os.path.join(qaas_web_dir, "apps", "config")


    #output_dir = os.path.join(apache_dir, 'private')
    #create_directory(output_dir)

    #TODO hardcoded should move this to system dir
    #maqao_package_dir = f'/host/home/yjiao/package/2.17.10'

    #install_packages()




    # # # # #also copy maqao package to output folder
    #os.system(f"sudo cp -r {os.path.join(maqao_package_dir, 'lib')} {os.path.join(maqao_package_dir, 'bin')} {output_dir}")
 

    # # # # #set the environment path
    #os.environ["PATH"] = f"{os.path.join(output_dir, 'bin')}" + os.pathsep + os.environ["PATH"]
    #os.environ["LD_LIBRARY_PATH"] = f"{os.path.join(output_dir, 'lib')}"


    # # # # #permission for the www-data to wrtie to apache dir
 
    #create_apache_config()

    # # # #give permissions
    #os.system(f"sudo a2enmod wsgi")
    #os.system(f"sudo a2enmod rewrite")

    # # #setup database
    config_path = os.path.join(config_dir, "qaas-web.conf")
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read(config_path)
    db_connection_strings = set()
    for var, val in config.items("web"):
        if var.upper().startswith("SQLALCHEMY_DATABASE_URI"):
            print(f'Will setup database for: {var.upper()}')
            db_connection_strings.add(val)
    db_connection_strings = sorted(db_connection_strings)
    print("Setting up the database...")
    os.system("sudo service mysql start")
    for db_connection_string in db_connection_strings: 
        print(f'Setting up database for connection string: {db_connection_string}')
        setup_database(db_connection_string)

    #database_url = config['web']['SQLALCHEMY_DATABASE_URI_ONEVIEW']

    update_web()


    # # #delete default index html
    #delete_index_html(apache_dir)
