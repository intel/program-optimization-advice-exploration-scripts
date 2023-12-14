import sys

sys.path.insert(0, '/var/www/html/qaas/backend')

from mockup_server import create_app
application = create_app()

if __name__ == "__main__":
    application.run()