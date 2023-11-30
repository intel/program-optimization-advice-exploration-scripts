import os
import sys

def install_backend_dependencies(backend_dir, apache_html_dir):
    try:
        print(f"Installing backend dependencies in {backend_dir}...")
        script_path = os.path.join(backend_dir, "install_pip.sh")
        if os.path.exists(script_path):
            os.system(f"cd {backend_dir} && bash install_pip.sh")
       
        target_cp_path = os.path.join(apache_html_dir, 'backend')
        create_directory(target_cp_path)
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
        create_directory(target_cp_path)

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


#update dependency+copy to apache
def update_web():
    script_dir=os.path.dirname(os.path.realpath(__file__))
    apache_dir = f"/var/www/html"
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

    # install_web_dependencies(ov_backend_dir, ov_frontend_dir, ov_apache_dir)
    # install_web_dependencies(qaas_backend_dir, qaas_frontend_dir, qaas_apache_dir)
    install_web_dependencies(common_backend_dir, common_frontend_dir, common_apache_dir)
    install_web_dependencies(lore_backend_dir, lore_frontend_dir, lore_apache_dir)

if __name__ == "__main__":
    update_web()