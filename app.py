import tkinter as tk
from tkinter import ttk, messagebox
from theme import apply_modern_dark_theme
from modern_widgets import RoundedButton
from ai_tutor import ask_tutor
from settings import load_settings
from ai_tutor import load_chat_history
from db import (
    get_topics, create_topic, update_topic, delete_topic,
    get_notes_by_topic, create_note, update_note, delete_note,
    init_db
)


class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Notes Manager")
        self.root.geometry("1450x850")
        self.root.minsize(1200, 700)

        self.colors = apply_modern_dark_theme(self.root)

        self.typing_animation_running = False
        self.typing_animation_job = None

        self.selected_topic_id = None
        self.selected_note_id = None

        self.build_layout()
        self.load_topics()
        self.settings_window = None

    def save_settings(self, lang_var, depth_var, temp_var, max_tokens_var, win):
        from settings import save_settings

        new_settings = {
            "language": lang_var.get(),
            "depth": depth_var.get(),
            "temperature": float(temp_var.get()),
            "max_tokens": int(max_tokens_var.get()),
            "model": "gpt-4o-mini"
        }

        save_settings(new_settings)
        win.destroy()
        messagebox.showinfo("Settings", "Tutor settings saved!")


    def resize_chat_frame(self, event):
        """Ensure chat_frame matches chat_container width."""
        canvas_width = event.width
        self.chat_container.itemconfig(self.chat_window, width=canvas_width)

    def load_chat_ui(self):
        """Load saved conversation for the selected topic."""
        # clear UI chat bubbles
        for widget in self.chat_frame.winfo_children():
            widget.destroy()

        history = load_chat_history()
        tid = str(self.selected_topic_id)

        if tid not in history:
            return  # no messages yet

        for msg in history[tid]:
            role = msg["role"]
            content = msg["content"]

            if role == "user":
                self.add_bubble(f"👤 You:\n{content}", sender="user")
            else:
                self.add_bubble(f"🤖 Tutor:\n{content}", sender="assistant")

        self.chat_container.update_idletasks()
        self.chat_container.yview_moveto(1.0)

    def on_mousewheel(self, event):
        """Scroll chat on Windows & Mac."""
        # event.delta > 0 means scroll up
        self.chat_container.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def open_settings_window(self):
        if self.settings_window is not None and tk.Toplevel.winfo_exists(self.settings_window):
            self.settings_window.lift()
            return
        
        win = tk.Toplevel(self.root)
        win.title("Tutor Settings")
        win.geometry("400x400")
        win.configure(bg=self.colors["bg_main"])
        win.grab_set()

        settings = load_settings()

        # ---------------- Language ----------------
        ttk.Label(win, text="Preferred Language:", foreground=self.colors["fg_text"]).pack(pady=5)
        lang_var = tk.StringVar(value=settings.get("language", "RO"))
        ttk.OptionMenu(win, lang_var, lang_var.get(), "RO", "EN").pack()

        # ---------------- Answer Depth ----------------
        ttk.Label(win, text="Answer Depth:", foreground=self.colors["fg_text"]).pack(pady=5)
        depth_var = tk.StringVar(value=settings.get("depth", "medium"))
        ttk.OptionMenu(win, depth_var, depth_var.get(), "short", "medium", "detailed").pack()

        # ---------------- Temperature ----------------
        ttk.Label(win, text="Temperature:", foreground=self.colors["fg_text"]).pack(pady=5)
        temp_var = tk.DoubleVar(value=settings.get("temperature", 0.5))
        ttk.Scale(win, from_=0.0, to=1.0, orient="horizontal", variable=temp_var).pack(fill="x", padx=40)

        # ---------------- Max Tokens ----------------
        ttk.Label(win, text="Max Tokens:", foreground=self.colors["fg_text"]).pack(pady=5)
        max_tokens_var = tk.IntVar(value=settings.get("max_tokens", 300))
        tk.Entry(win, textvariable=max_tokens_var, width=10).pack()

        # ---------------- Save Button ----------------
        RoundedButton(
            win,
            text="Save Settings",
            bg_color="#A6E3A1",
            fg_color="#1E1E2E",
            parent_bg=self.colors["bg_main"],
            command=lambda: self.save_settings(lang_var, depth_var, temp_var, max_tokens_var, win)
        ).pack(pady=20)



    # ============================================================
    # BUILD LAYOUT
    # ============================================================
    def build_layout(self):

        # ------------------ SIDEBAR ------------------
        self.sidebar = ttk.Frame(self.root, width=250, style="Sidebar.TFrame")
        self.sidebar.pack(side="left", fill="y")

        ttk.Label(self.sidebar, text="Topics",
                  font=("Segoe UI", 15, "bold"),
                  foreground=self.colors["accent"],
                  background=self.colors["bg_sidebar"]).pack(pady=15)

        self.topic_list = tk.Listbox(
            self.sidebar,
            bg=self.colors["bg_sidebar"],
            fg=self.colors["fg_text"],
            selectbackground=self.colors["select_bg"],
            highlightthickness=0,
            relief="flat",
            bd=0,
            font=("Segoe UI", 11)
        )
        self.topic_list.pack(fill="both", expand=True, padx=10)
        self.topic_list.bind("<<ListboxSelect>>", self.on_topic_select)

        RoundedButton(self.sidebar, text="Add Topic",
                      bg_color=self.colors["accent"], fg_color="#1E1E2E",
                      parent_bg=self.colors["bg_sidebar"],
                      command=self.add_topic).pack(pady=5)

        RoundedButton(self.sidebar, text="Edit Topic",
                      bg_color=self.colors["accent"], fg_color="#1E1E2E",
                      parent_bg=self.colors["bg_sidebar"],
                      command=self.edit_topic).pack(pady=5)

        RoundedButton(self.sidebar, text="Delete Topic",
                      bg_color="#F38BA8", fg_color="#1E1E2E",
                      parent_bg=self.colors["bg_sidebar"],
                      command=self.delete_topic_action).pack(pady=5)
        RoundedButton(
            self.sidebar, text="Settings",
            bg_color="#89B4FA",
            fg_color="#1E1E2E",
            parent_bg=self.colors["bg_sidebar"],
            command=self.open_settings_window
        ).pack(pady=20)

        # ------------------ NOTES PANEL ------------------
        self.main = ttk.Frame(self.root, style="Main.TFrame")
        self.main.pack(side="left", fill="both", expand=True)

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.filter_notes())

        ttk.Label(self.main, text="Search Notes:", style="Header.TLabel").pack(
            anchor="w", padx=10, pady=5
        )

        self.search_entry = ttk.Entry(self.main, textvariable=self.search_var, width=50)
        self.search_entry.pack(anchor="w", padx=10, pady=2)

        self.notes_list = tk.Listbox(
            self.main,
            bg=self.colors["bg_card"],
            fg=self.colors["fg_text"],
            selectbackground=self.colors["select_bg"],
            highlightthickness=0,
            relief="flat",
            bd=0,
            height=8,
            font=("Segoe UI", 11)
        )
        self.notes_list.pack(fill="x", padx=10, pady=8)
        self.notes_list.bind("<<ListboxSelect>>", self.on_note_select)

        ttk.Label(self.main, text="Title:", style="Header.TLabel").pack(anchor="w", padx=10)

        self.note_title = ttk.Entry(self.main, width=50)
        self.note_title.pack(anchor="w", padx=10, pady=5)

        ttk.Label(self.main, text="Content:", style="Header.TLabel").pack(anchor="w", padx=10)

        self.note_content = tk.Text(
            self.main,
            bg=self.colors["bg_card"],
            fg=self.colors["fg_text"],
            insertbackground=self.colors["accent"],
            wrap=tk.WORD,
            relief="flat",
            bd=2,
            highlightbackground=self.colors["border"],
            highlightcolor=self.colors["accent"],
            font=("Segoe UI", 11)
        )
        self.note_content.pack(fill="both", expand=True, padx=10, pady=8)

        bottom_buttons = ttk.Frame(self.main, style="Main.TFrame")
        bottom_buttons.pack(fill="x", pady=2)

        bottom_buttons.columnconfigure(0, weight=1)
        bottom_buttons.columnconfigure(1, weight=1)
        bottom_buttons.columnconfigure(2, weight=1)

        RoundedButton(bottom_buttons, text="Add Note",
                      bg_color=self.colors["accent"], fg_color="#1E1E2E",
                      parent_bg=self.colors["bg_main"],
                      command=self.add_note).grid(row=0, column=0, padx=5, sticky="ew")

        RoundedButton(bottom_buttons, text="Save Changes",
                      bg_color="#A6E3A1", fg_color="#1E1E2E",
                      parent_bg=self.colors["bg_main"],
                      command=self.save_note).grid(row=0, column=1, padx=5, sticky="ew")

        RoundedButton(bottom_buttons, text="Delete Note",
                      bg_color="#F38BA8", fg_color="#1E1E2E",
                      parent_bg=self.colors["bg_main"],
                      command=self.delete_note_action).grid(row=0, column=2, padx=5, sticky="ew")
        


        # ============================================================
        # AI TUTOR PANEL (with bubbles)
        # ============================================================
        self.tutor_frame = ttk.Frame(self.root, style="Main.TFrame")
        self.tutor_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)


        ttk.Label(self.tutor_frame, text="AI Tutor:", style="Header.TLabel").pack(anchor="w")

        # Scrollable chat area
        self.chat_container = tk.Canvas(
            self.tutor_frame,
            bg=self.colors["bg_card"],
            highlightthickness=0
        )
        self.chat_container.pack(fill="both", expand=True, padx=5, pady=5)
        self.chat_container.bind_all("<MouseWheel>", self.on_mousewheel)
        self.chat_container.bind("<Enter>", lambda e: self.chat_container.focus_set())

        self.chat_scroll = ttk.Scrollbar(self.tutor_frame, orient="vertical", command=self.chat_container.yview)
        self.chat_scroll.pack(side="right", fill="y")

        self.chat_container.configure(yscrollcommand=self.chat_scroll.set)

        self.chat_frame = tk.Frame(self.chat_container, bg=self.colors["bg_card"])
        self.chat_window = self.chat_container.create_window(
        (0, 0),
        window=self.chat_frame,
        anchor="nw"
        )

        self.chat_frame.bind("<Configure>", lambda e: 
                             self.chat_container.configure(scrollregion=self.chat_container.bbox("all")))
        self.chat_container.bind("<Configure>", self.resize_chat_frame)

        # Input field + Send
        self.tutor_input = ttk.Entry(self.tutor_frame, width=80)
        self.tutor_input.pack(anchor="w", padx=5, pady=3)

        self.tutor_input.bind("<Return>", self.ask_tutor_enter)

        RoundedButton(self.tutor_frame, text="Ask Tutor",
                      bg_color=self.colors["accent"], fg_color="#1E1E2E",
                      parent_bg=self.colors["bg_main"],
                      command=self.ask_tutor_action).pack(pady=5)


    # ============================================================
    # CHAT BUBBLE UTILITIES
    # ============================================================
    def add_bubble(self, text, sender="user"):
        """Create a chat bubble aligned left or right."""

        # Each message gets its own ROW FRAME to avoid stretching.
        row = tk.Frame(self.chat_frame, bg=self.colors["bg_card"])
        row.pack(fill="x", pady=3)

        # Decide style based on sender
        if sender == "user":
            bubble_color = "#2e384d"
            fg = self.colors["accent"]
            side = "right"
            padx = (50, 10)
        else:
            bubble_color = "#374152"
            fg = "#A6E3A1"
            side = "left"
            padx = (10, 50)

        # bubble itself (shrink to text)
        bubble = tk.Frame(
            row,
            bg=bubble_color,
            padx=12,
            pady=8
        )

        tk.Label(
            bubble,
            text=text,
            fg=fg,
            bg=bubble_color,
            justify="left",
            wraplength=450,
            font=("Segoe UI", 10)
        ).pack()

        # PACK bubble aligned properly inside row
        if side == "right":
            bubble.pack(anchor="e", padx=padx)
        else:
            bubble.pack(anchor="w", padx=padx)

        # update scroll
        self.chat_container.update_idletasks()
        self.chat_container.yview_moveto(1.0)



    # ============================================================
    # TYPING ANIMATION
    # ============================================================
    def start_typing_animation(self):
        self.typing_animation_running = True
        self.typing_dots = 0

        # create placeholder bubble
        self.typing_bubble = tk.Label(
            self.chat_frame,
            text="🤖 Tutor is typing",
            fg="#A6E3A1",
            bg=self.colors["bg_card"],
            font=("Segoe UI", 10),
            anchor="w"
        )
        self.typing_bubble.pack(anchor="w", pady=3)

        self.update_typing_animation()

    def update_typing_animation(self):
        if not self.typing_animation_running:
            return

        dots = "." * (self.typing_dots % 4)
        self.typing_dots += 1

        self.typing_bubble.config(text=f"🤖 Tutor is typing{dots}")

        self.typing_animation_job = self.root.after(500, self.update_typing_animation)

    def stop_typing_animation(self):
        if self.typing_animation_job:
            self.root.after_cancel(self.typing_animation_job)

        if hasattr(self, "typing_bubble"):
            self.typing_bubble.destroy()

        self.typing_animation_running = False


    # ============================================================
    # ASK TUTOR
    # ============================================================
    def ask_tutor_action(self):
        if not self.selected_topic_id:
            messagebox.showerror("Error", "Select a topic first.")
            return

        question = self.tutor_input.get().strip()
        if not question:
            return

        # display user bubble
        self.add_bubble(f"👤 You:\n{question}", sender="user")

        # start typing animation
        self.start_typing_animation()

        # get context
        topic = next(t for t in self.topics if t["id"] == self.selected_topic_id)
        note_titles = [n["title"] for n in self.notes]

        selected_content = ""
        if self.notes_list.curselection():
            idx = self.notes_list.curselection()[0]
            selected_content = self.notes[idx]["content"]

        settings = load_settings()

        # query AI
        answer = ask_tutor(
            topic_id=self.selected_topic_id,
            topic_name=topic["name"],
            topic_desc=topic["description"],
            note_titles=note_titles,
            selected_note_content=selected_content,
            question=question,
            settings=settings
        )

        # stop animation
        self.stop_typing_animation()

        # show answer bubble
        self.add_bubble(f"🤖 Tutor:\n{answer}", sender="assistant")

        self.tutor_input.delete(0, tk.END)

    def ask_tutor_enter(self, event):
        self.ask_tutor_action()
        return "break"


    # ============================================================
    # TOPICS + NOTES LOGIC
    # ============================================================
    def load_topics(self):
        self.topic_list.delete(0, tk.END)
        self.topics = list(get_topics())
        for t in self.topics:
            self.topic_list.insert(tk.END, t["name"])

    def add_topic(self):
        name = simple_input("Add Topic", "Topic name:")
        if not name:
            return
        desc = simple_input("Add Topic", "Description:")
        create_topic(name, desc)
        self.load_topics()

    def edit_topic(self):
        if not self.topic_list.curselection():
            return
        idx = self.topic_list.curselection()[0]
        topic = self.topics[idx]
        new_name = simple_input("Edit Topic", "New name:", topic["name"])
        new_desc = simple_input("Edit Topic", "New description:", topic["description"])
        update_topic(topic["id"], new_name, new_desc)
        self.load_topics()

    def delete_topic_action(self):
        if not self.topic_list.curselection():
            return
        if messagebox.askyesno("Confirm", "Delete topic and all its notes?"):
            idx = self.topic_list.curselection()[0]
            delete_topic(self.topics[idx]["id"])
            self.selected_topic_id = None
            self.load_topics()
            self.notes_list.delete(0, tk.END)

    def on_topic_select(self, event):
        if not self.topic_list.curselection():
            return
        idx = self.topic_list.curselection()[0]
        self.selected_topic_id = self.topics[idx]["id"]
        self.load_notes()
        self.load_chat_ui()

    def load_notes(self):
        self.notes = list(get_notes_by_topic(self.selected_topic_id))
        self.render_notes(self.notes)

    def render_notes(self, notes):
        self.notes_list.delete(0, tk.END)
        for n in notes:
            self.notes_list.insert(tk.END, n["title"])

    def filter_notes(self):
        text = self.search_var.get().lower()
        filtered = [n for n in self.notes if text in n["title"].lower()]
        self.render_notes(filtered)

    def on_note_select(self, event):
        if not self.notes_list.curselection():
            return
        idx = self.notes_list.curselection()[0]
        note = self.notes[idx]
        self.selected_note_id = note["id"]
        self.note_title.delete(0, tk.END)
        self.note_title.insert(0, note["title"])
        self.note_content.delete("1.0", tk.END)
        self.note_content.insert("1.0", note["content"])

    def add_note(self):
        if not self.selected_topic_id:
            return
        create_note(self.selected_topic_id, "New Note", "")
        self.load_notes()

    def save_note(self):
        if not self.selected_note_id:
            return
        title = self.note_title.get()
        content = self.note_content.get("1.0", tk.END).strip()
        update_note(self.selected_note_id, title, content)
        self.load_notes()

    def delete_note_action(self):
        if not self.selected_note_id:
            return
        delete_note(self.selected_note_id)
        self.selected_note_id = None
        self.load_notes()
        self.note_title.delete(0, tk.END)
        self.note_content.delete("1.0", tk.END)


# ============================================================
# POPUP INPUT
# ============================================================
def simple_input(title, prompt, default=""):
    win = tk.Toplevel()
    win.title(title)
    win.geometry("350x160")
    win.configure(bg="#1E1E2E")
    win.grab_set()

    ttk.Label(win, text=prompt).pack(pady=10)

    entry = ttk.Entry(win)
    entry.insert(0, default)
    entry.pack(pady=5)

    val = {"value": None}

    def ok():
        val["value"] = entry.get()
        win.destroy()

    ttk.Button(win, text="OK", command=ok).pack(pady=10)
    win.wait_window()

    return val["value"]


# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    NotesApp(root)
    root.mainloop()
