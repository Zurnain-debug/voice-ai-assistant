import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
import threading

# Gemini configuration
genai.configure(api_key="Add your API key here")
model = genai.GenerativeModel("gemini-1.5-flash")

# Speech recognition and TTS setup
recognizer = sr.Recognizer()
tts = pyttsx3.init()

# 👩 Set voice to female (if available)
voices = tts.getProperty('voices')
if len(voices) > 1:
    tts.setProperty('voice', voices[1].id)  # voice[0] is usually male, voice[1] female

class VoiceAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini Voice Assistant")
        self.root.geometry("720x600")
        self.root.configure(bg="#f4f6f8")

        self.paused = False
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.root, text="🎙️ Gemini AI Assistant", font=("Segoe UI", 22, "bold"), bg="#f4f6f8").pack(pady=10)

        frame = tk.Frame(self.root, bg="#ffffff", bd=1, relief=tk.RIDGE)
        frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        self.chat_box = scrolledtext.ScrolledText(frame, font=("Consolas", 12), wrap=tk.WORD)
        self.chat_box.pack(fill=tk.BOTH, expand=True)
        self.chat_box.config(state=tk.DISABLED)

        self.status_label = tk.Label(self.root, text="Status: Idle", font=("Segoe UI", 12), fg="green", bg="#f4f6f8")
        self.status_label.pack(pady=5)

        try:
            mic_image = Image.open("mic.png").resize((60, 60))
            self.mic_icon = ImageTk.PhotoImage(mic_image)
            mic_button = tk.Button(self.root, image=self.mic_icon, command=self.listen_threaded, bd=0, bg="#f4f6f8")
        except:
            mic_button = tk.Button(self.root, text="🎤 Speak", font=("Segoe UI", 14), command=self.listen_threaded, bg="#4caf50", fg="white", padx=20, pady=10)
        mic_button.pack(pady=10)

        btn_frame = tk.Frame(self.root, bg="#f4f6f8")
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="🧹 Clear", command=self.clear_chat, font=("Segoe UI", 10), bg="#eeeeee").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="⏸️ Pause", command=self.pause_speaking, font=("Segoe UI", 10), bg="#eeeeee").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="▶️ Resume", command=self.resume_speaking, font=("Segoe UI", 10), bg="#eeeeee").pack(side=tk.LEFT, padx=10)

    def listen_threaded(self):
        if self.paused:
            self.update_chat("🔇 Gemini", "Currently paused. Click Resume to continue.")
            return
        threading.Thread(target=self.listen_and_respond, daemon=True).start()

    def clear_chat(self):
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.delete(1.0, tk.END)
        self.chat_box.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Idle", fg="green")

    def update_chat(self, speaker, text):
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.insert(tk.END, f"{speaker}: {text}\n\n")
        self.chat_box.see(tk.END)
        self.chat_box.config(state=tk.DISABLED)

    def pause_speaking(self):
        self.paused = True
        tts.stop()
        self.status_label.config(text="Status: Paused", fg="orange")
        self.update_chat("🔇 Gemini", "Assistant paused. Click Resume to continue.")

    def resume_speaking(self):
        self.paused = False
        self.status_label.config(text="Status: Idle", fg="green")
        self.update_chat("▶️ Gemini", "Assistant resumed. Click Mic to continue.")

    def listen_and_respond(self):
        try:
            self.status_label.config(text="Status: Listening...", fg="blue")
            with sr.Microphone() as source:
                audio = recognizer.listen(source)

            self.status_label.config(text="Status: Recognizing...", fg="orange")
            user_input = recognizer.recognize_google(audio)
            self.update_chat("🗣 You", user_input)

            self.status_label.config(text="Status: Thinking...", fg="purple")
            response = model.generate_content(user_input)
            reply = response.text.strip()
            self.update_chat("🤖 Gemini", reply)

            if not self.paused:
                self.status_label.config(text="Status: Speaking...", fg="green")
                tts.say(reply)
                tts.runAndWait()
                self.status_label.config(text="Status: Idle", fg="green")
            else:
                self.update_chat("⏸️ Paused", "Gemini is paused, no voice output.")

        except sr.UnknownValueError:
            self.update_chat("❌ Error", "Could not understand audio.")
            self.status_label.config(text="Status: Idle", fg="red")
        except Exception as e:
            self.update_chat("❌ Error", str(e))
            self.status_label.config(text="Status: Error", fg="red")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceAssistantApp(root)
    root.mainloop()
