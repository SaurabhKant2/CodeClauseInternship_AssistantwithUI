import tkinter as tk
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import pyjokes
import wikipedia
import sqlite3

# ---------- DATABASE SETUP ----------
conn = sqlite3.connect('assistant.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        command TEXT,
        response TEXT,
        timestamp TEXT
    )
''')
conn.commit()

def save_to_history(command, response):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO history (command, response, timestamp) VALUES (?, ?, ?)",
                   (command, response, timestamp))
    conn.commit()

def view_history():
    records = cursor.execute("SELECT * FROM history ORDER BY id DESC LIMIT 10").fetchall()
    if not records:
        messagebox.showinfo("History", "No command history found.")
        return
    log = "\n".join([f"{r[3]} ➤ {r[1]} → {r[2]}" for r in records])
    messagebox.showinfo("Command History (Last 10)", log)

# ---------- TEXT TO SPEECH ----------
engine = pyttsx3.init()
engine.setProperty('rate', 150)

def speak(text):
    engine.say(text)
    engine.runAndWait()

# ---------- PROCESS COMMAND ----------
def process_command(command):
    if "time" in command:
        now = datetime.datetime.now().strftime("%I:%M %p")
        return f"The time is {now}"

    elif "date" in command:
        today = datetime.date.today().strftime("%B %d, %Y")
        return f"Today is {today}"

    elif "google" in command:
        webbrowser.open("https://www.google.com")
        return "Opening Google"

    elif "youtube" in command:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube"

    elif "your name" in command:
        return "I'm your voice assistant!"

    elif "joke" in command:
        return pyjokes.get_joke()

    elif "wikipedia" in command:
        try:
            topic = command.replace("wikipedia", "").strip()
            return f"According to Wikipedia: {wikipedia.summary(topic, sentences=2)}"
        except:
            return "Sorry, I couldn't find that on Wikipedia."

    else:
        return "Sorry, I don't understand that."

# ---------- SPEECH INPUT ----------
def listen_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        status_label.config(text="Listening...")
        root.update()
        try:
            audio = recognizer.listen(source, timeout=5)
            return recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand."
        except sr.RequestError:
            return "Speech service unavailable."
        except sr.WaitTimeoutError:
            return "You were silent. Try again."

# ---------- BUTTON CLICK ----------
def on_mic_click():
    command = listen_command()
    command_display.config(state='normal')
    command_display.delete(1.0, tk.END)
    command_display.insert(tk.END, command)
    command_display.config(state='disabled')

    response = process_command(command)
    response_label.config(text=response)
    speak(response)
    save_to_history(command, response)
    status_label.config(text="Ready")

# ---------- GUI SETUP ----------
root = tk.Tk()
root.title("Voice Assistant with DB")
root.geometry("450x480")
root.configure(bg="#f0f0f0")

tk.Label(root, text="🎤 Voice Assistant", font=("Helvetica", 18, "bold"), bg="#f0f0f0").pack(pady=10)

tk.Button(root, text="🎙️ Tap to Speak", font=("Helvetica", 14), command=on_mic_click,
          bg="#007bff", fg="white", padx=20, pady=10).pack(pady=15)

command_display = tk.Text(root, height=3, font=("Helvetica", 12), wrap=tk.WORD, state='disabled')
command_display.pack(pady=10)

response_label = tk.Label(root, text="", font=("Helvetica", 12), bg="#f0f0f0", wraplength=400)
response_label.pack(pady=10)

tk.Button(root, text="📜 View History", font=("Helvetica", 12), command=view_history,
          bg="#6c757d", fg="white", padx=10).pack(pady=10)

status_label = tk.Label(root, text="Ready", font=("Helvetica", 10), bg="#f0f0f0", fg="green")
status_label.pack(pady=5)

root.mainloop()
