import json
import os

FILENAME = "agam_wordlist_with_stats.json"
words = []

# Load existing words
if os.path.exists(FILENAME):
    with open(FILENAME, encoding="utf-8") as f:
        words = json.load(f)

def find_word_index(english_word):
    return next((i for i, w in enumerate(words) if w["english"].lower() == english_word.lower()), -1)

def add_words_bulk_paste():
    print("\n✨ Welcome to your bulk paste vocabulary manager!")
    print("📋 Paste multiple lines in this format:")
    print("    english - hebrew - sentence")
    print("🔻 When you're done pasting, type 'done' on a new line.\n")

    lines = []

    while True:
        line = input()
        if line.strip().lower() == "done":
            break
        if line.strip():
            lines.append(line.strip())

    added = 0
    skipped = 0

    for line in lines:
        if " - " not in line:
            print(f"❗ Skipped invalid line (missing '-'): {line}")
            continue

        parts = line.split(" - ", 2)
        if len(parts) < 3:
            print(f"❗ Skipped invalid line (not enough parts): {line}")
            continue

        english, hebrew, sentence = parts

        if find_word_index(english) != -1:
            print(f"⚠️ Word '{english.strip()}' already exists. Skipping.")
            skipped += 1
            continue

        words.append({
            "english": english.strip(),
            "hebrew": hebrew.strip(),
            "sentence": sentence.strip(),
            "count_right_guess": 0,
            "count_wrong_guess": 0,
            "success_rate": 0.0,
            "category": "new"
        })
        print(f"✅ Added: {english.strip()} → {hebrew.strip()}")
        added += 1

    # Save back to file
    with open(FILENAME, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)

    print(f"\n🎯 Finished! {added} words added, {skipped} words skipped (already exist).")

# Start interaction
add_words_bulk_paste()
