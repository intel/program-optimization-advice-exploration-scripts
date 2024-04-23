import os
import sys
import subprocess
import configparser
import getpass
from pathlib import Path

from urllib.parse import urlparse

from update_web import update_web, create_directory

script_dir=os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(script_dir, '../apps/common/backend/')))
from base_util import send_ssh_key_to_backplane 
from model import create_all_tables
qaas_web_dir = os.path.join(script_dir, '..',)
apps_dir = os.path.join(qaas_web_dir, "apps")
qaas_web_backend_common_dir = os.path.join(apps_dir, 'common','backend')
sys.path.append(qaas_web_backend_common_dir)

def setup_backplane_machine_connections():
    machine_names = []
    while True:
        print("")
        machine_name = input("Please provide machine name for backplane runs [Enter for done]: ")
        if not machine_name:
            return ",".join(machine_names)
        mypass = getpass.getpass(prompt=f"Enter password for {machine_name}: ")
        rc = send_ssh_key_to_backplane(machine_name, mypass)
        if rc != 0:
            print ("Incorrect password, try again.")
            continue
        machine_names += [machine_name]


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


def get_current_database_version(alembic_ini_file):
    """check current db version."""
    result = subprocess.run(['alembic', '-c', alembic_ini_file, 'current'], capture_output=True, text=True)
    if 'head' in result.stdout: return 'head'
    #for case 4 
    if "FAILED: Can't locate revision identified by" in result.stderr: return None
    lines = result.stdout.splitlines()
    # extract the current version from the output, first if multiple
    if len(lines) > 0: return lines[0]
    return None

def upgrade_database_if_necessary(alembic_ini_file):
    #case 1: database has no version-> start with one that has down version = None and upgrade to head
    #case 2: database has version, but not newest -> start with the one that has current version and upgrade to head
    #case 3: database has version and it is newest -> return
    #case 4: database has version that is not in the current version folder -> return

    original_dir = os.getcwd()
    os.chdir(qaas_web_backend_common_dir)
    version_dir = os.path.join(qaas_web_backend_common_dir, 'multidb','versions')
    os.system(f'mkdir -p {version_dir}')
    
    #case 3  database has version and it is newest just return
    current_version = get_current_database_version(alembic_ini_file)
    if current_version == 'head': 
        print('Current version is newest version.')
        return

    # print("current_version",current_version)
    #case 4  database has version that is not in the current version folder just return
    available_migrations = [f.stem.split('_')[0] for f in Path(version_dir).glob('*.py')]
    if current_version and current_version not in available_migrations:
        print('Database has a version that does not exist in current versions, please get correct versions.')
        return
    #update until head
    try:
        # upgrade database to the latest version case 1 and case 2
        subprocess.run(['alembic', '-c', alembic_ini_file, 'upgrade', 'head'], check=True, capture_output=True, text=True)
        print("Database upgraded to the latest version successfully.")
    except subprocess.CalledProcessError as e:
        print("Error occurred during database upgrade:", e.stderr)
    finally:
        #go to original directory
        os.chdir(original_dir)


def setup_database(database_url, config):
    try:
        # Parse the database URL
        result = urlparse(database_url)
        username = result.username
        password = result.password
        database_name = result.path[1:]  # remove the leading '/'
        
        # check if the user alread,y exists
        # Use this version for SDP because flagging for shell=True
        user_exists = subprocess.check_output(["mysql", "-u", "root", "-e", f"SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = '{username}');"]).decode().strip()
        # This is original implementation
        #user_exists = subprocess.check_output(f"sudo mysql -u root -e \"SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = '{username}');\"", shell=True).decode().strip()
        user_exists_lines = user_exists.split('\n')
        # Drop the query and result is second line
        user_exist_result = user_exists_lines[1]

        #  user doesn't exist, create it
        if user_exist_result == '0':
            #print(f'Creating user "{username}"...')
            print(f'Creating user ...')
            os.system(f"mysql -u root -e \"CREATE USER '{username}'@'localhost' IDENTIFIED BY '{password}';\"")
        else:
            #print(f'User "{username}" already exists, skipping creation of {username} user.')
            print(f'User already exists, skipping creation of user.')

            # compare current password with the provided one, and update if different
            login_success = os.system(f"mysql -u '{username}' --password='{password}' -e ';'")
            if login_success != 0:
                #print(f'Updating password for user "{username}"...')
                print(f'Updating password for user ...')
                os.system(f"mysql -u root -e \"ALTER USER '{username}'@'localhost' IDENTIFIED BY '{password}';\"")

        # check if the database already exists
        #db_exists = subprocess.check_output(f"sudo mysql -u root -e \"SHOW DATABASES LIKE '{database_name}_';\"", shell=True).decode().strip()
        # Use this version for SDP because flagging for shell=True
        db_exists = subprocess.check_output(["mysql", "-u", "root", "-e",  f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME='{database_name}';"]).decode().strip()
        # This is original implementation
        # db_exists = subprocess.check_output(f"sudo mysql -u root -e \"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME='{database_name}';\"", shell=True).decode().strip()

        # if the database doesn't exist, create it
        if not db_exists:
            #print(f'Creating database "{database_name}"...')
            print(f'Creating database ...')
            os.system(f"mysql -u root -e \"CREATE DATABASE {database_name};\"")
            os.system(f"mysql -u root -e \"GRANT ALL PRIVILEGES ON {database_name}.* TO '{username}'@'localhost';\"")
            os.system("mysql -u root -e \"FLUSH PRIVILEGES;\"")
            create_all_tables(database_url)

        else:
            #print(f'Database "{database_name}" already exists, skipping creation of "{database_name}" database.')
            print(f'Database already exists, skipping creation of database.')
        

        #print(f'Database "{database_name}" set up successfully.')
        print(f'Database set up successfully.')
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

def generate_alembic_ini_from_template(db_connection_string, template_path, output_path):
    """
    Generates an new alembic.ini file for a specific database from a template.
    """
    with open(template_path, 'r') as file:
        template_content = file.read()
    
    ini_content = template_content.replace('$db_url', db_connection_string)
    
    # write new ini file
    with open(output_path, 'w') as file:
        file.write(ini_content)


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
    alembic_ini_file =  os.path.join(config_dir, "alembic.ini")
    alembic_ini_file_template =  os.path.join(config_dir, "alembic.ini.template")

    db_connection_strings = set()
    # db_name_connection_strings_pair = {}
    for var, val in config.items("web"):
        if var.upper().startswith("SQLALCHEMY_DATABASE_URI"):
            print(f'Will setup database for: {var.upper()}')
            db_connection_strings.add(val)

    print("Setting up the database...")
    os.system("service mysql start")
 
    for db_connection_string in db_connection_strings: 
        # print(f'Setting up database for connection string: {db_connection_string}')
        setup_database(db_connection_string, config)
        #create a new ini file for each connection string
        generate_alembic_ini_from_template( db_connection_string, alembic_ini_file_template, alembic_ini_file)
        #alembic updates if necessary
        upgrade_database_if_necessary(alembic_ini_file)

    #database_url = config['web']['SQLALCHEMY_DATABASE_URI_ONEVIEW']
    # update conf file just before update_web()
    # config['web']['BACKPLANE_SERVER_LIST'] = setup_backplane_machine_connections()
    # with open(config_path, 'w') as ff:
    #     config.write(ff)

    # update_web(force_install=True)

    
    # # #delete default index html
    #delete_index_html(apache_dir)
