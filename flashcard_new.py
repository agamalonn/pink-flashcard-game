import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import json
from gtts import gTTS
import os
import random
import tempfile

file_path = "/Users/agamalon/Downloads/pink-word-game/Agam_wordlist_with_stats.json"
new_words_path = "/Users/agamalon/Downloads/pink-word-game/new_words.json"

class FlashcardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Agami's Pink Flashcard Game 💖")
        self.root.geometry("950x800")
        self.root.configure(bg="#ffe6f7")
        self.center_window()
        self.mode = self.ask_mode()
        if not self.mode:
            self.root.destroy()
            exit()
        self.words = self.load_words(self.mode)
        self.index = 0
        self.showing_translation = False
        self.dark_mode = False
        self.show_all_translations = False
        self.known_words = set()
        self.cards_seen = set()
        self.starred = set()
        self.review_starred_only = False
        self.show_sentence = True
        self.session_start_time = None
        self.font_size = 40
        self.setup_styles()
        self.setup_ui()
        self.update_card()
        self.root.bind("<Right>", lambda e: self.next_card())
        self.root.bind("<Left>", lambda e: self.prev_card())
        self.root.bind("<space>", lambda e: self.toggle_card())
        self.root.bind("<Return>", lambda e: self.toggle_card())
        self.root.bind("d", lambda e: self.dont_know_word())
        self.root.bind("x", lambda e: self.delete_current_word())
        self.root.bind("r", lambda e: self.reset())
        self.root.bind("s", lambda e: self.shuffle_cards())
        self.root.bind("<F1>", lambda e: self.show_help())
        self.root.bind("k", lambda e: self.mark_as_known())
        self.root.bind("g", lambda e: self.goto_card_dialog())
        self.root.bind("t", lambda e: self.toggle_all_translations())
        self.root.bind("m", lambda e: self.toggle_dark_mode())
        self.root.bind("p", lambda e: self.show_stats())
        self.root.bind("f", lambda e: self.toggle_starred())
        self.root.bind("v", lambda e: self.toggle_review_starred())
        self.root.bind("z", lambda e: self.random_card())
        self.root.bind("c", lambda e: self.copy_word())
        self.root.bind("+", lambda e: self.increase_font())
        self.root.bind("-", lambda e: self.decrease_font())
        self.root.bind("e", lambda e: self.toggle_sentence())
        self.session_start_time = self._now()
        self.update_timer()

    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.root.geometry(f'{w}x{h}+{x}+{y}')

    def ask_mode(self):
        self.root.withdraw()
        mode = simpledialog.askstring(
            "Practice Mode",
            "Which vocabulary do you want to practice?\nType 'gen' for general or 'new' for new words."
        )
        self.root.deiconify()
        if not mode or mode.lower() not in ("gen", "new"):
            messagebox.showinfo("Info", "Invalid mode. Closing app.")
            return None
        return mode.lower()

    def load_words(self, mode):
        path = new_words_path if mode == "new" else file_path
        try:
            with open(path, "r", encoding="utf-8") as f:
                words = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            words = []
        random.shuffle(words)
        return words

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Pink.TButton",
                        font=("Segoe UI Semibold", 17),
                        padding=(22, 22),
                        width=24,  # Wider buttons
                        background="#ffb6d5",
                        foreground="#fff",
                        borderwidth=0,
                        relief="flat")
        style.map("Pink.TButton",
                  background=[('active', '#ff69b4'), ('!active', '#ffb6d5')],
                  foreground=[('active', '#fff'), ('!active', '#fff')],
                  relief=[('pressed', 'groove'), ('!pressed', 'flat')])

    def setup_ui(self):
        # Gradient background (simulate with canvas)
        bg_canvas = tk.Canvas(self.root, width=950, height=800, highlightthickness=0)
        bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        for i in range(0, 800, 2):
            color = self._gradient_color("#ffe6f7", "#ffb6d5", i / 800)
            bg_canvas.create_rectangle(0, i, 950, i+2, outline="", fill=color)

        # Custom title bar
        title_frame = tk.Frame(self.root, bg="#ff69b4")
        title_frame.place(relx=0, rely=0, relwidth=1, height=70)
        logo = tk.Label(title_frame, text="💖", font=("Segoe UI Emoji", 36), bg="#ff69b4", fg="#fff")
        logo.pack(side="left", padx=(30, 10), pady=10)
        title_label = tk.Label(title_frame, text="Agami's Pink Flashcard Game", font=("Segoe UI Black", 28, "bold"),
                               bg="#ff69b4", fg="#fff", anchor="w")
        title_label.pack(side="left", padx=10, pady=10)

        # Main frame for centering
        main_frame = tk.Frame(self.root, bg="#ffe6f7", highlightthickness=0)
        main_frame.pack(expand=True, fill="both", pady=(80, 40))

        self.progress_label = tk.Label(main_frame, font=("Segoe UI", 16, "bold"),
                                       bg="#ffe6f7", fg="#d72660")
        self.progress_label.place(x=30, y=10)

        # Card shadow effect (simulate drop shadow)
        shadow = tk.Frame(main_frame, bg="#ffb6d5")
        shadow.place(relx=0.5, rely=0.28, anchor="center", width=600, height=300)

        # Card frame (rounded look, simulated)
        card_frame = tk.Frame(main_frame, bg="#fff0fa", bd=0, highlightthickness=0)
        card_frame.place(relx=0.5, rely=0.26, anchor="center", width=580, height=280)
        card_frame.after(100, lambda: self._fade_in(card_frame, 0))

        self.word_label = tk.Label(card_frame, font=("Segoe UI Black", 40, "bold"),
                                  bg="#fff0fa", fg="#d72660",
                                  wraplength=540, width=18, height=2)
        self.word_label.pack(pady=(28, 0))

        self.sentence_label = tk.Label(card_frame, font=("Segoe UI", 20, "italic"),
                                       bg="#fff0fa", fg="#a64d79",
                                       wraplength=540)
        self.sentence_label.pack(pady=(0, 18))

        # --- Place buttons vertically on the left side, scrollable if needed ---
        btn_frame_container = tk.Frame(self.root, bg="#ffe6f7")
        btn_frame_container.place(relx=0.01, rely=0.18, anchor="nw", width=300, height=650)

        # Add a canvas and scrollbar for the button area
        btn_canvas = tk.Canvas(btn_frame_container, bg="#ffe6f7", highlightthickness=0)
        btn_scrollbar = tk.Scrollbar(btn_frame_container, orient="vertical", command=btn_canvas.yview)
        btn_scrollable_frame = tk.Frame(btn_canvas, bg="#ffe6f7")

        btn_scrollable_frame.bind(
            "<Configure>",
            lambda e: btn_canvas.configure(
                scrollregion=btn_canvas.bbox("all")
            )
        )
        btn_canvas.create_window((0, 0), window=btn_scrollable_frame, anchor="nw")
        btn_canvas.configure(yscrollcommand=btn_scrollbar.set)

        btn_canvas.pack(side="left", fill="both", expand=True)
        btn_scrollbar.pack(side="right", fill="y")

        btn_texts = [
            ("💫 Flip", "Show translation or English"),
            ("➡️ Next", "Go to next card"),
            ("⬅️ Back", "Go to previous card"),
            ("🔊 Speak", "Hear the word"),
            ("🔉 Sentence", "Hear example sentence"),
            ("🗑️ Delete", "Remove this word"),
            ("❓ Don't Know", "Add to 'New Words'"),
            ("🔀 Shuffle", "Randomize the order of cards"),
            ("🔄 Reset", "Restart from first card"),
            ("❔ Help", "Show keyboard shortcuts"),
            ("✅ Known", "Mark as known (remove from list)"),
            ("🔢 Go to #", "Jump to a specific card"),
            ("🌗 Dark Mode", "Toggle dark/light theme"),
            ("👁️ Show Both", "Show both English & Hebrew"),
            ("📊 Stats", "Show session stats"),
            ("⭐ Star", "Mark/unmark as favorite"),
            ("🌟 Review Starred", "Toggle review only starred"),
            ("🎲 Random", "Jump to a random card"),
            ("📋 Copy", "Copy current word"),
            ("👁️ Sentence", "Show/hide example sentence"),
            ("A+ Font", "Increase font size"),
            ("A- Font", "Decrease font size"),
        ]
        btn_cmds = [
            self.toggle_card, self.next_card, self.prev_card, self.play_word,
            self.play_sentence, self.delete_current_word, self.dont_know_word,
            self.shuffle_cards, self.reset, self.show_help,
            self.mark_as_known, self.goto_card_dialog, self.toggle_dark_mode,
            self.toggle_all_translations, self.show_stats,
            self.toggle_starred, self.toggle_review_starred, self.random_card,
            self.copy_word, self.toggle_sentence, self.increase_font, self.decrease_font
        ]
        for i, (main, sub) in enumerate(btn_texts):
            frame = tk.Frame(btn_scrollable_frame, bg="#ffe6f7")
            frame.pack(fill="x", pady=3)
            btn = ttk.Button(frame, text=main, command=btn_cmds[i], style="Pink.TButton", takefocus=True)
            btn.pack(side="left", padx=(6, 6), ipadx=6, ipady=4)
            label = tk.Label(frame, text=sub, font=("Segoe UI", 10), bg="#ffe6f7", fg="#d72660", anchor="w")
            label.pack(side="left", padx=(0, 0), fill="x", expand=True)

        # --- Quiz Widget in the top-right corner (moved up) ---
        self.quiz_frame = tk.Frame(self.root, bg="#fff0fa", bd=2, relief="ridge")
        self.quiz_frame.place(relx=1.0, rely=0.11, anchor="ne", x=-30, y=0, width=340, height=260)
        quiz_title = tk.Label(self.quiz_frame, text="Quiz: Choose the Hebrew meaning", font=("Segoe UI", 14, "bold"),
                              bg="#fff0fa", fg="#d72660")
        quiz_title.pack(pady=(10, 5))
        self.quiz_word_label = tk.Label(self.quiz_frame, text="", font=("Segoe UI", 18, "bold"),
                                        bg="#fff0fa", fg="#5f0e37")
        self.quiz_word_label.pack(pady=(0, 10))
        self.quiz_var = tk.StringVar()
        self.quiz_options = []
        for i in range(4):
            rb = tk.Radiobutton(self.quiz_frame, text="", variable=self.quiz_var, value="", font=("Segoe UI", 13),
                                bg="#fff0fa", fg="#a64d79", anchor="w", selectcolor="#ffe6f7", wraplength=300)
            rb.pack(fill="x", padx=12, pady=1)
            self.quiz_options.append(rb)
        self.quiz_feedback = tk.Label(self.quiz_frame, text="", font=("Segoe UI", 11, "italic"),
                                      bg="#fff0fa", fg="#d72660")
        self.quiz_feedback.pack(pady=(4, 1))
        self.quiz_btn = ttk.Button(self.quiz_frame, text="Check Answer", style="Pink.TButton", command=self.check_quiz)
        self.quiz_btn.pack(pady=(6, 0))
        self.update_quiz()

        # --- Vocabulary List at the bottom right ---
        vocab_frame = tk.Frame(self.root, bg="#fff0fa", bd=2, relief="ridge")
        vocab_frame.place(relx=1.0, rely=1.0, anchor="se", x=-30, y=-20, width=420, height=260)

        vocab_title = tk.Label(vocab_frame, text="📚 Vocabulary List", font=("Segoe UI", 15, "bold"),
                               bg="#fff0fa", fg="#d72660")
        vocab_title.pack(pady=(8, 2))

        # Scrollable area for the vocabulary list
        vocab_canvas = tk.Canvas(vocab_frame, bg="#fff0fa", highlightthickness=0)
        vocab_scrollbar = tk.Scrollbar(vocab_frame, orient="vertical", command=vocab_canvas.yview)
        vocab_inner = tk.Frame(vocab_canvas, bg="#fff0fa")

        vocab_inner.bind(
            "<Configure>",
            lambda e: vocab_canvas.configure(
                scrollregion=vocab_canvas.bbox("all")
            )
        )
        vocab_canvas.create_window((0, 0), window=vocab_inner, anchor="nw")
        vocab_canvas.configure(yscrollcommand=vocab_scrollbar.set)

        vocab_canvas.pack(side="left", fill="both", expand=True, padx=(10,0), pady=(0,10))
        vocab_scrollbar.pack(side="right", fill="y", pady=(0,10))

        self.vocab_inner = vocab_inner
        self.update_vocab_list()

        # Timer label
        self.timer_label = tk.Label(self.root, font=("Segoe UI", 13), bg="#ffe6f7", fg="#d72660")
        self.timer_label.place(relx=0.5, rely=0.01, anchor="n")

        # Footer
        footer = tk.Label(self.root, text="© 2025 Agam Alon's Pink Flashcard Game", font=("Segoe UI", 12),
                          bg="#ffe6f7", fg="#d72660")
        footer.place(relx=0.5, rely=0.98, anchor="s")

    def add_pink_button(self, parent, text, command, row, col, padx, pady):
        btn = ttk.Button(parent, text=text, command=command, style="Pink.TButton", takefocus=True)
        btn.grid(row=row, column=col, padx=padx, pady=pady, ipadx=18, ipady=22, sticky="nsew")
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        # Add focus highlight
        btn.bind("<FocusIn>", lambda e: btn.configure(style="Pink.TButton"))
        btn.bind("<FocusOut>", lambda e: btn.configure(style="Pink.TButton"))
        # Hover effect (simulate shadow)
        def on_enter(e): btn.configure(style="Pink.TButton")
        def on_leave(e): btn.configure(style="Pink.TButton")
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        # Add tooltip
        def show_tooltip(e, tip=text):
            x, y, _, _ = btn.bbox("insert")
            x += btn.winfo_rootx() + 40
            y += btn.winfo_rooty() + 20
            self.tooltip = tk.Toplevel(btn)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            label = tk.Label(self.tooltip, text=tip, bg="#ffb6d5", fg="#fff", font=("Segoe UI", 10))
            label.pack()
        def hide_tooltip(e):
            if hasattr(self, "tooltip"):
                self.tooltip.destroy()
        btn.bind("<Enter>", show_tooltip)
        btn.bind("<Leave>", hide_tooltip)

    def update_card(self):
        if not self.words:
            self.word_label.config(text="No words found")
            self.sentence_label.config(text="")
            self.progress_label.config(text="")
            # Also clear quiz
            self.quiz_word_label.config(text="")
            for rb in self.quiz_options:
                rb.config(text="", value="")
            self.quiz_feedback.config(text="")
            self.update_vocab_list()
            return
        word = self.words[self.index]
        self.cards_seen.add(word["english"])
        star = "⭐ " if word["english"] in self.starred else ""
        if self.show_all_translations:
            self.word_label.config(
                text=f"{star}{word['english']} / {word['hebrew']}", font=("Segoe UI Black", self.font_size, "bold")
            )
        else:
            self.word_label.config(
                text=f"{star}{word['english'] if not self.showing_translation else word['hebrew']}",
                font=("Segoe UI Black", self.font_size, "bold")
            )
        self.sentence_label.config(
            text=word["sentence"] if self.show_sentence else "",
            font=("Segoe UI", 20, "italic")
        )
        self.showing_translation = False
        self.update_progress()
        self.update_quiz()
        self.update_vocab_list()

    def update_progress(self):
        self.progress_label.config(text=f"Card {self.index+1} of {len(self.words)}")

    def toggle_card(self):
        if not self.words or self.show_all_translations:
            return
        if not self.showing_translation:
            self.word_label.config(text=self.words[self.index]["hebrew"])
            self.showing_translation = True
        else:
            self.word_label.config(text=self.words[self.index]["english"])
            self.showing_translation = False

    def next_card(self):
        if not self.words:
            return
        self.index = (self.index + 1) % len(self.words)
        self.update_card()

    def prev_card(self):
        if not self.words:
            return
        self.index = (self.index - 1) % len(self.words)
        self.update_card()

    def speak(self, text, lang):
        try:
            tts = gTTS(text=text, lang=lang)
            with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as fp:
                tts.save(fp.name)
                os.system(f"afplay {fp.name}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not play audio: {e}")

    def play_word(self):
        if not self.words:
            return
        lang = "en" if not self.showing_translation else "he"
        text = self.words[self.index]["english"] if lang == "en" else self.words[self.index]["hebrew"]
        self.speak(text, lang)

    def play_sentence(self):
        if not self.words:
            return
        lang = "en" if not self.showing_translation else "he"
        sentence = self.words[self.index]["sentence"] if lang == "en" else self.words[self.index]["hebrew"]
        self.speak(sentence, lang)

    def delete_current_word(self):
        if not self.words:
            return
        confirm = messagebox.askyesno("Delete", "Are you sure you want to delete this word?")
        if not confirm:
            return
        del self.words[self.index]
        self.save_words()
        if not self.words:
            self.word_label.config(text="No words left!")
            self.sentence_label.config(text="")
            self.progress_label.config(text="")
            return
        self.index = self.index % len(self.words)
        self.update_card()

    def save_words(self):
        path = new_words_path if self.mode == "new" else file_path
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.words, f, ensure_ascii=False, indent=2)

    def dont_know_word(self):
        if not self.words:
            return
        try:
            with open(new_words_path, "r", encoding="utf-8") as f:
                new_words = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            new_words = []
        current_word = self.words[self.index]
        if current_word not in new_words:
            new_words.append(current_word)
            with open(new_words_path, "w", encoding="utf-8") as f:
                json.dump(new_words, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Info", "Word added to 'New Words' list!")
        else:
            messagebox.showinfo("Info", "Word is already in 'New Words' list.")

    def shuffle_cards(self):
        if not self.words:
            return
        random.shuffle(self.words)
        self.index = 0
        self.update_card()
        messagebox.showinfo("Shuffled", "The cards have been shuffled and randomized!")

    def reset(self):
        self.index = 0
        self.update_card()
        messagebox.showinfo("Reset", "Restarted from the first card.")

    def show_help(self):
        help_text = (
            "Keyboard Shortcuts:\n"
            "  → : Next card\n"
            "  ← : Previous card\n"
            "  Space/Enter : Flip card\n"
            "  d : Add to 'New Words'\n"
            "  x : Delete word\n"
            "  r : Reset to first card\n"
            "  s : Shuffle cards\n"
            "  F1 : Show this help\n"
            "  k : Mark as known\n"
            "  g : Go to card #\n"
            "  t : Toggle show both\n"
            "  m : Toggle dark mode\n"
            "  p : Show stats\n"
            "  f : Star/unstar word\n"
            "  v : Review starred only\n"
            "  z : Random card\n"
            "  c : Copy word\n"
            "  e : Show/hide sentence\n"
            "  + : Increase font\n"
            "  - : Decrease font\n"
            "\nEach button now has a short explanation!"
        )
        messagebox.showinfo("Help", help_text)

    def _gradient_color(self, color1, color2, t):
        # color1, color2: "#RRGGBB", t in [0,1]
        def hex2rgb(h): return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))
        def rgb2hex(rgb): return "#%02x%02x%02x" % rgb
        rgb1 = hex2rgb(color1)
        rgb2 = hex2rgb(color2)
        rgb = tuple(int(a + (b - a) * t) for a, b in zip(rgb1, rgb2))
        return rgb2hex(rgb)

    def _fade_in(self, widget, step):
        # Simple fade-in effect for the card (simulate by changing bg color)
        if step > 10:
            return
        color = self._gradient_color("#ffe6f7", "#fff0fa", step / 10)
        widget.configure(bg=color)
        for child in widget.winfo_children():
            child.configure(bg=color)
        widget.after(30, lambda: self._fade_in(widget, step + 1))

    def update_quiz(self):
        # Show the current English word and 4 Hebrew options (one correct, three random)
        if not self.words:
            self.quiz_word_label.config(text="")
            for rb in self.quiz_options:
                rb.config(text="", value="")
            self.quiz_feedback.config(text="")
            return
        current = self.words[self.index]
        correct_hebrew = current["hebrew"]
        # Collect all possible Hebrew meanings (excluding the current one)
        all_hebrew = [w["hebrew"] for w in self.words if w["hebrew"] != correct_hebrew]
        random.shuffle(all_hebrew)
        options = [correct_hebrew] + all_hebrew[:3]
        random.shuffle(options)
        self.quiz_word_label.config(text=current["english"])
        for i, rb in enumerate(self.quiz_options):
            rb.config(text=options[i], value=options[i])
        self.quiz_var.set("")
        self.quiz_feedback.config(text="")

    def check_quiz(self):
        if not self.words:
            return
        selected = self.quiz_var.get()
        correct = self.words[self.index]["hebrew"]
        if not selected:
            self.quiz_feedback.config(text="Please select an option.", fg="#d72660")
        elif selected == correct:
            self.quiz_feedback.config(text="Correct! 🌸", fg="#43a047")
            # Remove from new_words.json if in 'new' mode
            if self.mode == "new":
                del self.words[self.index]
                with open(new_words_path, "w", encoding="utf-8") as f:
                    json.dump(self.words, f, ensure_ascii=False, indent=2)
                if not self.words:
                    self.word_label.config(text="No words left!")
                    self.sentence_label.config(text="")
                    self.progress_label.config(text="")
                    self.quiz_word_label.config(text="")
                    for rb in self.quiz_options:
                        rb.config(text="", value="")
                    self.quiz_feedback.config(text="")
                    return
                self.index = self.index % len(self.words)
                self.update_card()
        else:
            self.quiz_feedback.config(text=f"Incorrect. The correct answer is: {correct}", fg="#d72660")

    def update_vocab_list(self):
        # Clear previous widgets
        for widget in self.vocab_inner.winfo_children():
            widget.destroy()
        # Show all words with a remove button, ultra-dense layout
        for idx, word in enumerate(self.words):
            row = tk.Frame(self.vocab_inner, bg="#fff0fa")
            row.pack(fill="x", pady=0, padx=0, ipady=0)
            en = tk.Label(row, text=word["english"], font=("Segoe UI", 9, "bold"),
                          bg="#fff0fa", fg="#d72660", width=12, anchor="w")
            en.pack(side="left", padx=(0, 1))
            he = tk.Label(row, text=word["hebrew"], font=("Segoe UI", 9),
                          bg="#fff0fa", fg="#5f0e37", width=12, anchor="w")
            he.pack(side="left", padx=(0, 1))
            remove_btn = ttk.Button(row, text="✖", style="Pink.TButton",
                                    width=1, command=lambda i=idx: self.remove_vocab_word(i))
            remove_btn.pack(side="right", padx=(0, 1), ipadx=0)

    def remove_vocab_word(self, idx):
        if not self.words:
            return
        removed_word = self.words.pop(idx)
        # Save if in 'new' mode, else save to main file
        if self.mode == "new":
            with open(new_words_path, "w", encoding="utf-8") as f:
                json.dump(self.words, f, ensure_ascii=False, indent=2)
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.words, f, ensure_ascii=False, indent=2)
        # Adjust index if needed
        if self.index >= len(self.words):
            self.index = max(0, len(self.words) - 1)
        self.update_card()
        self.update_vocab_list()

    def toggle_all_translations(self):
        self.show_all_translations = not self.show_all_translations
        self.update_card()

    def mark_as_known(self):
        if not self.words:
            return
        confirm = messagebox.askyesno("Mark as Known", "Remove this word from your list?")
        if not confirm:
            return
        word = self.words[self.index]
        self.known_words.add(word["english"])
        del self.words[self.index]
        self.save_words()
        if not self.words:
            self.word_label.config(text="No words left!")
            self.sentence_label.config(text="")
            self.progress_label.config(text="")
            return
        self.index = self.index % len(self.words)
        self.update_card()

    def goto_card_dialog(self):
        if not self.words:
            return
        num = simpledialog.askinteger("Go to Card", f"Enter card number (1-{len(self.words)}):")
        if num is None:
            return
        if 1 <= num <= len(self.words):
            self.index = num - 1
            self.update_card()
        else:
            messagebox.showinfo("Invalid", "Card number out of range.")

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        bg = "#23272e" if self.dark_mode else "#ffe6f7"
        fg = "#fff" if self.dark_mode else "#d72660"
        self.root.configure(bg=bg)
        # Recursively update all widgets' bg/fg
        def update_widget_colors(widget):
            try:
                widget.configure(bg=bg)
            except:
                pass
            try:
                widget.configure(fg=fg)
            except:
                pass
            for child in widget.winfo_children():
                update_widget_colors(child)
        update_widget_colors(self.root)
        self.update_card()

    def show_stats(self):
        total = len(self.words) + len(self.known_words)
        seen = len(self.cards_seen)
        known = len(self.known_words)
        unknown = len(self.words)
        msg = (
            f"Session Stats:\n"
            f"  Total cards: {total}\n"
            f"  Seen: {seen}\n"
            f"  Known: {known}\n"
            f"  Unknown: {unknown}\n"
        )
        messagebox.showinfo("Session Stats", msg)

    def toggle_starred(self):
        if not self.words:
            return
        word = self.words[self.index]["english"]
        if word in self.starred:
            self.starred.remove(word)
        else:
            self.starred.add(word)
        self.update_card()

    def toggle_review_starred(self):
        self.review_starred_only = not self.review_starred_only
        if self.review_starred_only:
            self.filtered_words = [w for w in self.words if w["english"] in self.starred]
            if not self.filtered_words:
                messagebox.showinfo("No Starred", "No starred words to review.")
                self.review_starred_only = False
                return
            self.words, self._all_words = self.filtered_words, self.words
            self.index = 0
        else:
            if hasattr(self, "_all_words"):
                self.words = self._all_words
                del self._all_words
            self.index = 0
        self.update_card()

    def random_card(self):
        if not self.words:
            return
        self.index = random.randint(0, len(self.words) - 1)
        self.update_card()

    def copy_word(self):
        if not self.words:
            return
        word = self.words[self.index]
        text = f"{word['english']} - {word['hebrew']}"
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copied", f"Copied: {text}")

    def toggle_sentence(self):
        self.show_sentence = not self.show_sentence
        self.update_card()

    def increase_font(self):
        self.font_size = min(self.font_size + 4, 80)
        self.update_card()

    def decrease_font(self):
        self.font_size = max(self.font_size - 4, 16)
        self.update_card()

    def update_timer(self):
        if self.session_start_time:
            elapsed = int(self._now() - self.session_start_time)
            mins, secs = divmod(elapsed, 60)
            self.timer_label.config(text=f"Session Time: {mins:02d}:{secs:02d}")
        self.root.after(1000, self.update_timer)

    def _now(self):
        import time
        return time.time()

if __name__ == "__main__":
    root = tk.Tk()
    app = FlashcardApp(root)
    root.mainloop()
