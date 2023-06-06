import os
import sys

def stop_services():
    try:
        print("Stopping Apache  services...")
        os.system("sudo service apache2 stop")
        # os.system("sudo systemctl stop mariadb")

        print("Services stopped successfully.")
    except Exception as e:
        print("Error stopping services:", e)
        sys.exit(1)

if __name__ == "__main__":
    stop_services()