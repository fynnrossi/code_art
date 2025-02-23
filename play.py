from manim.manimlib import *

class TestScene(Scene):
    def construct(self):
        circle = Circle()
        self.play(Create(circle))

