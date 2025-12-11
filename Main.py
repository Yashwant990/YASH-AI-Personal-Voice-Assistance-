import datetime
import webbrowser
import time
import pyttsx3
import speech_recognition as sr
import pyautogui
import screen_brightness_control as sbc
import os
import subprocess
import json
import pickle
import numpy as np
import random
import re

# Deep learning library imports
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# --- LLM API IMPORTS ---
# You must install the google-genai library: pip install google-genai
from google import genai
from google.genai.errors import APIError 

# --- CONFIGURATION ---
CONFIDENCE_THRESHOLD = 0.55  # Adjusted based on your low test scores (0.46, 0.37)

# --- Load Required Files ---
# NOTE: Update these paths if your files are not in the same directory as Main.py
try:
    with open("intents.json") as file: 
        data = json.load(file)
except FileNotFoundError:
    print("Error: intents.json not found. Make sure the path is correct.")
    exit()
except json.JSONDecodeError:
    print("Error: Could not decode intents.json. Check file format.")
    exit()

try:
    model = load_model("chat_model.h5")
except Exception as e:
    print(f"Error loading chat_model.h5: {e}")
    exit()

try:
    with open("tokenizer.pkl", "rb") as f:
        tokenizer = pickle.load(f)
except FileNotFoundError:
    print("Error: tokenizer.pkl not found. Make sure the path is correct.")
    exit()
except pickle.UnpicklingError:
    print("Error: Could not unpickle tokenizer.pkl. File might be corrupted.")
    exit()

try:
    with open("label_encoder.pkl", "rb") as encoder_file:
        label_encoder = pickle.load(encoder_file)
except FileNotFoundError:
    print("Error: label_encoder.pkl not found. Make sure the path is correct.")
    exit()
except pickle.UnpicklingError:
    print("Error: Could not unpickle label_encoder.pkl. File might be corrupted.")
    exit()


# --- Speak Function ---
def speak(text):
    print(f"Yash: {text}")
    try:
        engine = pyttsx3.init("sapi5")
        voices = engine.getProperty('voices')
        # Use a safe index for voices
        engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print(f"Error in speak function: {e}")


# --- Listen Function ---
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        # Increased duration for better noise adjustment
        r.adjust_for_ambient_noise(source, duration=1.0) 
        print("Listening...")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            command = r.recognize_google(audio, language='en-IN')
            
            # Print what was recognized for debugging
            print(f"You said: {command}") 
            
            return command.lower()
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return None
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during listening: {e}")
            return None


# --- Helper Functions ---

def cal_day():
    day_num = datetime.datetime.today().weekday() + 1
    days = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}
    return days.get(day_num, "Unknown Day")

def wishme():
    day = cal_day()
    hour = datetime.datetime.now().hour
    t = datetime.datetime.now().strftime("%I:%M %p")
    if hour < 12:
        speak(f"Good Morning! It's {t} on {day}, I am Yash, your personal assistant")
    elif hour < 18:
        speak(f"Good Afternoon! It's {t} on {day}, I am Yash, your personal assistant")
    else:
        speak(f"Good Evening! It's {t} on {day}, I am Yash, your personal assistant")

# --- System Control Functions (volume_control, brightness_control, openApp, closeApp) ---
# (Keeping your original, unchanged definitions for brevity, as they were correct.)

def volume_control(command):
    # ... (Your original volume_control function content) ...
    try:
        if 'increase' in command:
            for _ in range(5):
                pyautogui.press('volumeup')
            speak("Volume increased.")
        elif 'decrease' in command:
            for _ in range(5):
                pyautogui.press('volumedown')
            speak("Volume decreased.")
        elif 'mute' in command:
            pyautogui.press('volumemute')
            speak("Volume muted/unmuted.")
        else:
            speak("Please specify to increase, decrease, or mute the volume.")
    except Exception as e:
        speak(f"Could not control volume: {e}")

def brightness_control(command):
    import re
    try:
        if 'increase' in command:
            current = sbc.get_brightness()[0]
            new_value = min(100, current + 10)
            sbc.set_brightness(new_value)
            speak(f"Brightness increased to {new_value} percent.")
        elif 'decrease' in command:
            current = sbc.get_brightness()[0]
            new_value = max(0, current - 10)
            sbc.set_brightness(new_value)
            speak(f"Brightness decreased to {new_value} percent.")
        else:
            match = re.search(r'(\d{1,3})', command)
            if match:
                value = int(match.group(1))
                value = max(0, min(100, value))
                sbc.set_brightness(value)
                speak(f"Brightness set to {value} percent.")
            else:
                speak("Please specify to increase, decrease, or set a brightness value between 0 and 100.")
    except Exception as e:
        speak(f"Could not control brightness: {e}")

def openApp(command):
    app_opened = False
    if 'calculator' in command:
        speak("Opening Calculator")
        os.startfile("calc.exe")
        app_opened = True
    elif 'camera' in command:
        speak("Opening Camera")
        os.startfile("camera.exe")
        app_opened = True
    elif 'notepad' in command:
        speak("Opening Notepad")
        os.startfile("notepad.exe")
        app_opened = True
    elif 'paint' in command:
        speak("Opening Paint")
        os.startfile("mspaint.exe")
        app_opened = True
    return app_opened

