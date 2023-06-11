import speech_recognition as sr
import requests
import pyttsx3
import winsound
import openai
import pandas as pd

from pyowm.owm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps
from pyowm.utils.config import get_default_config


import json
import datetime
import random

from random import randint
from pprint import pprint

class Assistant:
    speech_recognizer = sr.Recognizer()
    speech_recognizer.pause_threshold = 0.5

    text_to_speach = pyttsx3.init()
    text_to_speach.setProperty('voice', 'ru')
    
    openai.api_key = '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'

    test_host = '26.139.60.34:8080'

    name = 'пятница'
    ex_list = ['выход', 
               'закрыть', 
               'закройся', 
               f'{name} выход', 
               f'{name} закрыть', 
               f'{name} закройся', 
               f'выход {name}', 
               f'закрыть {name}', 
               f'закройся {name}', 
               'пока', 
               f'{name} пока', 
               f'пока {name}'
               ]
    activate_list = ['запуск', 
                     'откройся', 
                     'привет', 
                     name, 
                     f'привет {name}', 
                     f'{name} привет', 
                     'здравствуй', 
                     f'{name} здравствуй', 
                     f'здравствуй {name}']

    def __init__(self, name='пятница'):
        self.name = name
        self.ex_list = ['выход', 'закрыть', 'закройся', f'{self.name} выход', f'{self.name} закрыть', f'{self.name} закройся', f'выход {self.name}', f'закрыть {self.name}', f'закройся {self.name}', 'пока', f'{self.name} пока', f'пока {self.name}']
        self.activate_list = ['запуск', 'откройся', 'привет', self.name, f'привет {self.name}', f'{self.name} привет', 'здравствуй', f'{self.name} здравствуй', f'здравствуй {self.name}']
        with sr.Microphone() as mic:
            self.speech_recognizer.adjust_for_ambient_noise(source=mic, duration=1)

    def weather(self):
        '''Получаем погоду с помощью pyowm'''
        try:
            config_dict = get_default_config()
            config_dict['language'] = 'ru'
            
            self.say('Назовите город в котором вы хотите узнать погоду')
            place = self.listen()
            self.say('Назовите страну в которой вы хотите узнать погоду')
            country = self.listen()
            country_and_place = place + ', ' + country
            
            owm = OWM('6d00d1d4e704068d70191bad2673e0cc')
            
            mgr = owm.weather_manager()
            observation = mgr.weather_at_place(country_and_place)
            weather = observation.weather
            
            status = weather.detailed_status
            weather.wind()
            humidity = weather.humidity
            temp = weather.temperature('celsius')['temp']
        except:
            self.say('Возникли ошибки при подключении к серверам погоды')
            self.activate_assist()
        self.say(f'''В городе {place} сейчас {str(status)}
Температура: {str(int(temp))} градусов
Влажность воздуха: {str(humidity)}%
Скорость ветра: {str(weather.wind()['speed'])} метров в секунду''')
        self.activate_assist()

    def activate_assist(self, signal_flag=False):
        response = self.listen(signal=signal_flag)
        if response in self.activate_list:
            self.main()
        elif response in self.ex_list:
            exit()
        else:
            self.activate_assist()
            
    def say_time_and_date(self):
        time = datetime.datetime.now().strftime("%H:%M:%S")
        date = datetime.datetime.now().strftime("%d.%m.%Y")
        self.say(f'''Сегодня: {date}
Время: {time}''')
        self.activate_assist()
    def not_recognized(self, answer, *args):
        '''Метод для ограничения пользователем команд, которые он говорит
        Пока не скажет нужную, будет осуществляться повтор прослушивания команды'''
        while answer not in args:
            self.say('Не удалось распознать команду, повторите пожалуйста.')
            answer = self.listen()
        return answer

    def say(self, message):
        print(message)
        self.text_to_speach.say(message)
        self.text_to_speach.runAndWait()

    def listen(self, signal=True):
        '''Слушаем пользователя''' 
        try:
            with sr.Microphone() as mic:
                self.speech_recognizer.adjust_for_ambient_noise(source=mic, duration=1)
                if signal:
                    winsound.PlaySound('signal.wav', winsound.SND_FILENAME)
                self.text_to_speach.runAndWait()
                audio = self.speech_recognizer.listen(source=mic)
                query = self.speech_recognizer.recognize_google(audio_data=audio, language='ru-RU').lower()
            return query
        except:
            return 'Uknown value'
    
    def repeat(self):
        '''Повторяем за пользователем его слова'''
        self.say('Это повторюшка, я буду повторять за вами всё. Если вы захотите выйти скажите выход.')
        answer = self.listen()
        while answer not in self.ex_list:
            self.say(answer)
            answer = self.listen()
        self.activate_assist()

    def find_answer(self):
        '''Ищем ответ на вопрос пользователя с помощью ChatGPT'''
        self.say('Задайте ваш вопрос.')
        model_engine = 'text-davinci-003'
        question = self.listen()
        while question == 'Uknown value':
            self.say('Ваш вопрос не удалось распознать')
            question = self.listen()
        print(question)
        try:
            completion = openai.Completion.create(engine=model_engine, 
                                              prompt=question,
                                              max_tokens=1024,
                                              temperature=0.5,
                                              top_p=1,
                                              frequency_penalty=0,
                                              presence_penalty=0)
        except:
            self.say('Возникли проблемы при подключении к серверу.')
            self.activate_assist()
        
        self.say(completion.choices[0].text)
        self.say("Вы хотите задать ещё вопрос? Да/Нет")
        answer = self.listen()
        answer = self.not_recognized(answer, *['да','нет'])
        if answer == 'да':
            self.find_answer()
        else:
            self.activate_assist()
        
    def question(self, question):
        '''Метод для задания вопроса пользователю'''
        self.say(question)
        answer = self.listen()
        return answer
    
    def exit_(self):
        self.say('До свидания:) Надеюсь вы скоро вернётесь^^')
        self.activate_assist()
    
    #def create_user(self):

    def login_user(self):
        '''Вход пользователя в наш сервер'''
        self.say('Вы желаете войти или зарегистрироваться?')
        user_data = dict()
        answer = input()
        answer = self.not_recognized(answer, *['войти', 'регистрация'])
        if answer == 'войти':
            self.say('Входим')
            self.say('Введите имя:')
            user_data['name'] = input()
            self.say('Введите фамилию:')
            user_data['secname'] = input()
            self.say('Введите группу')
            user_data['group'] = input()
            try:
                user = requests.post(f'http://{self.test_host}/login', json=user_data)
                if user.status_code == 200:
                    return user
                elif user.status_code == 401:
                    self.say(user.json()['error'])
                    self.login_user()              
            except:
                self.say('Возникли проблемы на сервере')
                self.main()
            
        else:
            self.say('Регистрируемся')
            self.say('Введите имя:')
            user_data['name'] = input()
            self.say('Введите фамилию:')
            user_data['secname'] = input()
            self.say('Введите группу')
            user_data['group'] = input()
            try:
                user = requests.post(f'http://{self.test_host}/register', json=user_data)
                if user.status_code not in (400,500):
                    return user
                elif user.status_code == 400:
                    self.say('Такой пользователь уже существует!')
                    self.login_user()
                else:
                    self.say('Извините произошла ошибка в процессе регистрации')
                    self.main()

            except Exception as e:
                self.say(f'Возникли проблемы на сервере {e}')
                #self.main()
            
        
    def get_questions(self):
        return requests.get(f'http://{self.test_host}/get_questions').json()

    

    def test_cs(self):
        user_answers = [self.login_user().json()['id']]
        questions = self.get_questions()
        for question in questions:
            answers = question['answer'].split('#@')
            random.shuffle(answers)
            self.say(question['text'])
            print('Выберите номер правильного ответа, если их несколько впишите их через запятую:')
            for i in range(len(answers)):
                print(f'{i+1}.{answers[i]}')
            ans = set(map(int, [digit for digit in input().split(',') if digit.isdigit()]))
            user_answer = list()
            for a in ans:
                if a-1 in range(len(answers)):
                    user_answer.append(answers[a-1])
            user_answers.append({f"{question['id']}" : "#@".join(user_answer)})
        if (req := requests.post(f'http://{self.test_host}/write_answers',json=user_answers)).status_code == 200:
            user_data = req.json()
            user_datadict = dict()
            for i in range(len(user_data)):
                if i == 0:
                    user_datadict['percent'] = user_data[i]
                else:
                    user_datadict[f'{i} question'] = int(list(user_data[i].values())[0])
            user_dataframe = pd.DataFrame(user_datadict, index=[0])
            with open('results.csv', 'w+', encoding='UTF-8'):
                user_dataframe.to_csv('results.csv', sep='\t', encoding='utf-8')
            self.main()
        else:
            self.say('Блокировка базы данных.')
            self.main()

    def main(self):
        
        test = ['2', 'тест', 'тест по иб', 'тест по информационной безопасности', 'иб тест', 'информационная безопасноть тест', 'иб', 'информационная безопасность']
        rep = ['1', 'повтор', 'повтор слов', 'повторюшка', 'запусти повторюшку', 'повторка', 'запусти повтор слов', 'повтори за мной']
        ans = ['3','вопрос','у меня вопрос','ответь мне','возникли сложности']
        weath = ['4', 'погода', 'какая погода', 'скажи погоду', 'погода какая', 'погоду скажи', 'прогноз погоды', 'скажи прогноз погоды', 'прогноз погоды скажи']
        time = ['5', 'время', 'сколько время', 'время сколько', 'дата', 'скажи дату', 'дату скажи', 'назови дату', 'дату назови']


        greet = ['Слушаю вас', 'Да да', 'Приветствую', 'Здравствуйте']

        self.say(greet[randint(0, len(greet)-1)])
        
        answer = self.listen()
        answer = self.not_recognized(answer, *test, *rep, *ans, *weath, *time, *self.ex_list)

        if answer in test:
            self.test_cs()
        if answer in rep:
            self.repeat()
        if answer in ans:
            self.find_answer()
        if answer in weath:
            self.weather()
        if answer in time:
            self.say_time_and_date()
        if answer in self.ex_list:
            self.exit_()


if __name__ == '__main__':
    assistant = Assistant()
    assistant.test_cs()