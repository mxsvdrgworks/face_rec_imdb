import cv2
from pprint import pprint
from multiprocessing import Pool
from db.db_main import DataBaseMain
from db.db_creator import (User,
                        Gender,
                        association_table_user_gender)
from models.model_downloader import ModelDownloader
from utillities.check_all import produce_chunks
from config import dictionary_gender


class ModelGender:
    """
    class which is dedicated to produce values of the gender to selected values
    """
    def __init__(self) -> None:
        self.database_main = DataBaseMain()
        self.gender_net, self.gender_deploy, self.face_detector_pb, \
            self.face_detector_pbtxt = ModelDownloader().download_gender_detection_models()
        self.session = self.database_main.return_session()
        self.net_face = cv2.dnn.readNet(self.face_detector_pb, self.face_detector_pbtxt)
        self.net_gender = cv2.dnn.readNet(self.gender_net, self.gender_deploy)
        self.model_mean = (78.4263377603, 87.7689143744, 114.895847746)

    def get_gender_value(self, value_manual:list, value_model:list, value_priority:bool=True) -> list:
        """
        Method which is dedicated to develop answer to get them into the database
        Input:  value_list_manual = list of the gender by manually search
                value_list_model = list of the gender by modelling of the
                value_priority = priority to use one way to another
        Output: we develop values of the image to detect it from it
        """
        value_answer = []
        for (id_manual, answer_manual), (id_model, answer_model) in zip(value_manual, value_model):
            if id_manual == id_model:
                if answer_model == 'Unknown' and answer_manual != answer_model:
                    value_answer.append([id_manual, answer_manual])
                elif answer_manual == 'Unknown' and answer_manual != answer_model:
                    value_answer.append([id_model, answer_model])
                elif answer_manual != 'Unknown' and answer_model != 'Unknown' \
                        and value_priority and answer_manual != answer_model:
                    value_answer.append([id_manual, answer_manual])
                elif answer_manual != 'Unknown' and answer_model != 'Unknown' \
                        and not value_priority and answer_manual != answer_model:
                    value_answer.append([id_model, answer_model])
                elif answer_manual == answer_model == "Unknown":
                    value_answer.append([id_model, answer_model])
                else:
                    value_answer.append([id_model, answer_model])
        return value_answer

    def produce_gender_search_manually(self, value_text:str) -> int:
        """
        Method which is dedicated to produce values from the 
        Input:  value_text = text about the user
        Output: we developed value of the id to which gender of it
        """
        value_male = ['he', 'him', 'his']
        value_female = ['she', 'her', 'hers']
        value_text = [''.join(e for e in f if e.isalnum()).lower() for f in value_text.split()]
        count_male = sum([value_text.count(f) for f in value_male])
        count_female = sum([value_text.count(f) for f in value_female])
        if count_male > count_female:
            return 'Male'
        elif count_male < count_female:
            return 'Female'
        return 'Unknown'

    def highlight_image_persons(self, net, frame, threshold = 0.7) -> list:
        """
        Method which is dedicated to produce values of the faces
        Input:  net = out network for the usage
                frame = our picture
                threshold = parameter for the making sure of it
        Output: we detected the locations of the possible faces
        """
        frameOpencvDnn = frame.copy()
        height = frameOpencvDnn.shape[0]
        width = frameOpencvDnn.shape[1]
        blob = cv2.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], True, False)
        net.setInput(blob)
        detections = net.forward()
        faceboxes = []

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > threshold:
                faceboxes.append(
                    [
                        int(detections[0, 0, i, 3] * width), 
                        int(detections[0, 0, i, 4] * height), 
                        int(detections[0, 0, i, 5] * width), 
                        int(detections[0, 0, i, 6] * height)
                    ])
        return faceboxes

    def produce_gender_search_modelling(self, index, value_image_link:str):
        """
        Method which is dedicated to develop values of the image
        Input:  index = value indexing of the development
                value_image_link = image string for the development
        Output: value of the model which was previously checked
        """
        if not value_image_link:
            return index, 'Unknown'
        video = cv2.VideoCapture(value_image_link)
        padding = 20

        while cv2.waitKey(1) < 0:
            hasFrame, frame = video.read()
            if not hasFrame:
                cv2.waitKey()
                break
            
            faceboxes = self.highlight_image_persons(self.net_face, frame)
            if not faceboxes:
                return index, 'Unknown'
            for facebox in faceboxes:
                face = frame[
                    max(0, facebox[1] - padding) : min(facebox[3] + padding, frame.shape[0] - 1),
                    max(0, facebox[0] - padding) : min(facebox[2] + padding, frame.shape[1] - 1)]
                if not face.any():
                    try:
                        blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), self.model_mean, swapRB=False)
                        self.net_gender.setInput(blob)
                        genderPreds = self.net_gender.forward()
                        gender = ['Male', 'Female'][genderPreds[0].argmax()]
                    except Exception as e:
                        # print(f'Broken; index: {index}; Error: {e}')
                        gender = 'Unknown'
                else:
                    gender = 'Unknown'
        return index, gender

    def produce_values_main(self, value_refind:bool=True) -> None:
        """
        Method which is dedicated to produce values into the datbase with produce values
        of the gender to the database
        Input:  value_refind = boolean value which signifies the work
        Output: we created values of the 
        """
        if not value_refind:
            return
        user_gender_specified = self.session.query(User.id).filter(association_table_user_gender.c.id_user== User.id).all()
        user_gender_specified = [f[0] for f in user_gender_specified]
        user_desc_images_gender_without = self.session.query(
            User.id, User.description, User.link_image).filter(~User.id.in_(user_gender_specified)).all()
        value_gender_manual = [[i, self.produce_gender_search_manually(text)] 
            if text else [i, 'Unknown'] for i, text, _ in user_desc_images_gender_without]
        value_image = [[i, link] for i, _, link in user_desc_images_gender_without]
        value_gender_manual = produce_chunks(value_gender_manual, 50)
        value_image = produce_chunks(value_image, 50)
        
        for index, images in enumerate(value_image):
            gender_models = [self.produce_gender_search_modelling(i, image) for i, image in images]
            value_gender_operated = self.get_gender_value(value_gender_manual[index], gender_models)
            value_gender_operated = [[id, dictionary_gender[name]] for id, name in value_gender_operated]
            value_gender_main = [[value, key] for key, value in dictionary_gender.items()]
            self.database_main.produce_insertion_model_gender(value_gender_main, value_gender_operated)
