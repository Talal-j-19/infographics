from manim import *

class Scene(Scene):
    def construct(self):
        # 0. Configuration
        self.camera.background_color = "#202020" # Dark background

        # Define custom colors using hex codes
        COLOR_TITLE = "#ADD8E6" # Light Blue
        COLOR_STEP_1 = "#5DADE2" # Blue
        COLOR_STEP_2 = "#52BE80" # Green
        COLOR_STEP_3 = "#F4D03F" # Yellow
        COLOR_STEP_4 = "#EB984E" # Orange
        COLOR_STEP_5 = "#E74C3C" # Red
        COLOR_TEXT = "#FFFFFF"   # White
        COLOR_DETAILS = "#B0B0B0" # Light Gray
        COLOR_ARROW = "#808080"  # Gray
        COLOR_TIP_BOX = "#F7DC6F" # Yellow for tip

        # 1. Main Title
        title = Text("Roadmap to Learn AI", font_size=36, color=COLOR_TITLE, weight="BOLD") 
        
        # 2. Define Step Properties
        box_padding_x = 0.3 
        box_padding_y = 0.2 
        min_box_width = 8.5 
        box_radius = 0.2
        arrow_tip_length = 0.2
        vertical_step_buff = 0.8 # Increased buff for more space between steps
        vertical_group_buff = 1.0 # Increased buff for more space between main sections

        # 3. Step Information
        step_data = [
            {
                "title": "Foundations",
                "details": "Math (Lin Alg, Calc, Stats), Python (Libraries), DS&A",
                "color": COLOR_STEP_1,
                "icon_tex": r"$\sum$" # Summation symbol for math/foundations
            },
            {
                "title": "Machine Learning",
                "details": "Supervised, Unsupervised, Regression, Classification, Clustering",
                "color": COLOR_STEP_2,
                "icon_tex": r"$\approx$" # Approximation symbol for modeling
            },
            {
                "title": "Deep Learning & Frameworks",
                "details": "Neural Networks, CNNs, RNNs, Transformers, PyTorch/TF", 
                "color": COLOR_STEP_3,
                "icon_tex": r"$\psi$" # Psi, abstract for deep learning
            },
            {
                "title": "Specialization",
                "details": "NLP (Natural Language Processing), CV (Computer Vision), RL (Reinforcement Learning), GenAI", 
                "color": COLOR_STEP_4,
                "icon_tex": r"$\star$" # Star for specialization/niche
            },
            {
                "title": "Projects & Portfolio",
                "details": "Kaggle, GitHub, Personal Projects, Blog, Portfolio Building", 
                "color": COLOR_STEP_5,
                "icon_tex": r"$\checkmark$" # Checkmark for completion/achievement
            }
        ]

        # Create all individual step Mobjects (rectangle + text content)
        individual_steps = []
        for data in step_data:
            # Create icon and title
            icon = Tex(data["icon_tex"], font_size=24, color=COLOR_TEXT) 
            title_text = Text(data["title"], font_size=24, color=COLOR_TEXT, weight="BOLD") 
            
            # Group icon and title horizontally
            icon_and_title = Group(icon, title_text).arrange(RIGHT, buff=0.15, aligned_edge=LEFT) 
            
            # Create details text, wrapping within a specific width
            details_text = Text(
                data["details"], 
                font_size=14, # Reduced font size for better fit
                color=COLOR_DETAILS, 
                line_spacing=1.2,
                max_width=min_box_width - 2 * box_padding_x 
            )

            # Group all text content vertically
            text_vgroup = VGroup(icon_and_title, details_text).arrange(DOWN, buff=0.15, aligned_edge=LEFT) 
            
            # Calculate rectangle dimensions based on text content and padding
            current_box_width = max(min_box_width, text_vgroup.width + 2 * box_padding_x)
            current_box_height = text_vgroup.height + 2 * box_padding_y

            rect = RoundedRectangle(
                width=current_box_width,
                height=current_box_height,
                corner_radius=box_radius,
                stroke_color=data["color"],
                fill_color=data["color"],
                fill_opacity=0.15,
                stroke_width=3
            )
            
            # Position the text_vgroup inside the rectangle
            text_vgroup.align_to(rect.get_corner(UL) + RIGHT * box_padding_x + DOWN * box_padding_y, UL)

            # Group rectangle and text for the step
            step_group = VGroup(rect, text_vgroup)
            individual_steps.append(step_group)
        
        # Arrange all steps vertically, centered
        steps_vgroup = VGroup(*individual_steps).arrange(DOWN, buff=vertical_step_buff, center=True)

        # Create arrows between arranged steps.
        list_of_arrows = []
        for i in range(len(steps_vgroup.submobjects) - 1):
            start_rect = steps_vgroup.submobjects[i][0]
            end_rect = steps_vgroup.submobjects[i+1][0]
            arrow = Arrow(
                start=start_rect.get_bottom(), 
                end=end_rect.get_top(),   
                color=COLOR_ARROW,
                tip_length=arrow_tip_length,
                stroke_width=3.5
            )
            list_of_arrows.append(arrow)
        arrows = VGroup(*list_of_arrows)

        # 4. Concluding note/tip
        tip_rect = RoundedRectangle(
            width=min_box_width, 
            height=1.6, 
            corner_radius=0.2,
            stroke_color=COLOR_TIP_BOX, fill_color=COLOR_TIP_BOX, fill_opacity=0.15, stroke_width=3
        )
        tip_text = Text(
            "Continuous learning & hands-on projects are key!",
            font_size=14, # Reduced font size for better fit
            color=COLOR_TIP_BOX,
            weight="BOLD",
            line_spacing=1.2,
            max_width=tip_rect.width - 2*box_padding_x 
        ).move_to(tip_rect.get_center())
        
        final_tip_group = VGroup(tip_rect, tip_text)

        # 5. Assemble the entire infographic structure for final positioning
        steps_and_arrows = VGroup(steps_vgroup, arrows)

        all_content = VGroup(title, steps_and_arrows, final_tip_group)
        
        # Arrange and scale to fit the frame
        all_content.arrange(DOWN, buff=vertical_group_buff, center=True)
        all_content.scale_to_fit_height(config.frame_height * 0.9).center()

        # Add all elements to the scene
        self.add(all_content)