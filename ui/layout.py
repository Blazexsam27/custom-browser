from config.constants import *
import tkinter
from ui.text import Text
from ui.element import Element


class Layout:
    def __init__(self, tokens, width):
        self.display_list = []
        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.weight = "normal"
        self.style = "roman"
        self.width = width
        self.size = 12
        self.line = []
        self.centered = False
        self.supscript = False

        self.recurse(tokens)
        self.flush()

    def recurse(self, tree):
        if isinstance(tree, Text):
            for word in tree.text.split():
                self.word(word)

        else:
            self.open_tag(tree.tag)
            for child in tree.children:
                self.recurse(child)
            self.close_tag(tree.tag)

    def open_tag(self, tag):
        if tag == "i":
            self.style = "italic"
        elif tag == "b":
            self.weight = "bold"
        elif tag == "small":
            self.size -= 2
        elif tag == "big":
            self.size += 4
        elif tag.startswith("h1"):
            tag_name, attrs = Element.parse_tag(tag)
            if tag_name == "h1":
                self.flush()
                self.size += 12
                self.weight = "bold"
                self.centered = attrs.get("class") == "title"
        elif tag == "br":
            self.flush()
        elif tag == "sup":
            self.size -= 4
            self.supscript = True
            self.flush()

    def close_tag(self, tag):
        if tag == "/i":
            self.style = "roman"
        elif tag == "/b":
            self.weight = "normal"
        elif tag == "/small":
            self.size += 2
        elif tag == "/big":
            self.size -= 4
        elif tag == "/h1":
            self.flush()
            self.size -= 12
            self.weight = "normal"
            self.centered = False
            self.cursor_y += VSTEP

        elif tag == "br":
            self.flush()
        elif tag == "/p":
            self.flush()
            self.cursor_y += VSTEP
        elif tag == "/sup":
            self.size += 4
            self.supscript = False
            self.flush()

    def word(self, word) -> None:
        font = get_font(self.size, self.weight, self.style)
        w_width = font.measure(word)

        if self.cursor_x + w_width > self.width - HSTEP:
            self.flush()
            self.cursor_x = HSTEP
            self.cursor_y += font.metrics("linespace") * 1.25

        # self.display_list.append((self.cursor_x, self.cursor_y, word, font))
        self.line.append((self.cursor_x, word, font))
        self.cursor_x += w_width + font.measure(" ")

    def flush(self):
        if not self.line:
            return
        metrics = [font.metrics() for x, word, font in self.line]
        max_ascent = max(metric["ascent"] for metric in metrics)

        baseline = self.cursor_y + 1.25 * max_ascent
        total_width = 0
        for _, word, font in self.line:
            total_width += font.measure(word) + font.measure(" ")
        total_width -= font.measure(" ")

        if self.centered:
            start_x = (self.width - total_width) / 2
        else:
            start_x = HSTEP

        x = start_x
        for _, word, font in self.line:
            y = baseline - font.metrics("ascent")
            if self.supscript:
                y -= font.metrics("linespace") * 0.35

            self.display_list.append((x, y, word, font))
            x += font.measure(word) + font.measure(" ")
        max_descent = max(metric["descent"] for metric in metrics)
        self.cursor_y = baseline + max_descent * 1.25

        self.cursor_x = HSTEP
        self.line = []


def get_font(size, weight, style):
    key = (size, weight, style)
    if key not in FONTS:
        font = tkinter.font.Font(size=size, weight=weight, slant=style)
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)

    return FONTS[key][0]
