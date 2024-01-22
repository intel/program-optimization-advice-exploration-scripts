import os
import sys

#global variable
apache_dir = f"/var/www/html"
script_dir = os.path.dirname(os.path.realpath(__file__))
qaas_web_dir = os.path.join(script_dir, '..',)
apps_dir = os.path.join(qaas_web_dir, "apps")
qaas_web_backend_common_dir = os.path.join(apps_dir, 'common','backend')
sys.path.append(qaas_web_backend_common_dir)

def install_backend_dependencies(backend_dir, apache_html_dir):
    try:
        print(f"Installing backend dependencies in {backend_dir}...")
        #script_path = os.path.join(backend_dir, "install_pip.sh")
        #if os.path.exists(script_path):
        #    os.system(f"cd {backend_dir} && bash install_pip.sh")
       
        target_cp_path = os.path.join(apache_html_dir, 'backend')
        #create_directory(target_cp_path)
        create_directory(apache_html_dir)

        print(backend_dir, target_cp_path)
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

        #create_directory(target_cp_path)
        create_directory(apache_html_dir)

        os.system(f"sudo rm -rf {target_cp_path}")
        os.system(f"sudo cp -r {frontend_dir}/dist {target_cp_path}") 
        
    except Exception as e:
        print("Error installing frontend dependencies:", e)
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

def install_web_dependencies(backend_dir, frontend_dir, apache_dir):
    if backend_dir:
        install_backend_dependencies(backend_dir, apache_dir)
    if frontend_dir:
        install_frontend_dependencies(frontend_dir, apache_dir)


def get_proxy_var(var_name):
    name = os.environ.get(var_name)
    if name:
        return name if name.startswith("http://") else "http://"+name
    else:
        return None

def get_proxy():
    # get environment variables for the proxy
    return get_proxy_var('http_proxy'), get_proxy_var('https_proxy')

def set_node_proxy(http_proxy, https_proxy):
    try:
        os.system(f'npm config set proxy {http_proxy}')
        os.system(f'npm config set https-proxy {https_proxy}')
        os.system(f'npm config set registry https://registry.npmjs.org/')
        print("Node.js/npm proxy configuration set successfully.")
    except Exception as e:
        print("Error setting Node.js/npm proxy configuration:", e)

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

def sync_db(alembic_ini_file):
    original_dir = os.getcwd()
    os.chdir(qaas_web_backend_common_dir)
    #make sure we have a version folder to save version
    version_dir = os.path.join(qaas_web_backend_common_dir, 'multidb','versions')
    os.system(f'mkdir -p {version_dir}')
    command = f'alembic -c {alembic_ini_file} revision --autogenerate -m "sync db"'
    status = os.system(command)

    if status == 0:
        print("New revision file created successfully.")
    else:
        print("An error occurred while creating the new revision file.")
    
    status = os.system(f'alembic -c {alembic_ini_file} upgrade head')
    if status == 0:
        print("Database updated to the latest revision successfully.")
    else:
        print("An error occurred during database synchronization.")
    os.chdir(original_dir)


#update dependency+copy to apache
def update_web(force_install=False):

    script_dir=os.path.dirname(os.path.realpath(__file__))

    # # # #also copy the config folder
    qaas_web_dir = os.path.join(script_dir, '..',)
    config_dir =  os.path.join(qaas_web_dir, "apps", "config")
    qaas_config_file =  os.path.join(config_dir, "qaas-web.conf")
    alembic_ini_file =  os.path.join(config_dir, "alembic.ini")
    apache_qaas_config_dir = os.path.join(apache_dir, 'config')
    apache_qaas_config_file = os.path.join(apache_qaas_config_dir, "qaas-web.conf")

    if os.path.exists(apache_qaas_config_file):
        if not force_install:
            return # Already installed
        # fall through proceed to installation since force_install is True

   
    os.system(f"sudo mkdir -p {apache_qaas_config_dir}")
    os.system(f"sudo cp {qaas_config_file} {apache_qaas_config_file}")
    # Copy the 000-default.conf to apache folder
    create_apache_config()

    
    http_proxy, https_proxy = get_proxy()
    set_node_proxy(http_proxy, https_proxy)
    

    qaas_web_dir = os.path.join(script_dir, '..','apps')

    ov_backend_dir = os.path.join(qaas_web_dir, 'oneview',"backend")
    ov_frontend_dir = os.path.join(qaas_web_dir,'oneview', "frontend")

    qaas_backend_dir = os.path.join(qaas_web_dir, 'qaas',"backend")
    qaas_frontend_dir = os.path.join(qaas_web_dir,'qaas', "frontend")
    
    common_backend_dir = os.path.join(qaas_web_dir,'common','backend')
    landing_frontend_dir = os.path.join(qaas_web_dir,'landing', "frontend")

    lore_backend_dir = os.path.join(qaas_web_dir, 'lore',"backend")
    lore_frontend_dir = os.path.join(qaas_web_dir,'lore', "frontend")

    ov_apache_dir = os.path.join(apache_dir,  'oneview')
    qaas_apache_dir = os.path.join(apache_dir, 'qaas')
    common_apache_dir = os.path.join(apache_dir, 'common')
    lore_apache_dir = os.path.join(apache_dir, 'lore')
    landing_apache_dir = os.path.join(apache_dir, 'landing')

    install_web_dependencies(ov_backend_dir, ov_frontend_dir, ov_apache_dir)
    install_web_dependencies(qaas_backend_dir, qaas_frontend_dir, qaas_apache_dir)
    install_web_dependencies(common_backend_dir, None, common_apache_dir)
    install_web_dependencies(lore_backend_dir, lore_frontend_dir, lore_apache_dir)
    install_web_dependencies(None, landing_frontend_dir, landing_apache_dir)

    output_dir = os.path.join(apache_dir, 'private')
    give_permission(output_dir, 'www-data')
    give_permission(apache_dir, 'www-data')
    give_permission('/etc/apache2/auth', 'www-data')

    #sync db last
    sync_db(alembic_ini_file)

def give_permission(folder, user):
    os.system(f"sudo chown -R {user}:{user} {folder}")
    os.system(f"sudo chmod -R 755 {folder}")
    os.system(f"sudo chmod -R g+w {folder}")

    output_dir = os.path.join(apache_dir, 'private')
    give_permission(output_dir, 'www-data')
    give_permission(apache_dir, 'www-data')
    give_permission('/etc/apache2/auth', 'www-data')

def give_permission(folder, user):
    os.system(f"sudo chown -R {user}:{user} {folder}")
    os.system(f"sudo chmod -R 755 {folder}")
    os.system(f"sudo chmod -R g+w {folder}")

if __name__ == "__main__":
    
    update_web(force_install=True)
