from tkinter import *
import threading
import time
from chat import get_response, bot_name

BG_COLOR = "#17202A"
TEXT_COLOR = "#EAECEE"
BG_GRAY = "#ABB2B9"
FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"

class ChatApplication:
    def __init__(self):
        self.window = Tk()
        self._setup_main_window()

    def run(self):
        self.window.mainloop()

    def _setup_main_window(self):
        self.window.title("AI Chatbot")
        self.window.resizable(width=False, height=False)
        self.window.configure(width=470, height=550, bg=BG_COLOR)

        head_label = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                           text="AI Chatbot Assistant", font=FONT_BOLD, pady=10)
        head_label.place(relwidth=1)

        line = Label(self.window, width=450, bg=BG_GRAY)
        line.place(relwidth=1, rely=0.07, relheight=0.012)

        self.text_widget = Text(self.window, width=20, height=2,
                                bg=BG_COLOR, fg=TEXT_COLOR, font=FONT,
                                padx=5, pady=5, cursor="arrow", state=DISABLED)
        self.text_widget.place(relheight=0.745, relwidth=1, rely=0.08)

        scrollbar = Scrollbar(self.window)
        scrollbar.place(relheight=0.745, relx=0.974, rely=0.08)
        self.text_widget.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.text_widget.yview)

        bottom_label = Label(self.window, bg=BG_GRAY, height=80)
        bottom_label.place(relwidth=1, rely=0.825)

        self.msg_entry = Entry(bottom_label, bg="#2C3E50", fg=TEXT_COLOR, font=FONT)
        self.msg_entry.place(relwidth=0.74, relheight=0.06, rely=0.008, relx=0.011)
        self.msg_entry.focus()
        self.msg_entry.bind("<Return>", self._on_enter_pressed)

        send_button = Button(bottom_label, text="Send", font=FONT_BOLD,
                             bg=BG_GRAY, command=lambda: self._on_enter_pressed(None))
        send_button.place(relx=0.77, rely=0.008, relheight=0.06, relwidth=0.22)

    def _on_enter_pressed(self, event):
        msg = self.msg_entry.get()
        if msg.strip() == "":
            return
        self.msg_entry.delete(0, END)
        self._insert_message(f"You: {msg}\n\n")
        self._insert_message(f"{bot_name} is typing...\n\n")
        threading.Thread(target=self._bot_response, args=(msg,), daemon=True).start()

    def _insert_message(self, msg):
        self.text_widget.configure(state=NORMAL)
        self.text_widget.insert(END, msg)
        self.text_widget.configure(state=DISABLED)
        self.text_widget.see(END)

    def _bot_response(self, msg):
        time.sleep(0.5)
        response = get_response(msg)
        self.window.after(0, lambda: self._update_response(response))

    def _update_response(self, response):
        content = self.text_widget.get("1.0", END)
        content = content.replace(f"{bot_name} is typing...\n\n", "")
        self.text_widget.configure(state=NORMAL)
        self.text_widget.delete("1.0", END)
        self.text_widget.insert(END, content + f"{bot_name}: {response}\n\n")
        self.text_widget.configure(state=DISABLED)
        self.text_widget.see(END)

if __name__ == "__main__":
    app = ChatApplication()
    app.run()