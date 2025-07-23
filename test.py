
from manim import *

class LLMInfographic(Scene):
    def construct(self):
        # Title
        title = Text("Understanding LLMs", color=YELLOW).scale(1.2).to_edge(UP)
        self.play(Write(title))

        # Scene 1 - Training Data
        data_text = Text("📄 Trained on Vast Text Datasets", color=BLUE).scale(0.7).to_edge(LEFT)
        self.play(Write(data_text), run_time=2)
        self.play(data_text.animate.shift(UP*2).set_opacity(0.5), run_time=2)

        # Scene 2 - Parameters Counter with ValueTracker
        param_text = Text("🔢 Billions of Parameters", color=GREEN).scale(0.7).to_edge(LEFT)
        self.play(Write(param_text))

        tracker = ValueTracker(0)
        number = DecimalNumber(tracker.get_value(), color=GREEN, num_decimal_places=0).scale(0.7)
        number.add_updater(lambda m: m.set_value(tracker.get_value()))
        number.next_to(param_text, RIGHT)
        self.add(number)
        self.play(tracker.animate.set_value(10_000_000_000), run_time=4)
        number.clear_updaters()

        # Scene 3 - Transformer Architecture Animation
        trans_box = Rectangle(width=4, height=2, color=WHITE).to_edge(DOWN)
        trans_label = Text("Transformer Model", font_size=24).move_to(trans_box.get_center())
        self.play(Create(trans_box), Write(trans_label))

        tokens = [Dot().move_to(trans_box.get_left() + RIGHT*0.8*i) for i in range(5)]
        self.play(AnimationGroup(*[FadeIn(token) for token in tokens], lag_ratio=0.2))
        self.play(AnimationGroup(*[token.animate.shift(RIGHT*2) for token in tokens], lag_ratio=0.2))

        # Scene 4 - Applications with Fade In
        apps = VGroup(
            Text("🤖 Chatbots", color=ORANGE).scale(0.6),
            Text("📝 Summarization", color=ORANGE).scale(0.6),
            Text("💻 Code Generation", color=ORANGE).scale(0.6)
        ).arrange(DOWN, aligned_edge=LEFT).to_edge(RIGHT)
        self.play(FadeIn(apps, shift=LEFT), run_time=2)

        # Final Wait to Complete Animation
        self.wait(4)
