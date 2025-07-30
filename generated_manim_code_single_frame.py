from manim import *

class Scene(Scene):
    def construct(self):
        # Configuration and Custom Color Palette
        COLOR_PALETTE = {
            "primary": "#4285F4",  # Manim Blue / Google Blue
            "secondary": "#34A853", # Manim Green / Google Green
            "accent": "#EA4335",   # Manim Red / Google Red
            "text": WHITE,
            "subtext": LIGHT_GRAY,
            "box_bg": "#2C3E50",   # Darker Blue/Gray for stage boxes
            "arrow": YELLOW_A,     # Bright arrow color
            "start_end_node": "#FBB03B", # Orange/Gold for start/end nodes
            "icon1": BLUE_C,
            "icon2": GREEN_C,
            "icon3": PURPLE_C,
            "icon4": RED_C,
            "tip_bg": "#3A3A3A",   # Darker gray for tips background
            "tip_heading": YELLOW_E, # Bright yellow for tip headings
        }

        stage_box_color = COLOR_PALETTE["box_bg"]
        stage_fill_opacity = 0.9
        stage_corner_radius = 0.2
        arrow_color = COLOR_PALETTE["arrow"]
        text_color = COLOR_PALETTE["text"]
        heading_color = COLOR_PALETTE["primary"]
        subtext_color = COLOR_PALETTE["subtext"]

        # Adjusted Font Sizes for better fit and readability
        title_font_size = 32 # Reduced from 36
        stage_label_font_size = 18 # Reduced from 20
        concept_font_size = 13 # Reduced from 14
        tip_text_font_size = 12 # Reduced from 13
        node_label_font_size = 14 # Reduced from 16

        # --- Title ---
        title = Text("The Journey to Coding Mastery", font_size=title_font_size, color=heading_color, weight=BOLD)
        title.to_edge(UP, buff=0.2) # Reduced buff from 0.3

        # --- Helper function for stages ---
        def create_stage_box(label_text, concepts_list, icon_mob, icon_color):
            icon_mob.set_height(0.6).set_color(icon_color)
            label = Text(label_text, font_size=stage_label_font_size, color=text_color, weight=BOLD)

            # Create a VGroup for concepts, with bullet points and left-aligned
            concepts_mob = VGroup(*[Text(f"• {c}", font_size=concept_font_size, color=subtext_color) for c in concepts_list])
            concepts_mob.arrange(DOWN, buff=0.1, aligned_edge=LEFT) 

            # Arrange icon, label, and concepts_mob as a column, centered horizontally
            content_column = VGroup(icon_mob, label, concepts_mob).arrange(DOWN, buff=0.08, center=True) # Reduced buff from 0.15

            # Create a rectangle around the content
            rect = SurroundingRectangle(content_column, buff=0.1, color=stage_box_color, fill_opacity=stage_fill_opacity, corner_radius=stage_corner_radius) # Reduced buff from 0.2

            # Position the content column precisely at the center of the rectangle
            # This move_to is technically redundant if SurroundingRectangle auto-centers, but harmless.
            content_column.move_to(rect.get_center()) 

            return VGroup(rect, content_column)

        # --- Stages ---

        # Stage 0: Start
        start_text = Text("START", font_size=node_label_font_size, color=COLOR_PALETTE["start_end_node"], weight=BOLD)

        # Stage 1: Foundations
        foundations = create_stage_box(
            "1. Foundations",
            ["Logic & Control Flow", "Variables & Data Types"],
            Tex(r"$\langle/\rangle$").scale(1.2), COLOR_PALETTE["icon1"]
        )

        # Stage 2: Core Concepts (Reduced to 2 concepts for space)
        core_concepts = create_stage_box(
            "2. Core Concepts",
            ["Functions & Modularity", "Data Structures"], # Removed "Algorithms Basics"
            Tex(r"$\Sigma$").scale(1.2), COLOR_PALETTE["icon2"]
        )

        # Stage 3: Applied Development
        applied_dev = create_stage_box(
            "3. Applied Development",
            ["Version Control (Git)", "Web/API Development", "Databases Basics"],
            Tex(r"$\{\!\!\}$").scale(1.2), COLOR_PALETTE["icon3"]
        )

        # Stage 4: Advanced & Specialization (Reduced to 2 concepts for space)
        advanced_topics = create_stage_box(
            "4. Advanced & Specialization",
            ["Software Architecture", "System Design"], # Removed "Performance & Security"
            Tex(r"$\infty$").scale(1.2), COLOR_PALETTE["icon4"]
        )

        # Final Goal
        goal_text = Text("MASTERY", font_size=node_label_font_size, color=COLOR_PALETTE["start_end_node"], weight=BOLD)
        
        # Arrange all stage boxes and start/goal text vertically
        main_flow = VGroup(start_text, foundations, core_concepts, applied_dev, advanced_topics, goal_text)
        main_flow.arrange(DOWN, buff=0.25, center=True) # Reduced buff from 0.4
        main_flow.next_to(title, DOWN, buff=0.2) # Reduced buff from 0.3

        # --- Arrows ---
        arrow_config = {"buff": 0.1, "color": arrow_color, "stroke_width": 3, "tip_length": 0.2}
        arrow1 = Arrow(start_text.get_bottom(), foundations.get_top(), **arrow_config)
        arrow2 = Arrow(foundations.get_bottom(), core_concepts.get_top(), **arrow_config)
        arrow3 = Arrow(core_concepts.get_bottom(), applied_dev.get_top(), **arrow_config)
        arrow4 = Arrow(applied_dev.get_bottom(), advanced_topics.get_top(), **arrow_config)
        arrow5 = Arrow(advanced_topics.get_bottom(), goal_text.get_top(), **arrow_config)

        # --- Side Tips ---
        tip_style = {"font_size": tip_text_font_size, "color": text_color, "line_spacing": 0.8}
        tip_rect_properties = {"corner_radius": 0.2, "color": COLOR_PALETTE["tip_bg"], "fill_opacity": 0.7}
        tip_text_padding_width = 0.15 # Reduced from 0.3
        tip_text_padding_height = 0.1 # Reduced from 0.2
        tip_horizontal_buff = 0.4 # Reduced from 0.5

        # Tip 1: General learning advice
        tip1_heading = Text("PRO TIPS:", font_size=tip_text_font_size + 2, color=COLOR_PALETTE["tip_heading"], weight=BOLD)
        tip1_content = Text("• Practice Daily, Build Projects\n• Debug & Read Docs\n• Join Dev Communities", **tip_style)
        
        # Create a VGroup for the text content, arranged with left alignment
        tip1_text_elements = VGroup(tip1_heading, tip1_content).arrange(DOWN, buff=0.05, aligned_edge=LEFT)
        
        # Create the rectangle sized for the text, initially at ORIGIN
        tip1_rect = RoundedRectangle(
            width=tip1_text_elements.width + tip_text_padding_width * 2,
            height=tip1_text_elements.height + tip_text_padding_height * 2,
            **tip_rect_properties
        )
        
        # Position the text elements relative to the rectangle to ensure visual left alignment with padding
        tip1_text_elements.align_to(tip1_rect, LEFT)
        tip1_text_elements.shift(RIGHT * tip_text_padding_width)
        tip1_text_elements.set_y(tip1_rect.get_y()) # Vertically center the text within the rectangle
        
        # Finally, group the rectangle and the now-positioned text elements
        tip1_group = VGroup(tip1_rect, tip1_text_elements)
        
        # Tip 2: Advanced/Growth advice
        tip2_heading = Text("CAREER & GROWTH:", font_size=tip_text_font_size + 2, color=COLOR_PALETTE["tip_heading"], weight=BOLD)
        tip2_content = Text("• Contribute to Open Source\n• Network & Specialize\n• Continuous Learning", **tip_style)
        
        tip2_text_elements = VGroup(tip2_heading, tip2_content).arrange(DOWN, buff=0.05, aligned_edge=LEFT)
        tip2_rect = RoundedRectangle(
            width=tip2_text_elements.width + tip_text_padding_width * 2,
            height=tip2_text_elements.height + tip_text_padding_height * 2,
            **tip_rect_properties
        )
        tip2_text_elements.align_to(tip2_rect, LEFT)
        tip2_text_elements.shift(RIGHT * tip_text_padding_width)
        tip2_text_elements.set_y(tip2_rect.get_y())
        tip2_group = VGroup(tip2_rect, tip2_text_elements)
        
        # Position tips to the right of the main stage flow, aligning with relevant stages
        tip1_group.set_x(main_flow.get_right()[0] + tip_horizontal_buff + tip1_group.width/2)
        tip1_group.set_y(foundations.get_center()[1])
        
        tip2_group.set_x(main_flow.get_right()[0] + tip_horizontal_buff + tip2_group.width/2)
        tip2_group.set_y(advanced_topics.get_center()[1])

        # --- Footer ---
        footer_text = Text("Knowledge is Power. Code Wisely!", font_size=18, color=LIGHT_GRAY)
        
        # --- Assemble main elements and scale to fit ---
        main_elements = VGroup(
            title,
            main_flow,
            arrow1, arrow2, arrow3, arrow4, arrow5,
            tip1_group, tip2_group,
        )

        # Scale the collection to fit within the scene frame (approx 14.22x8 units)
        # Target height reduced to leave enough space for footer and prevent cutoff
        target_height = config.frame_height * 0.9 # Reduced from 0.95
        target_width = config.frame_width * 0.95

        if main_elements.height > target_height or main_elements.width > target_width:
            main_elements.scale_to_fit_height(target_height)
            if main_elements.width > target_width:
                main_elements.scale_to_fit_width(target_width)
        
        main_elements.move_to(ORIGIN) # Center the main diagram on the screen

        # Position footer relative to the scaled main diagram
        footer_text.next_to(main_elements, DOWN, buff=0.2)

        # Add all elements to the scene
        self.add(main_elements, footer_text)