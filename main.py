import ast
import math
import os
import re

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse, Line


# Use a system monospace font when it exists; otherwise use Kivy's safe default.
def find_tech_font():
    candidates = (
        "/system/fonts/RobotoMono-Regular.ttf",
        "/system/fonts/monospace.ttf",
        "/system/fonts/DroidSansMono.ttf",
    )
    for font_path in candidates:
        if os.path.isfile(font_path):
            return font_path
    return "Roboto"


TECH_FONT = find_tech_font()
Window.clearcolor = (0.012, 0.004, 0.025, 1)


class GalaxyLayout(BoxLayout):
    """Static galaxy background; no timers or animation callbacks."""

    STAR_POINTS = (
        (0.08, 0.88, 2.0), (0.19, 0.78, 1.4), (0.31, 0.93, 1.6),
        (0.43, 0.82, 1.8), (0.57, 0.91, 1.5), (0.72, 0.84, 2.0),
        (0.89, 0.94, 1.6), (0.94, 0.70, 1.8), (0.12, 0.59, 1.5),
        (0.27, 0.50, 1.8), (0.76, 0.58, 1.4), (0.88, 0.43, 1.7),
        (0.06, 0.31, 1.7), (0.21, 0.21, 1.5), (0.39, 0.34, 1.8),
        (0.61, 0.25, 1.5), (0.81, 0.18, 1.8), (0.96, 0.09, 1.5),
        (0.48, 0.08, 1.4), (0.69, 0.43, 1.6), (0.35, 0.67, 1.4),
        (0.53, 0.55, 1.7), (0.15, 0.42, 1.5), (0.91, 0.83, 1.4),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.012, 0.004, 0.025, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)

            Color(0.55, 0.025, 0.38, 0.16)
            self.glow_pink = Ellipse()
            Color(0.20, 0.035, 0.55, 0.13)
            self.glow_purple = Ellipse()

            self.star_shapes = []
            for index, (nx, ny, radius) in enumerate(self.STAR_POINTS):
                alpha = 0.42 if index % 3 else 0.72
                Color(1.0, 0.48, 0.84, alpha)
                dot = Ellipse(size=(dp(radius), dp(radius)))
                self.star_shapes.append((dot, nx, ny, radius))

        self.bind(pos=self.update_background, size=self.update_background)
        self.update_background()

    def update_background(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.glow_pink.pos = (self.x - self.width * 0.08, self.y + self.height * 0.43)
        self.glow_pink.size = (self.width * 0.92, self.height * 0.58)
        self.glow_purple.pos = (self.x + self.width * 0.36, self.y + self.height * 0.08)
        self.glow_purple.size = (self.width * 0.76, self.height * 0.50)

        for dot, nx, ny, radius in self.star_shapes:
            diameter = dp(radius)
            dot.size = (diameter, diameter)
            dot.pos = (
                self.x + self.width * nx - diameter / 2,
                self.y + self.height * ny - diameter / 2,
            )


class NeonButton(Button):
    def __init__(self, **kwargs):
        self.kind = kwargs.pop("kind", "number")
        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.font_name = TECH_FONT
        self.font_size = sp(26)
        self.bold = True
        self.color = (1.0, 0.53, 0.86, 1)

        if self.kind == "equals":
            fill = (0.43, 0.035, 0.28, 1)
            border = (1.0, 0.36, 0.78, 1)
        elif self.kind == "operator":
            fill = (0.23, 0.035, 0.30, 1)
            border = (0.86, 0.30, 0.92, 0.95)
            self.color = (1.0, 0.78, 1.0, 1)
        elif self.kind == "action":
            fill = (0.19, 0.025, 0.20, 1)
            border = (0.90, 0.25, 0.67, 0.85)
            self.color = (1.0, 0.67, 0.88, 1)
        else:
            fill = (0.105, 0.018, 0.145, 0.98)
            border = (0.76, 0.19, 0.60, 0.75)

        self._normal_fill = fill
        self._normal_border = border

        with self.canvas.before:
            self.glow_color = Color(1.0, 0.10, 0.62, 0.16)
            self.glow_shape = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(23)]
            )
            self.fill_color = Color(*fill)
            self.fill_shape = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(20)]
            )

        with self.canvas.after:
            self.border_color = Color(*border)
            self.border_shape = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, dp(20)),
                width=1.15,
            )

        self.bind(pos=self.update_shapes, size=self.update_shapes)
        self.bind(on_press=self.show_pressed, on_release=self.show_released)
        self.update_shapes()

    def update_shapes(self, *args):
        self.glow_shape.pos = (self.x - dp(3), self.y - dp(3))
        self.glow_shape.size = (self.width + dp(6), self.height + dp(6))
        self.fill_shape.pos = self.pos
        self.fill_shape.size = self.size
        self.border_shape.rounded_rectangle = (
            self.x, self.y, self.width, self.height, dp(20)
        )

    def show_pressed(self, *args):
        self.fill_color.rgba = (0.48, 0.045, 0.31, 1)
        self.glow_color.rgba = (1.0, 0.12, 0.68, 0.38)
        self.border_color.rgba = (1.0, 0.62, 0.91, 1)

    def show_released(self, *args):
        self.fill_color.rgba = self._normal_fill
        self.glow_color.rgba = (1.0, 0.10, 0.62, 0.16)
        self.border_color.rgba = self._normal_border


