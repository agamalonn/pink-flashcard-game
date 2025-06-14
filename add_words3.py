import json
import os

MAIN_FILE = "agam_wordlist_with_stats.json"
NEW_WORDS_FILE = "/Users/agamalon/Downloads/pink-word-game/new_words.json"

def add_words_to_files(words_to_add, main_file=MAIN_FILE, new_words_file=NEW_WORDS_FILE):
    # Load current vocabulary
    if os.path.exists(main_file):
        with open(main_file, "r", encoding="utf-8") as f:
            main_words = json.load(f)
    else:
        main_words = []

    # Load current new words list
    if os.path.exists(new_words_file):
        with open(new_words_file, "r", encoding="utf-8") as f:
            new_words = json.load(f)
    else:
        new_words = []

    # To avoid duplicates
    main_english = {w["english"].lower() for w in main_words}
    new_english = {w["english"].lower() for w in new_words}

    added_to_main = []
    added_to_new = []

    for word in words_to_add:
        english = word["english"].strip().lower()
        # Add to main vocab if new
        if english not in main_english:
            main_words.append(word)
            main_english.add(english)
            added_to_main.append(word["english"])
        # Add to new_words if new
        if english not in new_english:
            new_words.append(word)
            new_english.add(english)
            added_to_new.append(word["english"])

    # Save back to files
    with open(main_file, "w", encoding="utf-8") as f:
        json.dump(main_words, f, ensure_ascii=False, indent=2)
    with open(new_words_file, "w", encoding="utf-8") as f:
        json.dump(new_words, f, ensure_ascii=False, indent=2)

    print(f"✅ Added to main vocab: {added_to_main}")
    print(f"✅ Added to new words: {added_to_new}")

# ---- Bulk Paste Logic ----

def find_word_index(english_word, words):
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

    # Load existing words for duplicate detection
    if os.path.exists(MAIN_FILE):
        with open(MAIN_FILE, encoding="utf-8") as f:
            existing_words = json.load(f)
    else:
        existing_words = []

    added = 0
    skipped = 0
    words_to_add = []

    for line in lines:
        if " - " not in line:
            print(f"❗ Skipped invalid line (missing '-'): {line}")
            continue
        parts = line.split(" - ", 2)
        if len(parts) < 3:
            print(f"❗ Skipped invalid line (not enough parts): {line}")
            continue
        english, hebrew, sentence = parts
        if find_word_index(english, existing_words) != -1 or any(w["english"].lower() == english.strip().lower() for w in words_to_add):
            print(f"⚠️ Word '{english.strip()}' already exists. Skipping.")
            skipped += 1
            continue

        word_obj = {
            "english": english.strip(),
            "hebrew": hebrew.strip(),
            "sentence": sentence.strip(),
            "count_right_guess": 0,
            "count_wrong_guess": 0,
            "success_rate": 0.0,
            "category": "new"
        }
        words_to_add.append(word_obj)
        print(f"✅ Will add: {english.strip()} → {hebrew.strip()}")
        added += 1

    # Use the general function to update both files
    add_words_to_files(words_to_add)

    print(f"\n🎯 Finished! {added} words added, {skipped} words skipped (already exist).")

# ---- Start interaction ----
if __name__ == "__main__":
    add_words_bulk_paste()
