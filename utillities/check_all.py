import os
from config import default_chunk

def check_storage(folder_path:str) -> bool:
    return os.path.exists(folder_path) \
        and os.path.isdir(folder_path)

def produce_storage(folder_path:str) -> None:
    return os.path.exists(folder_path) \
        or os.mkdir(folder_path)

def check_file_presence(file_path:str) -> bool:
    return os.path.exists(file_path) \
        and os.path.isfile(file_path)

def produce_chunks(value_list:list, value_length:int=default_chunk) -> list:
    def chunk(value_list:list, length:int):
        for i in range(0, len(value_list), length):
            yield value_list[i:i + length]
    return list(chunk(value_list, value_length))