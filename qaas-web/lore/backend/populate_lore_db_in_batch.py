import argparse
from sqlalchemy.orm import sessionmaker
from model_accessor import LoreMigrator
from qaas_database import QaaSDatabase
from model import create_all_tables
import time  
import pickle
from util import get_config, connect_db

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read executions.csv in batches')
    parser.add_argument('--start', type=int,  help='Starting row to read from')
    parser.add_argument('--size', type=int,  help='Number of rows to read')
    parser.add_argument('--lore_csv_dir', type=str, default='/host/home/yjiao/lore_test', help='Path to the directory containing lore CSV files')

    args = parser.parse_args()


    # Connect to the database
    config = get_config()
    engine = connect_db(config)
    Session = sessionmaker(bind=engine)
    session = Session()
    start_time = time.time()

    create_all_tables(engine)

    # Initialize LoreMigrator
    lore_csv_dir = args.lore_csv_dir
    migrator = LoreMigrator(session, lore_csv_dir)
    qaas_database = QaaSDatabase()
    qaas_database.accept(migrator)
    # Read executions in batch
    migrator.read_executions_in_batch(args.start, args.size)

    #save the orig loop map file 
    with open('orig_src_loop_map.pkl', 'wb') as f:
        pickle.dump(migrator.orig_src_loop_map, f)
    session.commit()
    session.close()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"The script took {elapsed_time} seconds to run.")

    
