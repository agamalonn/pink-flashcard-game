import tkinter as tk
import json
from gtts import gTTS
import os
import random
import tempfile
from tkinter import simpledialog, messagebox

file_path = "/Users/agamalon/Downloads/pink-word-game/Agam_wordlist_with_stats.json"
new_words_path = "/Users/agamalon/Downloads/pink-word-game/new_words.json"  # NEW

# Load words
def load_words(mode):
    if mode == "new":
        try:
            with open(new_words_path, "r", encoding="utf-8") as f:
                words = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            words = []
    else:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                words = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            words = []
    random.shuffle(words)
    return words

# Prompt for mode
root = tk.Tk()
root.withdraw()  # Hide main window for now
mode = simpledialog.askstring(
    "Practice Mode",
    "Which vocabulary do you want to practice?\nType 'gen' for general or 'new' for new words."
)
if not mode or mode.lower() not in ("gen", "new"):
    messagebox.showinfo("Info", "Invalid mode. Closing app.")
    root.destroy()
    exit()
mode = mode.lower()
words = load_words(mode)
index = 0
showing_translation = False

def speak(text, lang):
    tts = gTTS(text=text, lang=lang)
    with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as fp:
        tts.save(fp.name)
        os.system(f"afplay {fp.name}")

def toggle_card():
    global showing_translation
    if not showing_translation:
        word_label.config(text=words[index]["hebrew"])
        showing_translation = True
    else:
        word_label.config(text=words[index]["english"])
        showing_translation = False

def next_card():
    global index, showing_translation
    if len(words) == 0:
        word_label.config(text="No words left!")
        sentence_label.config(text="")
        return
    index = (index + 1) % len(words)
    showing_translation = False
    word_label.config(text=words[index]["english"])
    sentence_label.config(text=words[index]["sentence"])

def play_word():
    lang = "en" if not showing_translation else "he"
    text = words[index]["english"] if lang == "en" else words[index]["hebrew"]
    speak(text, lang)

def play_sentence():
    lang = "en" if not showing_translation else "he"
    sentence = words[index]["sentence"] if lang == "en" else words[index]["hebrew"]
    speak(sentence, lang)

def delete_current_word():
    global index
    if len(words) == 0:
        return
    del words[index]
    if mode == "new":
        # Save to new_words_path
        with open(new_words_path, "w", encoding="utf-8") as f:
            json.dump(words, f, ensure_ascii=False, indent=2)
    else:
        # Save to main file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(words, f, ensure_ascii=False, indent=2)

    if len(words) == 0:
        word_label.config(text="No words left!")
        sentence_label.config(text="")
        return

    index = index % len(words)
    word_label.config(text=words[index]["english"])
    sentence_label.config(text=words[index]["sentence"])

def dont_know_word():
    # Add to new_words.json if not already there
    try:
        with open(new_words_path, "r", encoding="utf-8") as f:
            new_words = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        new_words = []
    current_word = words[index]
    if current_word not in new_words:
        new_words.append(current_word)
        with open(new_words_path, "w", encoding="utf-8") as f:
            json.dump(new_words, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Info", "Word added to 'New Words' list!")
    else:
        messagebox.showinfo("Info", "Word is already in 'New Words' list.")

# GUI setup
root.deiconify()
root.title("Agami's Pink Flashcard Game 💖")
root.geometry("700x680")
root.configure(bg="#ffadbb")

word_label = tk.Label(root, font=("Comic Sans MS", 40, "bold"),
                      bg="#ffe6f0", fg="#cc0066",
                      wraplength=360, width=15, height=2, relief="ridge", bd=3)
word_label.pack(pady=20)

sentence_label = tk.Label(root, font=("Arial", 20, "italic"),
                          bg="#ffc0cb", fg="#5a5a5a",
                          wraplength=360)
sentence_label.pack(pady=5)

btn_style = {"width": 12, "font": ("Comic Sans MS", 20, "bold"), "bg": "#5f0e37", "fg": "white", "relief": "raised"}

flip_btn = tk.Button(root, text="💫Flip", command=toggle_card, **btn_style)
flip_btn.pack(pady=5)

next_btn = tk.Button(root, text="➡️Next", command=next_card, **btn_style)
next_btn.pack(pady=5)

voice_btn = tk.Button(root, text="🔊Speak", command=play_word, **btn_style)
voice_btn.pack(pady=5)

delete_btn = tk.Button(root, text="🗑️Delete", command=delete_current_word, **btn_style)
delete_btn.pack(pady=5)

dont_know_btn = tk.Button(root, text="❓Don't Know", command=dont_know_word, **btn_style)
dont_know_btn.pack(pady=5)

voice_s_btn = tk.Button(root, text="listen", command=play_sentence, **btn_style)
voice_s_btn.pack(pady=5)

if len(words) > 0:
    word_label.config(text=words[index]["english"])
    sentence_label.config(text=words[index]["sentence"])
else:
    word_label.config(text="No words found")
    sentence_label.config(text="")

root.mainloop()