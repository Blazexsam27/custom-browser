from config.constants import *
import tkinter
from ui.text import Text


class Layout:
    def __init__(self, tokens, width):
        self.display_list = []
        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.weight = "normal"
        self.style = "roman"
        self.width = width

        for tok in tokens:
            self.token(tok)

    def token(self, tok) -> None:
        if isinstance(tok, Text):
            for word in tok.text.split():
                self.word(word)

        elif tok.tag == "i":
            self.style = "italic"
        elif tok.tag == "/i":
            self.style = "roman"
        elif tok.tag == "b":
            self.weight = "bold"
        elif tok.tag == "/b":
            self.weight = "normal"

    def word(self, word) -> None:
        font = tkinter.font.Font(size=16, weight=self.weight, slant=self.style)
        w_width = font.measure(word)
        if self.cursor_x + w_width >= self.width - HSTEP:
            self.cursor_x = HSTEP
            self.cursor_y += font.metrics("linespace") * 1.25

        self.display_list.append((self.cursor_x, self.cursor_y, word, font))
        self.cursor_x += w_width + font.measure(" ")
