import os
import sys
import time
from db.db_main import DataBaseMain
from models.model_gender import ModelGender
from website.website import app
from config import ProductionConfig

try:
    start_database_development = time.time()
    value_add_db = True
    value_add_db = False
    DataBaseMain().produce_basic_values_insertion(value_add_db)
    print(f"Inserting new profiles took: {time.time() - start_database_development} seconds")
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    
    start_database_gender = time.time()
    ModelGender().produce_values_main(value_add_db)
    print(f"Inserting genders of the people took: {time.time() - start_database_gender} seconds")
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    
    app.run(host=ProductionConfig.host, port=ProductionConfig.port, debug=ProductionConfig.debug)
except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print('____________________________________')
    print(e)
    print('.......................................')