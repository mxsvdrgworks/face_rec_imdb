import os
import gdown
import zipfile
from config import (Models, 
                    Folders,
                    link_model_gender)


class ModelDownloader:
    """
    class which is dedicated to produce the models 
    to the storages in cases of self download of them
    """
    def __init__(self) -> None:
        self.check_folder = lambda x: os.path.exists(x) or os.mkdir(x)
        self.location_folder = os.path.join(Folders.folder_main, 
                Folders.folder_storage, Models.folder_models)
        self.location_zip = os.path.join(Folders.folder_main, 
                Folders.folder_storage, Models.gender_name_archive)
        
    def extract_values_models(self, value_check:bool=False) -> None:
        """
        Method which is dedicated to extract values of the 
        Input:  value_check = checked value created
        Output: we outputed from the archive values
        """
        if value_check:
            return
        with zipfile.ZipFile(self.location_zip, 'r') as zip_return:
            for zip_name in zip_return.namelist():
                zip_get = os.path.join(self.location_folder, zip_name)
                if zip_name in [Models.gender_model, Models.gender_proto, 
                        Models.face_model, Models.face_proto] and not os.path.exists(zip_get):
                    zip_return.extract(zip_name, self.location_folder)
                
    def get_value_archive(self, value_check:bool=False) -> None:
        """
        Method which is dedicated to return value of the archives
        Input:  value_check = checked values of the created values
        Output: we developed archive with the link
        """
        if not os.path.exists(self.location_zip):
            value_check = False
        if not value_check:
            gdown.download(link_model_gender, self.location_zip)
        
    def download_gender_detection_models(self) -> None:
        """
        Method which is dedicated to develop values of the downloading model of it
        Input:  all presented values
        Output: we developed values of it
        """
        value_check = os.path.exists(self.location_folder)
        self.check_folder(self.location_folder)
        self.get_value_archive(value_check)
        if value_check:
            value_check = all([os.path.exists(os.path.join(self.location_folder, f)) for f in 
                [Models.gender_model, Models.gender_proto, Models.face_model, Models.face_proto]])
        self.extract_values_models(value_check)
        return  [os.path.join(self.location_folder, f) for f in 
                [Models.gender_model, Models.gender_proto, Models.face_model, Models.face_proto]]