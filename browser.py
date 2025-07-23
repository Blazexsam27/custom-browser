import tkinter
import tkinter.font
import platform
from config.constants import *
from ui.layout import Layout
from core.parser import HTMLParser


class Browser:

    def __init__(self):
        self.scroll = 0
        self.window = tkinter.Tk()
        self.bi_times = tkinter.font.Font(family="Times", size=16, weight="bold")
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

    def canvas_resize(self, e):
        self.width = e.width
        self.height = e.height

        self.display_list = Layout(self.nodes, self.width).display_list
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
        # self.canvas.create_image(0, 0, image=self.img, anchor="nw")
        if not hasattr(self, "height") or not hasattr(self, "width"):
            self.width = self.canvas.winfo_width()
            self.height = self.canvas.winfo_height()
        for x, y, c, font in self.display_list:
            if y > self.scroll + self.height:
                continue
            if y + VSTEP < self.scroll:
                continue

            self.canvas.create_text(x, y - self.scroll, text=c, font=font, anchor="nw")

    def load(self, url):
        body = url.request()

        if not hasattr(self, "width"):
            self.width = self.canvas.winfo_width()

        self.nodes = HTMLParser(body).parse()
        print("Nodes ====>>", self.nodes)
        self.display_list = Layout(self.nodes, self.width).display_list
        self.draw()
