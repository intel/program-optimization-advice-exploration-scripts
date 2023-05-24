import os
import sys
import subprocess
def start_services():
    try:
        print("Starting Apache services...")
        os.system("sudo systemctl restart apache2")
        # os.system("sudo systemctl start mariadb")
        print("Services started successfully.")
    except Exception as e:
        print("Error starting services:", e)
        sys.exit(1)

if __name__ == "__main__":
    start_services()