class GlassDisplay(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = (dp(14), dp(10))
        self.spacing = dp(3)

        with self.canvas.before:
            Color(0.095, 0.018, 0.12, 0.92)
            self.panel = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(24)]
            )

        with self.canvas.after:
            Color(1.0, 0.20, 0.70, 0.88)
            self.border = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, dp(24)),
                width=1.25,
            )

        self.bind(pos=self.update_panel, size=self.update_panel)
        self.update_panel()

    def update_panel(self, *args):
        self.panel.pos = self.pos
        self.panel.size = self.size
        self.border.rounded_rectangle = (
            self.x, self.y, self.width, self.height, dp(24)
        )


def safe_calculate(expression):
    """Evaluate only numeric arithmetic; no names, calls, or Python builtins."""
    normalized = expression.replace("×", "*").replace("÷", "/").replace("−", "-")
    if not normalized or not re.fullmatch(r"[0-9+\-*/().\s]+", normalized):
        raise ValueError("Invalid expression")

    tree = ast.parse(normalized, mode="eval")
    binary_ops = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: a / b,
    }
    unary_ops = {
        ast.UAdd: lambda a: a,
        ast.USub: lambda a: -a,
    }

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in binary_ops:
            left = visit(node.left)
            right = visit(node.right)
            return binary_ops[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in unary_ops:
            return unary_ops[type(node.op)](visit(node.operand))
        raise ValueError("Unsupported expression")

    result = visit(tree)
    if not isinstance(result, (int, float)) or not math.isfinite(result):
        raise ValueError("Invalid result")
    return result


def number_text(number):
    if isinstance(number, int):
        return str(number)
    if abs(number) < 1e-12:
        number = 0.0
    return format(number, ".12g")


class MGTCalculator(App):
    def build(self):
        self.expression = ""
        self.just_evaluated = False

        root = GalaxyLayout(
            orientation="vertical",
            padding=dp(14),
            spacing=dp(10),
        )

        title = Label(
            text="[b]MGT[/b] [color=ff63c8]CALCULATOR[/color]",
            markup=True,
            font_name=TECH_FONT,
            font_size=sp(25),
            color=(1, 0.48, 0.82, 1),
            size_hint_y=0.12,
        )
        root.add_widget(title)

        glass = GlassDisplay(size_hint_y=0.23)
        self.status = Label(
            text="NEON GALAXY  •  READY",
            font_name=TECH_FONT,
            font_size=sp(10),
            color=(0.88, 0.48, 0.80, 0.9),
            halign="right",
            valign="middle",
            size_hint_y=0.25,
        )
        self.status.bind(size=self.status.setter("text_size"))

        self.display = Label(
            text="0",
            font_name=TECH_FONT,
            font_size=sp(43),
            bold=True,
            color=(1, 0.42, 0.82, 1),
            halign="right",
            valign="middle",
            size_hint_y=0.75,
        )
        self.display.bind(size=self.display.setter("text_size"))
        glass.add_widget(self.status)
        glass.add_widget(self.display)
        root.add_widget(glass)

        grid = GridLayout(
            cols=4,
            rows=5,
            spacing=dp(9),
            size_hint_y=0.615,
        )
        buttons = (
            "AC", "⌫", "%", "÷",
            "7", "8", "9", "×",
            "4", "5", "6", "−",
            "1", "2", "3", "+",
            "±", "0", ".", "=",
        )

        for value in buttons:
            if value == "=":
                kind = "equals"
            elif value in ("÷", "×", "−", "+"):
                kind = "operator"
            elif value in ("AC", "⌫", "%", "±"):
                kind = "action"
            else:
                kind = "number"

            button = NeonButton(text=value, kind=kind)
            if value in ("AC", "⌫"):
                button.font_size = sp(22)
            button.bind(on_release=self.press)
            grid.add_widget(button)

        root.add_widget(grid)

        footer = Label(
            text="PINK NEON  /  MGT EDITION",
            font_name=TECH_FONT,
            font_size=sp(9),
            color=(0.66, 0.36, 0.68, 0.85),
            size_hint_y=0.035,
        )
        root.add_widget(footer)
        return root

    def refresh_display(self):
        text = self.expression or "0"
        self.display.text = text
        length = len(text)
        if length > 18:
            self.display.font_size = sp(26)
        elif length > 13:
            self.display.font_size = sp(33)
        elif length > 9:
            self.display.font_size = sp(38)
        else:
            self.display.font_size = sp(43)
        self.status.text = "RESULT  •  READY" if self.just_evaluated else "NEON GALAXY  •  READY"

    def toggle_sign(self):
        match = re.search(r"(?:\d+(?:\.\d*)?|\.\d+)$", self.expression)
        if not match:
            if not self.expression:
                self.expression = "-"
            return

        start = match.start()
        prefix = self.expression[:start]
        number = match.group(0)
        if prefix.endswith(("-", "−")) and (len(prefix) == 1 or prefix[-2] in "+−×÷("):
            prefix = prefix[:-1]
        else:
            prefix += "-"
        self.expression = prefix + number

    def apply_percent(self):
        match = re.search(r"(?:\d+(?:\.\d*)?|\.\d+)$", self.expression)
        if not match:
            return
        value = float(match.group(0)) / 100.0
        self.expression = self.expression[:match.start()] + number_text(value)

    def press(self, button):
        value = button.text
        operators = ("+", "−", "×", "÷")

        try:
            if value == "AC":
                self.expression = ""
                self.just_evaluated = False

            elif value == "⌫":
                if self.just_evaluated:
                    self.expression = ""
                    self.just_evaluated = False
                else:
                    self.expression = self.expression[:-1]

            elif value == "=":
                if self.expression and self.expression[-1] not in operators:
                    result = safe_calculate(self.expression)
                    self.expression = number_text(result)
                    self.just_evaluated = True

            elif value == "±":
                if self.just_evaluated:
                    self.just_evaluated = False
                self.toggle_sign()

            elif value == "%":
                if self.just_evaluated:
                    self.just_evaluated = False
                self.apply_percent()

            elif value in operators:
                if self.just_evaluated:
                    self.just_evaluated = False
                if not self.expression:
                    if value == "−":
                        self.expression = "−"
                elif self.expression[-1] in operators:
                    self.expression = self.expression[:-1] + value
                else:
                    self.expression += value

            elif value == ".":
                if self.just_evaluated:
                    self.expression = "0"
                    self.just_evaluated = False
                current_number = re.split(r"[+\-−×÷]", self.expression)[-1]
                if "." not in current_number:
                    if not self.expression or self.expression[-1] in operators:
                        self.expression += "0."
                    else:
                        self.expression += "."

            else:  # digits
                if self.just_evaluated:
                    self.expression = ""
                    self.just_evaluated = False
                self.expression += value

            self.refresh_display()

        except (ValueError, SyntaxError, ZeroDivisionError, OverflowError):
            self.expression = ""
            self.just_evaluated = False
            self.display.text = "Error"
            self.status.text = "CHECK EXPRESSION"
            self.display.font_size = sp(34)


if __name__ == "__main__":
    MGTCalculator().run()