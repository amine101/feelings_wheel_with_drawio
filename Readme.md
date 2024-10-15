# Feelings Wheel Generator with Draw.io

This project generates an XML representation of a **Feelings Wheel** for various languages. The XML files are compatible with [Draw.io](https://drawio-app.com/), allowing you to visualize the complex emotional structure in a circular format with three levels: Major Emotions, Sub-Emotions, and Sub-Feelings.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [JSON Structure](#json-structure)

## Overview

The **Feelings Wheel** is a psychological tool to help identify, express, and manage emotions. This project takes a JSON input describing different emotional hierarchies across multiple languages and generates corresponding XML files for visualizing these emotions as a circular diagram in Draw.io.

## Features

- Generates **three-level circular diagrams**:
  1. Major Emotions
  2. Sub-Emotions
  3. Sub-Feelings
- Supports **multiple languages**.
- Exports **Draw.io compatible XML** for each language.
- Customizable **colors and sizes** for each level.
- Visualizes the hierarchical structure of emotions, aiding in better emotional understanding.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/amine101/feelings_wheel_with_drawio.git
   ```
2. Navigate to the project directory:

   ```bash
   cd feelings_wheel_with_drawio
   ```

## Usage
1. Prepare your JSON data file that describes the emotional structure. You can use the example feelings_wheel.json in the repository to understand the format.

2. Run the main script:

   ```bash
    python generate_feelings_wheel.py.py
   ```
    This script will generate an XML file for each language described in the JSON file.

3. Open the generated XML files in Draw.io:

    - Navigate to Draw.io.

    - Import the XML file to visualize the Feelings Wheel.
    
    
    ![image](https://github.com/user-attachments/assets/8f7fbdef-6949-47cd-91a8-734044c5a769)


## Configuration

You can adjust various parameters such as the circle's radius, colors, opacity, and font sizes in the *CONFIG* dictionary located at the top of the main script (main.py):

- **center_x, center_y**: The center coordinates for the diagram.

- **text_width, text_height**: Dimensions for the text elements.

- **stroke_color, font_color**: Defines the color of the strokes and fonts.

- **font_sizes**: Controls the font sizes for different levels.

- **default_colors**: Default colors for each level of emotions.

### Levels and Radius:

- **Level 1**: Major Emotions (central circle)
radius: The radius of the circle.
opacity: Opacity level (0-100).

- **Level 2**: Sub-Emotions (middle annulus)
inner_radius, outer_radius: Define the inner and outer bounds of the annulus.
radial_offset: Adjusts the radial position.
opacity: Opacity level (0-100).

- **Level 3**: Sub-Feelings (outer annulus)
inner_radius, outer_radius: Define the inner and outer bounds of the outer annulus.
radial_offset: Adjusts the radial position.
opacity: Opacity level (0-100).


## JSON Structure
The input JSON file (feelings_wheel.json) must follow a specific structure:


```json
{
  "languages": {
    "English": {
      "emotions": {
        "Joy": {
          "sub_emotions": {
            "Excitement": ["Thrilled", "Eager"],
            "Optimism": ["Hopeful", "Enthusiastic"]
          },
          "color": ["#FFD700", "#FFA500", "#FF4500"]
        },
        "Sadness": {
          "sub_emotions": {
            "Grief": ["Sorrow", "Mourning"],
            "Disappointment": ["Let Down", "Frustrated"]
          },
          "color": ["#4682B4", "#4169E1", "#0000FF"]
        }
      }
    }
  }
}
```
### Fields:
- **languages**:
 A dictionary containing languages as keys and corresponding emotional data as values.
- **emotions**: A dictionary of major emotions and their respective sub-emotions.
- **sub_emotions**: Sub-categories of each major emotion, followed by their sub-feelings.
- **color**: A list of three colors (hex format) for each level of emotions.