import os
import sys

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
    install_backend_dependencies(backend_dir, apache_dir)
    install_frontend_dependencies(frontend_dir, apache_dir)


def get_proxy_var(var_name):
    name = os.environ.get(var_name)
    return name if name.startswith("http://") else "http://"+name

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

#update dependency+copy to apache
def update_web(force_install=False):

    apache_dir = f"/var/www/html"
    script_dir=os.path.dirname(os.path.realpath(__file__))

    # # # #also copy the config folder
    target_qaas_dir = os.path.join(script_dir, '..',)
    config_dir =  os.path.join(target_qaas_dir, "config")

    if os.path.exists(os.path.join(apache_dir, 'config')):
        if not force_install:
            return # Already installed
        # fall through proceed to installation since force_install is True

    os.system(f"sudo cp -r {config_dir} {apache_dir}")

    
    http_proxy, https_proxy = get_proxy()
    set_node_proxy(http_proxy, https_proxy)
    

    target_qaas_dir = os.path.join(script_dir, '..',)

    ov_backend_dir = os.path.join(target_qaas_dir, 'oneview',"backend")
    ov_frontend_dir = os.path.join(target_qaas_dir,'oneview', "frontend")
    qaas_backend_dir = os.path.join(target_qaas_dir, 'qaas',"backend")
    qaas_frontend_dir = os.path.join(target_qaas_dir,'qaas', "frontend")
    common_frontend_dir = os.path.join(target_qaas_dir,'common','landing')
    common_backend_dir = os.path.join(target_qaas_dir,'common','backend')
    lore_backend_dir = os.path.join(target_qaas_dir, 'lore',"backend")
    lore_frontend_dir = os.path.join(target_qaas_dir,'lore', "frontend")

    ov_apache_dir = os.path.join(apache_dir,  'oneview')
    qaas_apache_dir = os.path.join(apache_dir, 'qaas')
    common_apache_dir = os.path.join(apache_dir, 'common')
    lore_apache_dir = os.path.join(apache_dir, 'lore')

    install_web_dependencies(ov_backend_dir, ov_frontend_dir, ov_apache_dir)
    install_web_dependencies(qaas_backend_dir, qaas_frontend_dir, qaas_apache_dir)
    install_web_dependencies(common_backend_dir, common_frontend_dir, common_apache_dir)
    install_web_dependencies(lore_backend_dir, lore_frontend_dir, lore_apache_dir)

    output_dir = os.path.join(apache_dir, 'private')
    give_permission(output_dir, 'www-data')
    give_permission(apache_dir, 'www-data')
    give_permission('/etc/apache2/auth', 'www-data')

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