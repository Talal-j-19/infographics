from manim import *

class Scene(Scene):
    def construct(self):
        # --- Configuration & Global Elements ---
        TITLE_FONT_SIZE = 32
        SECTION_TITLE_FONT_SIZE = 24
        TEXT_FONT_SIZE = 12  # Adjusted for better column fit
        CODE_FONT_SIZE = 12
        
        BOX_COLOR = GREY_D
        LINE_COLOR = GREY_B
        BLUE_ACCENT = BLUE_A
        GOLD_ACCENT = GOLD
        GREEN_ACCENT = GREEN_B

        VERTICAL_ITEM_BUFF = 0.1
        SECTION_BREAK_BUFF = 0.4
        COLUMN_TEXT_LINE_SPACING = 0.7

        # Adjusted for better column separation
        LEFT_COL_ALIGN_X = -6.0 
        RIGHT_COL_ALIGN_X = 0.5 

        # Background frame
        background_rect = Rectangle(
            width=config.frame_width - 0.5,
            height=config.frame_height - 0.5,
            stroke_color=BOX_COLOR,
            stroke_width=2,
            fill_opacity=0.0
        )
        self.add(background_rect)

        # Title
        title = Text("Manim: A Quick Reference Guide", font_size=TITLE_FONT_SIZE, color=BLUE_C)
        title.to_edge(UP, buff=0.2)
        self.add(title)

        # Top separator line
        separator_top = Line(config.frame_width/2 * LEFT, config.frame_width/2 * RIGHT, color=LINE_COLOR, stroke_width=1)
        separator_top.next_to(title, DOWN, buff=VERTICAL_ITEM_BUFF)
        self.add(separator_top)

        # Placeholder for vertical separator - will be updated later
        v_separator_mid = Line(ORIGIN, ORIGIN, color=LINE_COLOR, stroke_width=1) 

        # --- Section 1: Mobjects & Positioning (Left Column) ---
        mobj_pos_title = Text("1. Mobjects & Positioning", font_size=SECTION_TITLE_FONT_SIZE, color=TEAL_C)
        mobj_pos_title.next_to(separator_top, DOWN, buff=SECTION_BREAK_BUFF)
        mobj_pos_title.align_to(ORIGIN + LEFT_COL_ALIGN_X * RIGHT, LEFT)
        self.add(mobj_pos_title)

        sq = Square(side_length=0.7, color=RED_C, fill_opacity=0.7)
        circ = Circle(radius=0.4, color=GREEN_C, fill_opacity=0.7)
        tri = Triangle(color=PURPLE_C, fill_opacity=0.7).scale(0.5)
        mobjects_visual_group = Group(sq, circ, tri).arrange(RIGHT, buff=0.4)
        mobjects_visual_group.next_to(mobj_pos_title, DOWN, buff=VERTICAL_ITEM_BUFF).align_to(mobj_pos_title, LEFT)
        self.add(mobjects_visual_group)

        mobj_pos_info = Text(
            "Mobjects: Shapes, Text, Equations, Images.\n"
            "Positioning: next_to(), shift(), scale(), align_to().",
            font_size=TEXT_FONT_SIZE,
            color=WHITE,
            line_spacing=COLUMN_TEXT_LINE_SPACING
        ).next_to(mobjects_visual_group, DOWN, buff=VERTICAL_ITEM_BUFF).align_to(mobj_pos_title, LEFT) 
        self.add(mobj_pos_info)

        # --- Section 2: Text & Equations (Right Column) ---
        text_eq_title = Text("2. Text & Equations", font_size=SECTION_TITLE_FONT_SIZE, color=TEAL_C)
        text_eq_title.align_to(mobj_pos_title, UP)
        text_eq_title.align_to(ORIGIN + RIGHT_COL_ALIGN_X * RIGHT, LEFT)
        self.add(text_eq_title)

        math_eq = MathTex(r"c^2 = a^2 + b^2", font_size=24, color=GREEN_C)
        text_eq_visual_group = math_eq 
        text_eq_visual_group.next_to(text_eq_title, DOWN, buff=VERTICAL_ITEM_BUFF).align_to(text_eq_title, LEFT)
        self.add(text_eq_visual_group)

        text_info = Text(
            "Text(): Basic text.\n"
            "MathTex(): LaTeX equations.",
            font_size=TEXT_FONT_SIZE,
            color=WHITE,
            line_spacing=COLUMN_TEXT_LINE_SPACING
        ).next_to(text_eq_visual_group, DOWN, buff=VERTICAL_ITEM_BUFF).align_to(text_eq_title, LEFT) 
        self.add(text_info)

        # --- Dynamic Vertical Separator for Columns ---
        max_y_top_content = max(mobj_pos_title.get_top()[1], text_eq_title.get_top()[1])
        min_y_bottom_content = min(mobj_pos_info.get_bottom()[1], text_info.get_bottom()[1])

        v_separator_mid.set_start_and_end_points(
            (max_y_top_content + VERTICAL_ITEM_BUFF) * UP,
            (min_y_bottom_content - VERTICAL_ITEM_BUFF) * UP
        )
        v_separator_mid.set_x(0) 
        self.add(v_separator_mid)

        # Middle horizontal separator
        separator_mid = Line(config.frame_width/2 * LEFT, config.frame_width/2 * RIGHT, color=LINE_COLOR, stroke_width=1)
        separator_mid.move_to(ORIGIN + UP * (min_y_bottom_content - SECTION_BREAK_BUFF)) # Adjusted buff to align with next section title
        self.add(separator_mid)

        # --- Section 3: Scene, Workflow & Animation (Bottom Center) ---
        scene_workflow_title = Text("3. Scene & Workflow: Bringing it to Life", font_size=SECTION_TITLE_FONT_SIZE, color=TEAL_C)
        scene_workflow_title.next_to(separator_mid, DOWN, buff=SECTION_BREAK_BUFF).set_x(0)
        self.add(scene_workflow_title)

        workflow_points = VGroup(
            Text("- Add Mobjects with self.add(). Animate with self.play().", font_size=TEXT_FONT_SIZE, color=GOLD_ACCENT, line_spacing=COLUMN_TEXT_LINE_SPACING),
            Text("- Render: manim -pql <file.py> YourScene", font_size=TEXT_FONT_SIZE, color=GREEN_ACCENT, line_spacing=COLUMN_TEXT_LINE_SPACING),
        ).arrange(DOWN, buff=VERTICAL_ITEM_BUFF, aligned_edge=LEFT)

        workflow_points.next_to(scene_workflow_title, DOWN, buff=VERTICAL_ITEM_BUFF).set_x(0) 
        self.add(workflow_points)

        code_example = Code(
            code="""class MyScene(Scene):
    def construct(self):
        self.play(Create(Circle()))""", # Adjusted indentation for clarity in the string
            tab_width=4,
            background_stroke_width=0.5,
            background_stroke_color=GREY_A,
            language="python",
            font="Monospace",
            font_size=CODE_FONT_SIZE,
            line_spacing=0.8
        )

        code_example.next_to(workflow_points, DOWN, buff=VERTICAL_ITEM_BUFF).set_x(0) 
        self.add(code_example)