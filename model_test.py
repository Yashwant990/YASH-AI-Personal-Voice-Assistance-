import json
import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import random
import numpy as np
import speech_recognition as sr
import pyttsx3

with open("intents.json") as file:
    data = json.load(file)

model = load_model("chat_model.h5")

with open("tokenizer.pkl", "rb") as f:
    tokenizer=pickle.load(f)

with open("label_encoder.pkl", "rb") as encoder_file:
    label_encoder=pickle.load(encoder_file)
    
def speak(text):
    print(text)
    local_engine = pyttsx3.init("sapi5")
    voices = local_engine.getProperty('voices')
    local_engine.setProperty('voice', voices[1].id)
    local_engine.setProperty('rate', 150)
    local_engine.setProperty('volume', 1.0)
    local_engine.say(text)
    local_engine.runAndWait()
    local_engine.stop()

    


def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:


        r.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening...")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            command = r.recognize_google(audio, language='en-IN')
            return command
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
            return None
        except sr.RequestError:
            print("Could not request results from Google Speech Recognition service.")
            return None
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start.")
            return None

while True:
    input_text = listen()
    if input_text:
        padded_sequences = pad_sequences(tokenizer.texts_to_sequences([input_text]), maxlen=20, truncating='post')
        result = model.predict(padded_sequences)
        tag = label_encoder.inverse_transform([np.argmax(result)])

    for i in data['intents']:
        if i['tag'] == tag:
            speak(np.random.choice(i['responses']))
