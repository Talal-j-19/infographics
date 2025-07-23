from manim import *

class Scene(MovingCameraScene):
    def construct(self):
        # Set a consistent color palette for the infographic
        COLOR_BG = "#222222" # Dark background
        COLOR_TEXT = "#FFFFFF" # White text
        COLOR_ACCENT1 = "#FFD700" # Gold/Yellow - for predicted words/attention
        COLOR_ACCENT2 = "#FF6347" # Tomato/Red-orange - for section labels/flow
        COLOR_BLUE = "#00BFFF" # Deep Sky Blue - for input tokens
        COLOR_PURPLE = "#8A2BE2" # Blue Violet - for transformer block
        COLOR_GREEN = "#32CD32" # Lime Green - for embeddings

        self.camera.background_color = COLOR_BG

        # Helper class for a styled token block
        class TokenBlock(VGroup):
            def __init__(self, text_str, font_size=28, text_color=COLOR_TEXT, rect_color=COLOR_BLUE, fill_opacity=0.2, stroke_color=COLOR_BLUE, stroke_width=2, **kwargs):
                super().__init__(**kwargs)
                text = Text(text_str, font_size=font_size, color=text_color)
                rect = Rectangle(width=text.get_width() + 0.4, height=0.7, color=rect_color, fill_opacity=fill_opacity, stroke_color=stroke_color, stroke_width=stroke_width)
                rect.move_to(text.get_center()) # Ensure rectangle is centered on text
                self.add(rect, text)
                self.move_to(ORIGIN) # Default position, will be overridden by arrange/next_to

        # --- Scene 1: Title Introduction ---
        title = Text("How Large Language Models (LLMs) Work", font_size=60, color=COLOR_TEXT).to_edge(UP, buff=0.8)
        subtitle = Text("A Step-by-Step Infographic", font_size=36, color=COLOR_ACCENT1).next_to(title, DOWN, buff=0.4)

        self.play(
            LaggedStart(
                FadeIn(title, shift=UP),
                FadeIn(subtitle, shift=UP),
                lag_ratio=0.3
            )
        )
        self.wait(1.5)

        # --- Scene 2: Input Prompt ---
        self.play(FadeOut(subtitle))
        self.play(title.animate.to_edge(UL).scale(0.6)) # Shrink and move title to top-left

        current_label = Text("1. Input Prompt", font_size=36, color=COLOR_ACCENT2).to_edge(UL).shift(RIGHT*2)
        prompt_text = Text('"Write a poem about a cat."', font_size=40, color=COLOR_TEXT).move_to(ORIGIN)

        self.play(FadeIn(current_label, shift=LEFT), Write(prompt_text))
        self.wait(1.5)

        # --- Scene 3: Tokenization ---
        # Create next_label as a copy of current_label to ensure it's a separate Mobject for transform
        next_label = current_label.copy().set_text("2. Tokenization")
        
        tokens_raw = ["Write", "a", "poem", "about", "a", "cat", "."]
        token_mobjects = VGroup(*[TokenBlock(t, rect_color=COLOR_BLUE, stroke_color=COLOR_BLUE) for t in tokens_raw]).arrange(RIGHT, buff=0.2)
        
        self.play(Transform(current_label, next_label))
        self.play(
            FadeOut(prompt_text),
            LaggedStart(*[FadeIn(t) for t in token_mobjects], lag_ratio=0.1)
        )
        self.wait(1.5)

        # --- Scene 4: Embeddings ---
        next_label = current_label.copy().set_text("3. Embeddings (Numerical Vectors)")

        animations_for_embedding = []
        
        # Create a new VGroup to hold the resulting embedding Mobjects
        final_embedded_tokens_mobjects = VGroup()

        for token_block in token_mobjects:
            # Represent embedding as a tall, thin rectangle (vector-like)
            embedding_rect = Rectangle(
                width=0.2, height=1.5,
                color=COLOR_GREEN, fill_opacity=0.8,
                stroke_width=1
            ).move_to(token_block.get_center()) # Position it at the center of the token it replaces
            
            # Use ReplacementTransform for transforming between different Mobject types
            animations_for_embedding.append(ReplacementTransform(token_block, embedding_rect))
            final_embedded_tokens_mobjects.add(embedding_rect) # Add to the group that will be animated collectively

        # Arrange the new embedding Mobjects for their final relative positions
        final_embedded_tokens_mobjects.arrange(RIGHT, buff=0.3)

        explanation_text = Text("Tokens become numerical vectors representing meaning.", font_size=28, color=COLOR_TEXT).next_to(final_embedded_tokens_mobjects, DOWN, buff=0.7)

        self.play(Transform(current_label, next_label))
        self.play(
            AnimationGroup(*animations_for_embedding, lag_ratio=0.1),
            FadeIn(explanation_text, shift=DOWN)
        )
        # Reassign embedded_tokens to the new VGroup after transformation for subsequent use
        embedded_tokens = final_embedded_tokens_mobjects
        self.wait(2)

        # --- Scene 5: Transformer & Attention ---
        next_label = current_label.copy().set_text("4. Transformer & Attention")

        transformer_block = RoundedRectangle(
            width=10, height=5, corner_radius=0.5,
            color=COLOR_PURPLE, fill_opacity=0.1, stroke_width=3
        ).move_to(ORIGIN).shift(DOWN*0.5)
        
        transformer_text = Text("Transformer Block", font_size=40, color=COLOR_TEXT).move_to(transformer_block.get_center() + UP*1.2)
        attention_text = Text("Self-Attention Mechanism", font_size=32, color=COLOR_ACCENT1).next_to(transformer_text, DOWN, buff=0.3)

        input_arrow = Arrow(embedded_tokens.get_bottom() + UP*0.5, transformer_block.get_top(), buff=0.1, color=COLOR_ACCENT2, stroke_width=4)
        input_arrow_label = Text("Input Embeddings", font_size=24, color=COLOR_TEXT).next_to(input_arrow, UP, buff=0.1)

        self.play(
            Transform(current_label, next_label),
            FadeOut(explanation_text),
            # Move embeddings up to serve as input
            embedded_tokens.animate.move_to(embedded_tokens.get_center() + UP*2) 
        )
        self.play(
            Create(transformer_block),
            FadeIn(transformer_text, attention_text),
            FadeIn(input_arrow, input_arrow_label)
        )
        # Move embeddings into the transformer visual
        self.play(
            FadeOut(input_arrow_label),
            embedded_tokens.animate.move_to(transformer_block.get_center() + UP*1.5).scale(0.8) # Adjust scale and position
        )

        # Simulate attention mechanism with a pulse and flash
        self.play(
            Indicate(attention_text, scale_factor=1.1, color=COLOR_ACCENT1, run_time=1.5),
            Flash(embedded_tokens[3].get_center(), color=YELLOW_B, line_length=0.2, run_time=0.5), # Highlight "about"
            Flash(embedded_tokens[5].get_center(), color=YELLOW_B, line_length=0.2, run_time=0.5)  # Highlight "cat"
        )
        self.wait(1)

        # --- Scene 6: Next Token Prediction ---
        next_label = current_label.copy().set_text("5. Next Token Prediction")

        output_arrow = Arrow(transformer_block.get_bottom(), transformer_block.get_bottom() + DOWN*1.5, buff=0.1, color=COLOR_ACCENT2, stroke_width=4)
        
        # Predicted token (first as embedding, then transformed to token block)
        predicted_embedding_visual = Rectangle(width=0.2, height=1.5, color=COLOR_GREEN, fill_opacity=0.8, stroke_width=1).next_to(output_arrow, DOWN, buff=0.2)
        predicted_word = "The"
        predicted_token = TokenBlock(predicted_word, rect_color=COLOR_ACCENT1, stroke_color=COLOR_ACCENT1) # Create the token block Mobject

        self.play(
            Transform(current_label, next_label),
            FadeOut(embedded_tokens) # These embeddings have been processed inside the transformer
        )
        self.play(
            Create(output_arrow),
            FadeIn(predicted_embedding_visual, shift=DOWN)
        )
        # Position predicted_token at the same spot as predicted_embedding_visual for smooth replacement
        predicted_token.move_to(predicted_embedding_visual.get_center())
        # Use ReplacementTransform for transforming between different Mobject types (Rectangle to VGroup)
        self.play(ReplacementTransform(predicted_embedding_visual, predicted_token)) 
        self.wait(1)

        # --- Scene 7: Iterative Generation ---
        next_label = current_label.copy().set_text("6. Iterative Generation")

        # Move transformer block to the left for the iterative process
        self.play(
            Transform(current_label, next_label),
            transformer_block.animate.scale(0.6).to_edge(LEFT, buff=0.5).shift(DOWN*0.5),
            transformer_text.animate.scale(0.6).move_to(transformer_block.get_center() + UP*0.8),
            attention_text.animate.scale(0.6).next_to(transformer_text, DOWN, buff=0.2),
            FadeOut(output_arrow) # Fade out the arrow, but predicted_token stays
        )

        # The initial context from the prompt (copied from Scene 3)
        initial_context_tokens = VGroup(*[TokenBlock(w, rect_color=COLOR_BLUE, stroke_color=COLOR_BLUE) for w in tokens_raw])
        initial_context_tokens.arrange(RIGHT, buff=0.2).to_edge(UP, buff=1.0)
        
        # Initialize current_sequence as the initial tokens
        # We add this VGroup to the scene. It will be modified in place by adding new tokens.
        self.play(FadeIn(initial_context_tokens)) # Animate fade in of base context

        # Remove predicted_token from scene as a top-level Mobject before adding it to current_sequence
        # This prevents duplicate Mobjects when current_sequence is rearranged.
        self.remove(predicted_token) 

        current_sequence = initial_context_tokens # Now current_sequence refers to the Mobjects on screen
        current_sequence.add(predicted_token) 
        self.play(
            current_sequence.animate.arrange(RIGHT, buff=0.2).to_edge(UP, buff=1.0) # Animate the VGroup rearrangement
        )
        self.wait(0.5)

        predicted_words_sequence = ["cat", "sits", "on", "the", "mat."] # Remaining words to be generated
        for i, word in enumerate(predicted_words_sequence):
            # Visually feed the entire current sequence back into the transformer
            temp_group_to_transformer = current_sequence.copy().set_opacity(0.5)
            self.play(temp_group_to_transformer.animate.move_to(transformer_block.get_center()), run_time=0.7)
            self.play(FadeOut(temp_group_to_transformer))
            
            # Indicate transformer processing
            self.play(Indicate(transformer_block, scale_factor=1.05, color=COLOR_PURPLE, run_time=0.7))

            # Simulate output of the next token
            new_predicted_token = TokenBlock(word, rect_color=COLOR_ACCENT1, stroke_color=COLOR_ACCENT1)
            output_from_transformer_pos = transformer_block.get_bottom() + DOWN*0.5
            output_arrow_iter = Arrow(transformer_block.get_bottom(), output_from_transformer_pos, buff=0.1, color=COLOR_ACCENT2, stroke_width=3)
            
            # Position new_predicted_token for animation
            new_predicted_token.move_to(output_from_transformer_pos)
            
            # Animate emergence. FadeIn will add it to the scene.
            self.play(Create(output_arrow_iter), FadeIn(new_predicted_token, shift=DOWN))
            self.play(FadeOut(output_arrow_iter))

            # Remove new_predicted_token from the scene as a top-level Mobject
            # before adding it to current_sequence, to prevent duplicates.
            self.remove(new_predicted_token) 
            
            # Add the Mobject to the VGroup
            current_sequence.add(new_predicted_token) 
            # Animate the VGroup rearrangement
            self.play(
                current_sequence.animate.arrange(RIGHT, buff=0.2).to_edge(UP, buff=1.0) 
            )
            self.wait(0.8)

        self.wait(1)

        # --- Scene 8: Coherent Output ---
        next_label = current_label.copy().set_text("7. Coherent Output")

        # Combine prompt and generated text for the final output
        final_poem_text_str = '"Write a poem about a cat." The cat sits on the mat.'
        final_poem_text = Text(final_poem_text_str, font_size=40, color=COLOR_TEXT).move_to(ORIGIN)

        self.play(
            Transform(current_label, next_label),
            FadeOut(transformer_block, transformer_text, attention_text)
        )
        # Use ReplacementTransform for transforming between different Mobject types (VGroup of TokenBlocks to Text)
        self.play(
            ReplacementTransform(current_sequence, final_poem_text)
        )
        self.wait(2)

        # --- Scene 9: Summary & End ---
        next_label = current_label.copy().set_text("Summary")

        # Create bullet points as individual Text Mobjects, then arrange the VGroup and position the VGroup
        summary_bullets = VGroup(
            Text("• LLMs learn patterns from vast text data.", font_size=32, color=COLOR_TEXT),
            Text("• They predict the most probable next token.", font_size=32, color=COLOR_TEXT),
            Text("• This iterative process creates human-like text.", font_size=32, color=COLOR_TEXT)
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT) # Arrange them vertically, aligning their left edges

        # Now, position the entire VGroup of bullets
        summary_bullets.to_edge(LEFT, buff=1.0).shift(UP*1)

        self.play(
            Transform(current_label, next_label),
            FadeOut(final_poem_text)
        )
        self.play(LaggedStart(*[FadeIn(b, shift=LEFT) for b in summary_bullets], lag_ratio=0.3))

        ending_text = Text("Unlocking the Power of AI Communication", font_size=44, color=COLOR_ACCENT1).to_edge(DOWN, buff=0.8)
        self.play(FadeIn(ending_text, shift=DOWN))
        self.wait(3)