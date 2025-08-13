import speech_recognition as sr
import win32com.client
import webbrowser
import datetime
import os
from config import apikey, weather_apikey, news_apikey
import requests
import re
import random

speaker = win32com.client.Dispatch("SAPI.SpVoice")

def wait_for_wake_word(wake_word="jarvis"):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for wake word...")
        while True:
            try:
                audio = r.listen(source, timeout=1, phrase_time_limit=5)
                query = r.recognize_google(audio, language="en-in").lower()
                print("Heard:", query)
                if wake_word in query:
                    speaker.Speak("Yes sir, I am listening.")
                    return
            except sr.UnknownValueError:
                continue
            except sr.WaitTimeoutError:
                continue
            except sr.RequestError:
                print("Speech recognition service is unavailable.")
                break


def extract_news_topic(query):
    known_categories = [
        "business", "entertainment", "general",
        "health", "science", "sports", "technology"
    ]
    for category in known_categories:
        if category in query.lower():
            return category
    # fallback regex for generic topics
    match = re.search(r"news (?:about|on|regarding)\s+([a-zA-Z\s]+)", query.lower())
    if match:
        return match.group(1).strip()
    return None


def get_news(topic=None):
    def fetch_and_speak(url, fallback=False):
        response = requests.get(url)

        if response.status_code == 200:
            articles = response.json().get("articles", [])
            if articles:
                if fallback:
                    speaker.Speak("No India-specific news found, but here are some global news headlines.")
                else:
                    speaker.Speak(f"Here are the top headlines{' about ' + topic if topic else ''}:")

                for i, article in enumerate(articles[:3], 1):  # Limit to 3 headlines
                    headline = article["title"]
                    print(f"{i}. {headline}")
                    speaker.Speak(headline)
                return True
        return False

    topic_to_category = {
        "business": "business",
        "entertainment": "entertainment",
        "general": "general",
        "health": "health",
        "science": "science",
        "sports": "sports",
        "technology": "technology"
    }

    fetched = False

    if topic and topic.lower() in topic_to_category:
        category = topic_to_category[topic.lower()]
        url = f"https://newsapi.org/v2/top-headlines?country=in&category={category}&apiKey={news_apikey}&pageSize=5"
        fetched = fetch_and_speak(url)

    if not fetched:
        url = f"https://newsapi.org/v2/everything?q={topic or 'india'}&apiKey={news_apikey}&language=en&pageSize=5&sortBy=publishedAt"
        fetched = fetch_and_speak(url, fallback=True)

    if not fetched:
        speaker.Speak("Sorry, I couldn't find any news on that topic.")



def extract_city_from_query(query):
    match = re.search(r"(?:weather|temperature|forecast) in ([a-zA-Z\s]+)", query.lower())
    if match:
        city = match.group(1).strip().title()
        return city
    return None

def get_weather(city="New Delhi"):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_apikey}&units=metric"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        weather_report = f"The temperature in {city} is {temp}°C with {desc}."
        print(weather_report)
        speaker.Speak(weather_report)
    else:
        error = "Sorry, I couldn't fetch the weather right now."
        print(error)
        speaker.Speak(error)

chat_history = [
    {"role": "system", "content": "You are Jarvis, a helpful desktop assistant."}
]

def ai_chat(prompt):
    chat_history.append({"role": "user", "content": prompt})

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {apikey}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-70b-8192",
        "messages": chat_history,
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        ai_text = response.json()["choices"][0]["message"]["content"]
        chat_history.append({"role": "assistant", "content": ai_text})

        print("Jarvis AI:", ai_text)
        speaker.Speak(ai_text)

        return ai_text

    else:
        error_msg = f"AI request failed with status {response.status_code}"
        print(error_msg)
        speaker.Speak("Sorry, I couldn't get a response from AI.")
        return None


def ai(prompt):

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {apikey}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        ai_text = response.json()["choices"][0]["message"]["content"]
        print("Jarvis AI:", ai_text)
        speaker.Speak(ai_text)

        # Save prompt and response to file
        folder = "GrokAI_logs"
        if not os.path.exists(folder):
            os.makedirs(folder)

        # Use timestamp in filename for uniqueness
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{folder}/conversation_{timestamp}.txt"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Prompt:\n{prompt}\n\nResponse:\n{ai_text}")

        return ai_text

    else:
        error_msg = f"AI request failed with status {response.status_code}"
        print(error_msg)
        speaker.Speak("Sorry, I couldn't get a response from AI.")
        return None


def takeCommand() :
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        try:
            print("Recognizing..")
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            return query
        except sr.UnknownValueError:
            print("Could not understand audio.")
        except sr.RequestError:
            print("Speech recognition service is unavailable.")
        return None


print("Hello, I am Jarvis AI.")
speaker.Speak("Hello, I am Jarvis AI.")

while True:
    wait_for_wake_word()  # Wait for activation once
    print("Activated. Listening for commands...")

    while True:  # Inner loop for continuous command listening
        query = takeCommand()
        if query is None:
            continue

        query = query.lower()

        sites = [["youtube", "https://www.youtube.com"], ["wikipedia", "https://www.wikipedia.com"],
                 ["google", "https://www.google.com"], ["instagram", "https://www.instagram.com"] ]
        for site in sites:
            if f"Open {site[0]}".lower() in query.lower():
                speaker.Speak(f"Opening {site[0]} sir...")
                webbrowser.open(site[1])

        if "go to sleep" in query:
            speaker.Speak("Going to sleep mode. Say my name when you need me.")
            break  # Breaks inner loop, returns to wake word listening

        elif any(word in query for word in ["exit", "shutdown", "quit", "jarvis exit"]):
            farewell = "Goodbye, sir. Shutting down now."
            speaker.Speak(farewell)
            exit()

        elif "the time" in query:
            strfTime = datetime.datetime.now().strftime("%H:%M:%S")
            speaker.Speak(f"Sir the time is {strfTime}")

        elif "music" in query:
            music_folder = r"C:\Users\91942\Music"  # Change this to your folder path
            songs = [song for song in os.listdir(music_folder) if song.endswith(('.mp3', '.wav'))]

            if songs:
                random_song = random.choice(songs)
                song_path = os.path.join(music_folder, random_song)
                speaker.Speak(f"Playing a random song: {random_song}")
                os.startfile(song_path)
            else:
                speaker.Speak("I couldn't find any music files in the folder.")

        elif "open whatsapp" in query:
            speaker.Speak("Opening WhatsApp")
            os.system("start shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App")

        elif "using artificial intelligence" in query:
            ai(prompt=query)

        elif "chat reset" in query:
            chat_history = [
                {"role": "system", "content": "You are Jarvis, a helpful desktop assistant."}
            ]
            speaker.Speak("Chat history has been reset.")


        elif any(word in query.lower() for word in ["weather", "temperature", "forecast"]):
            city = extract_city_from_query(query)
            if city:
                speaker.Speak(f"Fetching weather for {city}...")
                get_weather(city)
            else:
                speaker.Speak("No city detected. Fetching default weather for New Delhi.")
                get_weather("New Delhi")


        elif "news" in query:
            topic = extract_news_topic(query)
            if topic:
                speaker.Speak(f"Fetching news about {topic}...")
                get_news(topic=topic)
            else:
                speaker.Speak("Fetching top headlines...")
                get_news()

        else:
            ai_chat(prompt=query)