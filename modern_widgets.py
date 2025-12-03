
import tkinter as tk

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text="", radius=12, padding=10,
                 bg_color="#89B4FA", fg_color="#1E1E2E",
                 command=None, font=("Segoe UI", 10),
                 parent_bg="#1E1E2E"):
        
        self.width = 150
        self.height = 40
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.command = command

        super().__init__(parent,
                         width=self.width,
                         height=self.height,
                         bg=parent_bg,
                         bd=0,
                         highlightthickness=0)

        self.rounded_rect = self.create_round_rect(
            2, 2, self.width - 2, self.height - 2,
            radius=radius,
            fill=bg_color,
            outline=""
        )

        self.label = self.create_text(
            self.width // 2,
            self.height // 2,
            text=text,
            fill=fg_color,
            font=font
        )

        # CLICK
        self.bind("<Button-1>", self.on_click)
        self.tag_bind(self.label, "<Button-1>", self.on_click)

        # HOVER effect
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        self.tag_bind(self.label, "<Enter>", self.on_hover)
        self.tag_bind(self.label, "<Leave>", self.on_leave)

        # PRESS effect
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.tag_bind(self.label, "<ButtonPress-1>", self.on_press)
        self.tag_bind(self.label, "<ButtonRelease-1>", self.on_release)

    def create_round_rect(self, x1, y1, x2, y2, radius=12, **kwargs):
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, splinesteps=36, **kwargs)

    def on_hover(self, event):
        self.itemconfig(self.rounded_rect, fill="#B4BEFE")

    def on_leave(self, event):
        self.itemconfig(self.rounded_rect, fill=self.bg_color)

    def on_press(self, event):
        self.itemconfig(self.rounded_rect, fill="#A5B2FF")

    def on_release(self, event):
        self.itemconfig(self.rounded_rect, fill=self.bg_color)
        if self.command:
            self.command()

    def on_click(self, event):
        if self.command:
            self.command()
