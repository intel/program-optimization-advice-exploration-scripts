import os
import sys
import subprocess

from urllib.parse import urlparse



script_dir=os.path.dirname(os.path.realpath(__file__))
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


    # install_web_dependencies(ov_backend_dir, ov_frontend_dir, ov_apache_dir)
    install_web_dependencies(qaas_backend_dir, qaas_frontend_dir, qaas_apache_dir)
    # install_frontend_dependencies(common_frontend_dir, common_apache_dir)