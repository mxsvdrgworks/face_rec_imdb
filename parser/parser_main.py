import os
import time
import json
import asyncio
import pandas as pd
from pprint import pprint
from datetime import datetime
from parser.parser_imdb import ParseImdb
from utillities.check_all import (check_storage,
                                 produce_chunks,
                                 produce_storage,
                                 check_file_presence)
from config import (Folders, 
                    DataFrames,
                    user_numbers,
                    dictionary_astro)


class ParserMain:
    """
    class which is dedicated to develop values of the parser and store it as a dataframe
    """
    def __init__(self) -> None:
        self.folder_storage = os.path.join(Folders.folder_main, Folders.folder_storage)
        self.dataframe_storage = os.path.join(self.folder_storage, DataFrames.df_name)
        self.dataframe_professions = os.path.join(self.folder_storage, DataFrames.df_name_proffesions)
        self.dataframe_astro = os.path.join(self.folder_storage, DataFrames.df_name_astro)
        self.columns_professions = ['id', 'name']
        self.columns_astro = ['id', 'name', 'date_begin', 'date_end']
        self.columns = ['id', 'type', 'url', 'name', 'image', 
                        'description', 'birthdate', 'deathdate', 'jobs']
        self.columns_full = self.columns + ['jobs_indexes', 'astro_index']

    def produce_absent(self) -> list:
        """
        Method which is dedicated to produce values of the id values which were not used
        Input:  None
        Output: list with values which were previously non-created
        """
        value_repeat = pd.read_csv(self.dataframe_storage).id.values
        values_id = [i for i in range(1, user_numbers+1) if i not in value_repeat]
        return produce_chunks(values_id)

    def produce_dataframe_merging(self, value_df:pd.DataFrame) -> pd.DataFrame:
        """
        Method which is dedicated to produce values of the merge
        Input:  value_list = list of the dictionaries
        Output: we merged values to the datafrane
        """
        if not os.path.exists(self.dataframe_storage) or not os.path.isfile(self.dataframe_storage):
            value_old = pd.DataFrame([], columns=self.columns)
        else:
            value_old = pd.read_csv(self.dataframe_storage)
        value_df = pd.concat([value_old, value_df])
        value_df.drop_duplicates(subset=self.columns, keep='first', inplace=True)
        self.produce_save_df(self.dataframe_storage, value_df)

    def produce_list_transformations(self, value_list:list) -> pd.DataFrame:
        """
        Method which is dedicated to make list transformations 
        Input:  value_list = list values of the development
        Output: we created list transformation to this
        """
        value_list_old = []
        for value_dict in value_list:
            job_title = value_dict.get('jobTitle', []) if \
                isinstance(value_dict.get('jobTitle', []), list) else [value_dict.get('jobTitle', [])]
            value_list_old.append(
                [
                    value_dict.get('ID', 0),
                    value_dict.get('@type', 'Person'),
                    value_dict.get('url', ''),
                    value_dict.get('name', ''),
                    value_dict.get('image', ''),
                    value_dict.get('description', ''),
                    value_dict.get('birthDate', ''),
                    value_dict.get('deathDate', ''),
                    '|'.join(job_title)
                ]
            )
        value_df = pd.DataFrame(value_list_old, columns=self.columns)
        return value_df

    @staticmethod
    def produce_save_df(value_path:str, value_df:pd.DataFrame) -> None:
        """
        Method which is dedicated to save dataframe values
        Input:  value_path = path do dataframe where to save
                value_df = dataframe which is saved
        Output: 
        """
        value_df.to_csv(value_path, index=False)

    def produce_save_json(self, value_list:list, value_name:str='example.json') -> None:
        """
        Method which is dedicated to store values for it as a json
        Input:  value_list = list values 
                value_name = name which is required to work with
        Output: we saved value as a json
        """
        value_path = os.path.join(self.folder_storage, value_name)
        if os.path.exists(value_path):
            return
        with open(value_path, 'w') as json_wrote:
            json.dump(value_list, json_wrote, indent=4)

    def develop_dataframe_professions(self, value_list:list) -> pd.DataFrame:
        """
        Method which is dedicated to develop values of the 
        Input:  value_list = list of the values of the selected professions
        Output: dataframe of the proffesion values
        """
        value_professions = []
        for value in value_list:
            if isinstance(value, str):
                value_professions.extend(value.split('|'))
        value_professions = list(set(value_professions))
        value_professions = [(index + 1, profession) for index, 
                                profession in enumerate(value_professions)]
        return pd.DataFrame(value_professions, columns=self.columns_professions)

    def develop_dataframe_astro(self) -> pd.DataFrame:
        """
        Method which is dedicated to develop astro values
        Input:  None
        Output: we developed dataframe for the astro
        """
        value_list = [(index+1, f.get('name', ''), 
                        f.get('begin', ''), f.get('end', '')) 
                    for index, f in enumerate(dictionary_astro)]
        df_astro = pd.DataFrame(value_list, columns=self.columns_astro)
        self.produce_save_df(self.dataframe_astro, df_astro)

    def develop_values_astro(self, value_string:str, list_astro:list=[]) -> int:
        """
        Method which is dedicated to return values to the astro
        Input:  value_string = string of the birthdate
                list_astro = dataframe lists is returns 
        Output: we created values for the astro index
        """
        if not list_astro:
            list_astro = [[datetime.strptime(f.get('begin'), "%m.%d"), 
                            datetime.strptime(f.get('end'), "%m.%d")] 
                        for f in dictionary_astro]
        if isinstance(value_string, float):
            return 0
        value_date = datetime.strptime(value_string,"%Y-%m-%d")
        value_add = list_astro[0][0].year if not \
            (value_date.month==1 and value_date.day < 20) else list_astro[0][0].year + 1
        value_date = value_date.replace(day=28) if value_date.day == 29 \
            and value_date.month == 2 else value_date
        value_date = value_date.replace(year=value_add)
        for value_begin, value_end in list_astro:
            if value_begin <= value_date <= value_end:
                return list_astro.index([value_begin, value_end]) + 1
        return 0

    def produce_dataframe_filtration(self, df_value:pd.DataFrame=pd.DataFrame([])) -> pd.DataFrame:
        """
        Method which is dedicated to filtrate values of the selected dataframe
        Input:  df_value = value which is dedicated to produce values
        Output: we created values of the filtrated dataframe
        """
        if df_value.empty:
            df_value = pd.read_csv(self.dataframe_storage)
        df_value = df_value[df_value['type'] == 'Person']
        df_value_professions = self.develop_dataframe_professions(df_value['jobs'].values)
        self.produce_save_df(self.dataframe_professions, df_value_professions)
        list_indexes = []
        list_search = list(df_value_professions['name'].values)
        for values in df_value['jobs'].values:
            if isinstance(values, str):
                list_indexes.append(
                    '|'.join([str(list_search.index(f) + 1) for f in values.split('|')]))
            else:
                list_indexes.append('')
        df_value['jobs_indexes'] = list_indexes
        if not os.path.exists(self.dataframe_astro):
            self.develop_dataframe_astro()
        list_astro = [[datetime.strptime(f.get('begin'), "%m.%d"), 
                            datetime.strptime(f.get('end'), "%m.%d")] 
                        for f in dictionary_astro]
        list_astro[9][1] = list_astro[9][1].replace(year=list_astro[0][0].year +1)
        list_index_astro = []
        for value_date in df_value['birthdate'].values:
            list_index_astro.append(self.develop_values_astro(value_date, list_astro))   
        df_value['astro_index'] = list_index_astro
        self.produce_save_df(self.dataframe_storage, df_value)
        return df_value

    def produce_dataframe(self) -> pd.DataFrame:
        """
        Method which is dedicated to produce values of it
        Input:  None
        Output: we returned values of it
        """
        begin = time.time()
        if not check_storage(self.folder_storage):
            produce_storage(self.folder_storage)
        if check_storage(self.folder_storage) and not check_file_presence(self.dataframe_storage):
            values_id = [i+1 for i in range(user_numbers)]
            values_id = produce_chunks(values_id)
        else:
            values_id = self.produce_absent()
        parse_imdb = ParseImdb()
        for value_id in values_id[:]:
            loop = asyncio.get_event_loop()
            value_list = loop.run_until_complete(parse_imdb.produce_main(value_id))
            self.produce_save_json(value_list)
            [f.update({'ID': i}) for f, i in zip(value_list, value_id)]
            value_df = self.produce_list_transformations(value_list)
            self.produce_dataframe_merging(value_df)
            print(f"{value_id[0]}-{value_id[-1]} finished creating values")
            print('____________________________________________________')
        print(f"{time.time() - begin} seconds")
        print('cccccccccccccccccccccccccccccccccccccccccccccccccccccccc')