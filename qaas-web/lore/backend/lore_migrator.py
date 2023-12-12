import os

from loremodel import *

from model_accessor import LoreMigrator
from qaas_database import QaaSDatabase
from util import get_config, connect_db 


# populate database given the data in qaas data folder, gui timestamp is the timestamp for both opt and orig
def migrate_database():
    lore_csv_dir = '/host/home/yjiao/lore_test'
    #connect db
    config = get_config()
    engine = connect_db(config)
    Session = sessionmaker(bind=engine)
    session = Session()

    
    #######################populate database tables######################
    initializer = LoreMigrator(session, lore_csv_dir)

    qaas_database = QaaSDatabase()
    qaas_database.accept(initializer)
  
        
    session.commit()
    session.close()



