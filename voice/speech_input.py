import speech_recognition as sr


def listen():

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:

        print("🎤 Listening...")

        recognizer.adjust_for_ambient_noise(source, duration=1)

        audio = recognizer.listen(source)

    try:

        text = recognizer.recognize_google(audio)

        print("🗣️ You said:", text)

        return text

    except sr.UnknownValueError:

        print("❌ I couldn't understand you.")
        return ""

    except sr.RequestError as error:

        print("❌ Speech recognition error:", error)
        return ""


if __name__ == "__main__":

    listen()