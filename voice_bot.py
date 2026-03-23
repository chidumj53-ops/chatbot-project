from chat import get_response
import speech_recognition as sr
import pyttsx3

engine = pyttsx3.init()
recognizer = sr.Recognizer()

def speak(text):
    engine.say(text)
    engine.runAndWait()

print("Voice Chatbot Started... Speak!")

while True:
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        user_text = recognizer.recognize_google(audio)
        print("You:", user_text)

        response = get_response(user_text)
        print("Bot:", response)

        speak(response)
    except:
        print("Sorry, I didn't catch that.")