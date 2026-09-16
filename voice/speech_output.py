import pyttsx3


engine = pyttsx3.init()

engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)


def speak(text):

    print("🔊 AI:", text)

    engine.say(text)
    engine.runAndWait()


if __name__ == "__main__":

    speak("Hello buddy. Your AI agent is now speaking.")