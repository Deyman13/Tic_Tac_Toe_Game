import os
import json


STATISTICS_EMPTY = {'win': 0, 'lost': 0, 'lastgame': None}

def load_static(file_name = 'statistics.json'):
    """Функция загрузки информации о статистике пользователя

    - Возвращает статистику побед, поражений и последней игры пользователя, если он не новый 
    - Возвращает пустой словарь, в случае, если пользователь еще не играл"""

    if os.path.exists(file_name):
            with open(file_name, "r", ) as r:
                data = json.load(r)
                print(data)
                return data
    else:
        return {}

def save_static(data: dict, file_name= 'statistics.json'):
    """Функция сохраняет прогресс пользователя по победам, поражениям и последней игры
    
    - Принимает словарь со значениями побед, поражений и последней игры
    - Записывает в файл statistics.json изменения"""
    
    with open(file_name, "w") as s:
        json.dump(data, s)