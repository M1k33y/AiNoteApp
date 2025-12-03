import tkinter as tk
from tkinter import ttk, messagebox
from theme import apply_modern_dark_theme
from modern_widgets import RoundedButton
from db import (
    get_topics, create_topic, update_topic, delete_topic,
    get_notes_by_topic, create_note, update_note, delete_note,
    init_db
)

class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Notes Manager")
        self.root.geometry("1200x750")
        self.root.minsize(1100, 700)

        self.colors = apply_modern_dark_theme(self.root)

        self.selected_topic_id = None
        self.selected_note_id = None

        self.build_layout()
        self.load_topics()

    # ============================================================
    # UI LAYOUT
    # ============================================================
    def build_layout(self):

        # ------------------ SIDEBAR ------------------
        self.sidebar = ttk.Frame(self.root, width=250, style="Sidebar.TFrame")
        self.sidebar.pack(side="left", fill="y")

        ttk.Label(self.sidebar,
                  text="Topics",
                  font=("Segoe UI", 15, "bold"),
                  foreground=self.colors["accent"],
                  background=self.colors["bg_sidebar"]
                  ).pack(pady=15)

        self.topic_list = tk.Listbox(
            self.sidebar,
            bg=self.colors["bg_sidebar"],
            fg=self.colors["fg_text"],
            selectbackground=self.colors["select_bg"],
            highlightthickness=0,
            relief="flat",
            bd=0,
            font=("Segoe UI", 10)
        )
        self.topic_list.pack(fill="both", expand=True, padx=10)
        self.topic_list.bind("<<ListboxSelect>>", self.on_topic_select)

        RoundedButton(self.sidebar, text="Add Topic",
                      bg_color=self.colors["accent"],
                      fg_color="#1E1E2E",
                      parent_bg=self.colors["bg_sidebar"],
                      command=self.add_topic).pack(pady=5)

        RoundedButton(self.sidebar, text="Edit Topic",
                      bg_color=self.colors["accent"],
                      fg_color="#1E1E2E",
                      parent_bg=self.colors["bg_sidebar"],
                      command=self.edit_topic).pack(pady=5)

        RoundedButton(self.sidebar, text="Delete Topic",
                      bg_color="#F38BA8",
                      fg_color="#1E1E2E",
                      parent_bg=self.colors["bg_sidebar"],
                      command=self.delete_topic_action).pack(pady=5)

        # ------------------ MAIN PANEL ------------------
        self.main = ttk.Frame(self.root, style="Main.TFrame")
        self.main.pack(side="right", fill="both", expand=True)

        # SEARCH BAR
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.filter_notes())

        ttk.Label(self.main, text="Search Notes:", style="Header.TLabel").pack(
            anchor="w", padx=10, pady=5
        )

        self.search_entry = ttk.Entry(self.main, textvariable=self.search_var, width=50)
        self.search_entry.pack(anchor="w", padx=10, pady=2)

        # NOTES LIST
        self.notes_list = tk.Listbox(
            self.main,
            bg=self.colors["bg_card"],
            fg=self.colors["fg_text"],
            selectbackground=self.colors["select_bg"],
            highlightthickness=0,
            relief="flat",
            bd=0,
            height=8,
            font=("Segoe UI", 10)
        )
        self.notes_list.pack(fill="x", padx=10, pady=8)
        self.notes_list.bind("<<ListboxSelect>>", self.on_note_select)

        # TITLE
        ttk.Label(self.main, text="Title:", style="Header.TLabel").pack(
            anchor="w", padx=10
        )

        self.note_title = ttk.Entry(self.main, width=50, font=("Segoe UI", 10))
        self.note_title.pack(anchor="w", padx=10, pady=5)

        # CONTENT
        ttk.Label(self.main, text="Content:", style="Header.TLabel").pack(
            anchor="w", padx=10, pady=(5, 0)
        )

        self.note_content = tk.Text(
            self.main,
            bg=self.colors["bg_card"],
            fg=self.colors["fg_text"],
            insertbackground=self.colors["accent"],
            relief="flat",
            bd=2,
            highlightbackground=self.colors["border"],
            highlightcolor=self.colors["accent"],
            wrap=tk.WORD,
            font=("Segoe UI", 10)
        )
        self.note_content.pack(fill="both", expand=True, padx=10, pady=8)

        # ------------------ BOTTOM BUTTONS ------------------
        button_frame = ttk.Frame(self.main, style="Main.TFrame")
        button_frame.pack(fill="x", pady=2)

        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        RoundedButton(button_frame, text="Add Note",
                      bg_color=self.colors["accent"],
                      fg_color="#1E1E2E",
                      parent_bg=self.colors["bg_main"],
                      command=self.add_note).grid(row=0, column=0, padx=5, sticky="ew")

        RoundedButton(button_frame, text="Save Changes",
                      bg_color="#A6E3A1",
                      fg_color="#1E1E2E",
                      parent_bg=self.colors["bg_main"],
                      command=self.save_note).grid(row=0, column=1, padx=5, sticky="ew")

        RoundedButton(button_frame, text="Delete Note",
                      bg_color="#F38BA8",
                      fg_color="#1E1E2E",
                      parent_bg=self.colors["bg_main"],
                      command=self.delete_note_action).grid(row=0, column=2, padx=5, sticky="ew")

    # ============================================================
    # TOPICS
    # ============================================================
    def load_topics(self):
        self.topic_list.delete(0, tk.END)
        self.topics = list(get_topics())

        for t in self.topics:
            self.topic_list.insert(tk.END, t['name'])

    def add_topic(self):
        name = simple_input("Add Topic", "Topic name:")
        if not name:
            return
        desc = simple_input("Add Topic", "Description:")
        create_topic(name, desc)
        self.load_topics()

    def edit_topic(self):
        if self.selected_topic_id is None:
            return

        topic = self.topics[self.topic_list.curselection()[0]]

        new_name = simple_input("Edit Topic", "New name:", topic["name"])
        new_desc = simple_input("Edit Topic", "New description:", topic["description"])

        update_topic(topic["id"], new_name, new_desc)
        self.load_topics()

    def delete_topic_action(self):
        if self.selected_topic_id is None:
            return

        if messagebox.askyesno("Confirm", "Delete topic and all its notes?"):
            delete_topic(self.selected_topic_id)
            self.selected_topic_id = None
            self.load_topics()
            self.notes_list.delete(0, tk.END)

    def on_topic_select(self, event):
        if not self.topic_list.curselection():
            return

        idx = self.topic_list.curselection()[0]
        self.selected_topic_id = self.topics[idx]["id"]

        self.load_notes()

    # ============================================================
    # NOTES
    # ============================================================
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
        if self.selected_topic_id is None:
            return
        create_note(self.selected_topic_id, "New Note", "")
        self.load_notes()

    def save_note(self):
        if self.selected_note_id is None:
            return

        title = self.note_title.get()
        content = self.note_content.get("1.0", tk.END).strip()

        update_note(self.selected_note_id, title, content)
        self.load_notes()

    def delete_note_action(self):
        if self.selected_note_id is None:
            return

        delete_note(self.selected_note_id)

        self.selected_note_id = None
        self.load_notes()

        self.note_title.delete(0, tk.END)
        self.note_content.delete("1.0", tk.END)

# ============================================================
# POPUP INPUT
# ============================================================
def simple_output(msg):
    messagebox.showinfo("Info", msg)

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
