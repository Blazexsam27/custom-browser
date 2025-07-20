import tkinter
import platform

HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100


class Browser:

    def __init__(self):
        self.scroll = 0
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window)
        self.canvas.pack(fill="both", expand=True)

        self.window.bind("<Down>", self.scroll_down)
        self.window.bind("<Up>", self.scroll_up)
        self.window.bind("<Configure>", self.canvas_resize)

        system = platform.system()
        if system == "Windows":
            self.window.bind("<MouseWheel>", self.scroll_by_mousewheel)
        elif system == "Darwin":
            self.window.bind("<MouseWheel>", self.scroll_by_mousewheel_mac)
        else:
            self.window.bind("<Button-4>", self.scroll_up)
            self.window.bind("<Button-5>", self.scroll_down)

        self.canvas.pack()

    def canvas_resize(self, e):
        self.width = e.width
        self.height = e.height
        self.display_list = layout(self.text, self.width)
        self.draw()

    def scroll_by_mousewheel_mac(self, e):
        if e.delta > 0:
            self.scroll_down(e)
        else:
            self.scroll_up(e)

    def scroll_by_mousewheel(self, e):
        if e.delta > 0:
            self.scroll_up(e)
        else:
            self.scroll_down(e)

    def scroll_down(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

    def scroll_up(self, e):
        self.scroll = max(self.scroll - SCROLL_STEP, 0)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        if not hasattr(self, "height") or not hasattr(self, "width"):
            self.width = self.canvas.winfo_width()
            self.height = self.canvas.winfo_height()

        for x, y, c in self.display_list:
            if y > self.scroll + self.height:
                continue
            if y + VSTEP < self.scroll:
                continue

            self.canvas.create_text(x, y - self.scroll, text=c)

    def lex(self, body):
        text = ""
        in_tag = False
        for c in body:
            if c == "<":
                in_tag = True
            elif c == ">":
                in_tag = False
            elif not in_tag:
                text += c
        return text

    def load(self, url):
        body = url.request()
        self.text = self.lex(body)

        self.display_list = layout(self.text, 800)
        self.draw()


def layout(text, width):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP

    for c in text:
        if c == "\n":
            cursor_x = HSTEP
            cursor_y += VSTEP
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP

        if cursor_x >= width - HSTEP:
            cursor_x = HSTEP
            cursor_y += VSTEP
    return display_list
