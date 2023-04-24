import os
import datetime
import socket
import webbrowser
import speech_recognition as sr
import pyttsx3 as tts
import random
import pickle
import numpy as np
import json
import nltk
import wikipedia
from nltk.stem import WordNetLemmatizer
from keras.models import load_model
from pyjokes import pyjokes

lamm = WordNetLemmatizer()
intents = json.loads(open("intents.json").read())


engine = tts.init()
voices = engine.getProperty('voices')
rate = engine.getProperty('rate')
engine.setProperty('rate', rate - 30)


words = pickle.load(open("words.pkl",'rb'))
classes = pickle.load(open("classes.pkl",'rb'))
model = load_model('model.h5')

def speak(txt):
    engine.say(txt)
    engine.runAndWait()

def wishme():
    hour = int(datetime.datetime.now().hour)
    ch = datetime.datetime.now().strftime('%d %m')
    N = datetime.datetime.now().strftime("%d %m")
    if 0 <= hour < 12:
        speak('good morning sir')
    elif 12 <= hour < 16:
        speak('good afternoon sir')
    elif ch == '25 12':
        speak("happy  christmas  sir")
    elif N == '01 01':
        speak("happy  NewYear  sir")
    else:
        speak('good evening sir')

def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('Listening....')
        r.pause_threshold = 0.5
        Audio = r.listen(source)
        try:
            print('recognizing...')
            Query = r.recognize_google(Audio, language='en')
            print(f"user said: {Query}\n")

        except sr.UnknownValueError:
            p = ["i am  sorry", "come  again", "say  that  again", "sorry!!"]
            speak(random.choice(p))
            return "none"
        except sr.RequestError:
            speak("sorry,  my  speech  services  are  down")
        return Query



def clean_up(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lamm.lemmatize(word) for word in sentence_words]
    return sentence_words

def bagow(sentence):
    sentence_words = clean_up(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)


def predict(sentence):
    bow = bagow(sentence)
    res = model.predict(np.array([bow]))[0]
    er_thr = 0.25
    result = [[i,r] for i,r in enumerate(res) if r > er_thr]
    result.sort(key= lambda x: x[1], reverse=True)
    return_list = []
    for r in result:
        return_list.append({'intents': classes[r[0]],'probability':str(r[1])})
    return return_list

def response(intents_list,all_intents):
    tag = intents_list[0]['intents']
    all_intents_list = all_intents['intents']
    for i in all_intents_list:
        if i['tag'] == tag:
            result = i['responses']
            break
    return result


if __name__ == '__main__':
    speak("initializing enum......")
    wishme()
    while True:
        query = takecommand().lower()
        if 'joke' in query:
            speak(pyjokes.get_joke('en'))
        elif 'youtube' in query:
            webbrowser.open("youtube.com")
        elif 'skype' in query:
            os.system("skype")

        elif 'search' in query:
            url = f"https://google.com/search?q={query.replace('search','')}"
            webbrowser.open(url)
        elif 'bye' in query:
            speak("see you soon! bye....!!")
            exit()
        else:
            try:
                ints = predict(query)
                resp = response(ints,intents)
            except:
                continue
            if len(resp)>2:
                speak([random.choice(resp)])
            else:
                if resp[0]=="wiki":
                    try:
                        speak(f'according to wikipedia......{wikipedia.summary(query.replace("tell me about",""),sentences=2)}')
                    except:
                        speak("i am sorry , no results found...!!!")
                elif resp[0] == "ip":
                    print(socket.gethostbyname(socket.gethostname()))
                    speak(socket.gethostbyname(socket.gethostname()))

                else:
                    try:
                        speak(resp[1])
                        os.system(f'start {resp[0]}')
                    except:
                        speak("opening...")
                        os.system(f"start {resp[0]}")
