import os
from attr import dataclass
from dotenv import load_dotenv


load_dotenv()

link_webdriver = os.getenv("LINK_WEBDRIVER")
link_model_gender = os.getenv("LINK_MODEL_GENDER")

default_chunk = 10
user_numbers = 1000000

@dataclass
class Db:
    sqlite_name = 'sqlite.db'
    echo = False

@dataclass
class ProductionConfig(object):
    host = '0.0.0.0'
    port = 5001
    debug = True
    # SECRET_KEY = ''

@dataclass
class Models:
    folder_models = 'models'
    face_proto = 'opencv_face_detector.pbtxt'
    face_model = 'opencv_face_detector_uint8.pb'
    gender_proto = 'gender_deploy.prototxt'
    gender_model = 'gender_net.caffemodel'
    gender_name_archive = 'gad.zip'
    
@dataclass
class Folders:
    folder_main = os.getcwd()
    folder_storage = 'storage'

@dataclass
class Imdb:
    link = 'https://www.imdb.com'
    link_name = 'name'
    semaphore = 10
    link_name_add = 'nm'
    
@dataclass
class DataFrames:
    df_name = 'names_imdb.csv'
    df_name_proffesions = 'professions.csv'
    df_name_astro = 'astro.csv'

dictionary_gender = {
    'Male': 1,
    'Female': 2,
    'Unknown': 3,
}

dictionary_astro = [
    {
        'name': 'Astro1',
        'begin': '1',
        'end': '2',
    },
    {
        'name': 'Astro2',
        'begin': '1',
        'end': '2',
    }
]

# config = {
#     'dev': Website,
# }