import sys

sys.path.insert(0, '/var/www/html/oneview/backend')
sys.path.insert(0, '/var/www/html/common/backend')

import configparser
import os


script_dir=os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_dir,  "..", "..","config", "qaas-web.conf")
config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read(config_path)


from server import create_app
application = create_app(config)

if __name__ == "__main__":
    application.run()