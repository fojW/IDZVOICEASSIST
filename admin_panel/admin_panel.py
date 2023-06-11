import requests
import pandas as pd

import json

from datetime import datetime


test_host = '26.139.60.34:8080'

def new_questions():
    global test_host
    with open("new_questions.json", "r", encoding="UTF-8") as file:
        req = requests.post(f'http://{test_host}/new_questions',json=json.load(file))
        if req.status_code == 200:
            print('Успешно!')
        else:
            print(f'Ошибка {req.status_code}, если ошибка 500 перезапускайте базу')

def update_questions():
    global test_host
    with open("questions.json", "r", encoding="UTF-8") as file:
        req = requests.post(f'http://{test_host}/update_questions',json=json.load(file))
        if req.status_code == 200:
            print('Успешно!')
        else:
            print(f'Ошибка {req.status_code}, если ошибка 500 перезапускайте базу')

def get_statistic():
    global test_host
    if (statistic := requests.get(f'http://{test_host}/total_statistics')).status_code == 200:
        if len(statistic.json()) != 0:
            group_dct = {'Группа': [], 'Правильно(%)': []}
            stat = statistic.json()
            for elem in stat:
                for k, v in elem.items():
                    group_dct['Группа'].append(k)
                    group_dct['Правильно(%)'].append(v)
            with open(f'full_statistic_{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.csv', 'w+', encoding='UTF-8'):
                pd.DataFrame(group_dct).to_csv(f'full_statistic_{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.csv', sep='\t', encoding='utf-8')
        else:
            print('Статистику составить невозможно, база пустая')
    else:
        print(f'Ошибка {statistic.status_code}, если ошибка 500 перезапускайте базу') 

def group_statistic(group):
    global test_host
    if (statistic := requests.get(f'http://{test_host}/group_statistics?group={group}')).status_code == 200:
        if len(statistic.json()) != 0:
            group_dct = {'ФИО': [], 'Правильно(%)': []}
            stat = statistic.json()
            for elem in stat:
                group_dct['ФИО'].append(f"{elem['name']} {elem['secname']}")
                group_dct['Правильно(%)'].append(elem['right'])
            with open(f'group_statistic_{group}_{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.csv', 'w+', encoding='UTF-8'):
                pd.DataFrame(group_dct).to_csv(f'group_statistic_{group}_{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.csv', sep='\t', encoding='utf-8')
        else:
            print('Группа не найдена.')     
    else:
        print(f'Ошибка {statistic.status_code}, если ошибка 500 перезапускайте базу')
if __name__ == '__main__':
    print('''Админ-панель.
-----
Выберите номер функции которую хотите использовать:
-----
1.Новые вопросы
2.Обновить вопросы для существующего теста
3.Получение полной статистики
4.Получение статистики по группе
-----''')
    
    while (func_num := int(input())) not in [1,2,3,4]:
        func_num = int(input())
    match(func_num):
        case 1:
            new_questions()
        case 2:
            update_questions()
        case 3:
            get_statistic()
        case 4:
            group = input('Введите название группы: ')
            group_statistic(group)
