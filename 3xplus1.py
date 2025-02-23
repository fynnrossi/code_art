from manim import *

def collatz_sequence_step(n):
    if n % 2 == 0:
        return n // 2
    else:
        return n * 3 + 1

def collatz_sequence(n):
    sequence = []
    while n != 1:
        sequence.append(n)
        n = collatz_sequence_step(n)
    sequence.append(1)
    return sequence

class CollatzChart(Scene):
    def construct(self):
        # 1. Create the axes.
        # Here we define x from 0 to 20 (steps) and y from 0 to 100 (values).
        axes = Axes(
            x_min=0,
            x_max=20,
            y_min=0,
            y_max=100,
            # Configuring tick frequency and number labels:
            x_axis_config={
                "tick_frequency": 1,
                "include_numbers": True,
            },
            y_axis_config={
                "tick_frequency": 10,
                "include_numbers": True,
            }
        )
        axes.to_edge(LEFT, buff=1)
        self.add(axes)

        # 2. Choose starting values and colors.
        # You can add as many starting numbers as you like.
        start_values = [5, 7]
        colors = [RED, GREEN]

        # 3. For each starting value, compute its sequence and create an animated line.
        lines_info = []  # Will store tuples: (line, tracker, total_points)
        for i, start in enumerate(start_values):
            seq = collatz_sequence(start)
            # Create a ValueTracker to control the current index shown.
            tracker = ValueTracker(0)
            
            # Define an updater function that returns a line up to the current index.
            def get_line(tracker=tracker, seq=seq):
                curr_index = int(tracker.get_value())
                # If not enough points, return an empty VMobject.
                if curr_index < 1:
                    return VMobject()
                # Use indices as x-coordinates (steps) and sequence values as y-coordinates.
                points = [
                    axes.coords_to_point(x, y)
                    for x, y in zip(range(len(seq[:curr_index+1])), seq[:curr_index+1])
                ]
                line = VMobject()
                line.set_points_as_corners(points)
                return line

            # Create an always_redraw mobject for the line.
            line = always_redraw(lambda get_line=get_line, col=colors[i]: get_line().set_color(col))
            self.add(line)
            lines_info.append((line, tracker, len(seq)))

        # 4. Animate all the lines concurrently.
        # For each line, animate its ValueTracker from 0 to the full length.
        animations = [
            tracker.animate.set_value(total - 1)
            for (_, tracker, total) in lines_info
        ]
        self.play(AnimationGroup(*animations, lag_ratio=0.5, run_time=5))
        self.wait(2)

if __name__ == '__main__':
    scene = CollatzChart()
    scene.play()