def closeApp(command):
    app_closed = False
    if 'calculator' in command:
        speak("Closing Calculator")
        subprocess.run("taskkill /IM calc.exe /F", shell=True, capture_output=True)
        app_closed = True
    elif 'camera' in command:
        speak("Closing Camera")
        subprocess.run("taskkill /IM camera.exe /F", shell=True, capture_output=True)
        app_closed = True
    elif 'notepad' in command:
        speak("Closing Notepad")
        subprocess.run("taskkill /IM notepad.exe /F", shell=True, capture_output=True)
        app_closed = True
    elif 'paint' in command:
        speak("Closing Paint")
        subprocess.run("taskkill /IM mspaint.exe /F", shell=True, capture_output=True)
        app_closed = True
    elif 'chrome' in command:
        speak("Closing Chrome")
        subprocess.run("taskkill /IM chrome.exe /F", shell=True, capture_output=True)
        app_closed = True
    elif 'firefox' in command:
        speak("Closing Firefox")
        subprocess.run("taskkill /IM firefox.exe /F", shell=True, capture_output=True)
        app_closed = True
    elif 'youtube' in command:
        speak("Closing YouTube")
        subprocess.run("taskkill /IM chrome.exe /F", shell=True, capture_output=True)
        subprocess.run("taskkill /IM firefox.exe /F", shell=True, capture_output=True)
        app_closed = True
    elif 'linkedin' in command:
        speak("Closing LinkedIn")
        subprocess.run("taskkill /IM chrome.exe /F", shell=True, capture_output=True)
        subprocess.run("taskkill /IM firefox.exe /F", shell=True, capture_output=True)
        app_closed = True
    return app_closed


# --- DYNAMIC KNOWLEDGE BASE FUNCTION (GEMINI API) ---
def get_api_answer(query):
    # API_KEY is loaded from the environment variable 'GEMINI_API_KEY'
    API_KEY = os.environ.get("GEMINI_API_KEY") 
    
    if not API_KEY:
        return "I cannot answer general questions. My external knowledge base key is missing."
    
    try:
        # Initialize the client (it automatically uses the environment variable)
        client = genai.Client() 
        
        # Call the LLM for a dynamic, real-time answer
        response = client.models.generate_content(
            model='gemini-2.5-flash', # Fast and capable model
            contents=query
        )
        return response.text
        
    except APIError as e:
        print(f"API Error during search: {e}")
        return "I encountered a connection error to my external knowledge base. Please check your API key validity."
    except Exception as e:
        print(f"General LLM Error: {e}")
        return "An unexpected issue occurred while searching for that answer."


# --- Main Command Handler ---
def handle_command(command):
    command = command.lower()

    # 1. HARDCODED SYSTEM/WEB COMMANDS (Highest Priority)
    if any(x in command for x in ['exit', 'quit', 'stop', 'sign off']):
        speak("Signing off, Yash. Have a nice day.")
        exit()
        
    if 'open' in command:
        if openApp(command) or any(site in command for site in ['facebook', 'instagram', 'twitter', 'youtube', 'linkedin', 'whatsapp', 'gmail', 'google']):
            # Web browser commands check
            if 'facebook' in command:
                speak("Opening Facebook")
                webbrowser.open("https://www.facebook.com")
            elif 'youtube' in command:
                speak("Opening YouTube")
                webbrowser.open("https://www.youtube.com")
            # ... include all other web checks here or rely on the openApp return
            return
    if 'close' in command:
        if closeApp(command):
            return

    if 'brightness' in command:
        brightness_control(command)
        return
    if 'volume' in command:
        volume_control(command)
        return
    
    # Check for specific web commands not handled above (e.g., just "open google")
    if 'google' in command:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")
        return
    
    try:
        sequence = tokenizer.texts_to_sequences([command])
        padded_sequences = pad_sequences(sequence, maxlen=20, truncating='post')

        prediction = model.predict(padded_sequences, verbose=0) # Suppress progress bar
        tag_index = np.argmax(prediction)
        confidence = np.max(prediction)
        tag = label_encoder.inverse_transform([tag_index])[0]

        print(f"ML Predicted Tag: {tag} with confidence {confidence:.2f}")

        # --- FINAL LOGIC: ROUTE BASED ON CONFIDENCE & TAG ---

        # Case A: Low Confidence Fallback OR Case B: Explicit General Query Tag
        if confidence < CONFIDENCE_THRESHOLD or tag == 'general_query':
            
            # Message for low confidence (e.g., "hello" at 0.46)
            if confidence < CONFIDENCE_THRESHOLD and tag != 'general_query':
                speak(f"I'm not completely certain ({confidence:.0%}). Let me try to find an answer for you.")
            elif tag == 'general_query':
                speak("Accessing my external knowledge base for that question.")
            
            # Use the LLM API for dynamic answer
            api_response = get_api_answer(command)
            speak(api_response)
            return

        # Case C: High Confidence Standard Intent (confidence >= 0.55 and tag is NOT general_query)
        for i in data['intents']:
            if i['tag'] == tag:
                
                # Special handler for 'datetime'
                if tag == 'datetime':
                    now = datetime.datetime.now()
                    response = f"The current time is {now.strftime('%I:%M %p')} and today is {cal_day()}."
                    speak(response)
                    return
                
                # Use a random canned response for all other standard tags (greeting, jokes, etc.)
                response = random.choice(i['responses'])
                speak(response)
                return
        
        # Final fallback if a high-confidence tag is somehow missed
        speak("Sorry, I understood your intent but couldn't find a suitable response.")
        
    except Exception as e:
        speak(f"An unexpected error occurred during AI processing: {e}")


# --- Main Execution Loop ---
if __name__ == "__main__":
    wishme()
    unrecognized_count = 0 # Counter for failed audio recognition
    while True:
        command = listen()
        if command:
            handle_command(command)
            unrecognized_count = 0 # Reset counter on success
        else:
            # If listen() returns None (timeout or unknown audio)
            unrecognized_count += 1
            if unrecognized_count >= 2:
                 speak("I am having trouble hearing you. Please ensure your microphone is clear or restart the application.")
                 unrecognized_count = 0 # Prevent immediate loop if next one fails too
            else:
                 speak("I did not catch that. Please try again.")