import json
import os
import openai
from googletrans import Translator
from gtts import gTTS
import tkinter as tk
from tkinter import messagebox, scrolledtext

# Set your OpenAI API key
openai.api_key = 'YOUR_OPENAI_API_KEY'

MAIN_FILE = "agam_wordlist_with_stats.json"
NEW_WORDS_FILE = "new_words.json"

def generate_sentence(word):
    prompt = f"Write a clear, simple English sentence using the word '{word}'."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=25,
        temperature=0.5
    )
    return response.choices[0].text.strip()

def translate_to_hebrew(text):
    translator = Translator()
    return translator.translate(text, src='en', dest='he').text

def save_to_json(word_obj, main_file=MAIN_FILE, new_words_file=NEW_WORDS_FILE):
    # Load or create files
    for file, key in [(main_file, 'main_words'), (new_words_file, 'new_words')]:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []
        if not any(w['english'].lower() == word_obj['english'].lower() for w in data):
            data.append(word_obj)
            with open(file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

def pronounce_word(word):
    tts = gTTS(text=word, lang='en')
    filename = f"tts_{word}.mp3"
    tts.save(filename)
    os.system(f"start {filename}")  # use 'afplay' on mac, 'start' on win, 'xdg-open' on linux

def process_words(words):
    result = []
    for w in words:
        sentence = generate_sentence(w)
        hebrew_word = translate_to_hebrew(w)
        hebrew_sentence = translate_to_hebrew(sentence)
        word_obj = {
            "english": w,
            "hebrew": hebrew_word,
            "sentence": sentence,
            "sentence_hebrew": hebrew_sentence,
            "count_right_guess": 0,
            "count_wrong_guess": 0,
            "success_rate": 0.0,
            "category": "new"
        }
        result.append(word_obj)
    return result

def review_and_save(words_objs):
    root = tk.Tk()
    root.title("Review AI-Generated Words")
    frames = []

    def on_ok(idx):
        save_to_json(words_objs[idx])
        frames[idx].destroy()
        if all(not frame.winfo_ismapped() for frame in frames):
            messagebox.showinfo("Done", "All words processed!")
            root.destroy()

    def on_delete(idx):
        frames[idx].destroy()
        if all(not frame.winfo_ismapped() for frame in frames):
            messagebox.showinfo("Done", "All words processed!")
            root.destroy()

    for idx, word in enumerate(words_objs):
        frame = tk.Frame(root, relief=tk.RAISED, borderwidth=2)
        frame.pack(fill='x', padx=8, pady=6)
        frames.append(frame)
        # Display details
        text = f"English: {word['english']}\nHebrew: {word['hebrew']}\nSentence: {word['sentence']}\nHebrew Sentence: {word['sentence_hebrew']}"
        label = tk.Label(frame, text=text, justify='left', font=('Arial', 12))
        label.pack(side='left', padx=10)
        # OK Button
        btn_ok = tk.Button(frame, text="OK", command=lambda idx=idx: on_ok(idx), fg='green')
        btn_ok.pack(side='left', padx=5)
        # Delete Button
        btn_del = tk.Button(frame, text="Delete", command=lambda idx=idx: on_delete(idx), fg='red')
        btn_del.pack(side='left', padx=5)

    root.mainloop()

def main():
    print("Enter English words you want to learn (one per line). Type 'done' when finished:")
    words = []
    while True:
        w = input()
        if w.strip().lower() == 'done':
            break
        if w.strip():
            words.append(w.strip())
    if not words:
        print("No words entered. Exiting.")
        return
    print("Generating sentences and translations with AI...")
    words_objs = process_words(words)
    review_and_save(words_objs)

if __name__ == "__main__":
    main()