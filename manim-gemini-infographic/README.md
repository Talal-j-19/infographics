# Manim Gemini Infographic

This project utilizes the Gemini API to generate Manim code for creating infographics and renders them into GIFs using Manim.

## Project Structure

```
manim-gemini-infographic
├── src
│   ├── main.py          # Entry point of the application
│   ├── gemini_api.py    # Functions to interact with the Gemini API
│   ├── manim_render.py   # Handles rendering of Manim code
│   └── utils.py         # Utility functions
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd manim-gemini-infographic
   ```

2. **Install dependencies:**
   Make sure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the application:**
   Execute the main script to start the application:
   ```bash
   python src/main.py
   ```

2. **Provide a prompt:**
   When prompted, enter a description of the infographic you want to create. The application will interact with the Gemini API to generate the corresponding Manim code.

3. **Rendering:**
   The generated Manim code will be rendered into a GIF, which will be saved in the specified output directory.

## Main Functionalities

- **Gemini API Interaction:** The application prompts the Gemini API to generate Manim code based on user input.
- **Manim Rendering:** The generated Manim code is executed to create a GIF.
- **Utility Functions:** Helper functions are provided for saving the rendered GIF and other common tasks.

## Contributing

Feel free to submit issues or pull requests to improve the project.