# Sunburst Chart Generator with DrawIO


## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [JSON Structure](#json-structure)

## Overview

The Sunburst Chart Generator is a Python script designed to create sunburst charts (or wheel diagrams) in [Draw.io](https://drawio-app.com/)  (XML) format from hierarchical JSON data.

## Features
 - **Generate Sunburst Charts:** Create multi-level, circular hierarchical charts based on JSON input.

 - **Customizable Levels:** Define custom configurations for each chart level, including radii, colors, opacities, and font sizes.

 - **Color Adjustment:** Adjust colors automatically for different levels to enhance visual clarity.

 - **Dynamic Text Labeling:** Add text labels to each chart segment with automatic positioning and rotation to maintain readability.

 - **Flexible JSON Input:** Use a structured JSON file to define chart data and configurations.



## Installation


1. **Clone the repository**:
    ```bash
    git clone https://github.com/amine101/sunburst_chart_with_drawio.git
    ```
2. Navigate to the project directory:

   ```bash
   cd sunburst_chart_with_drawio
   ```

## Usage
1. Prepare your JSON data file that describes the emotional structure. You can use the example feelings_wheel.json in the repository to understand the format.

2. Run the main script:

   ```bash
   python generate.py 
   --file INPUT_JSON_FILE 
   [--extension EXTENSION] 
   [--log-level LOG_LEVEL]
   [--output OUTPUT_DIRECTORY]
      ```

    **Arguments**

    - --file: (Required) Path to the input JSON file containing the chart data.
    - --extension: (Optional) Output file extension (drawio or xml). Default is drawio.
    - --log-level: (Optional) Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default is INFO.
    - --output: (Optional) Output directory for the generated files. Default is ./output.

    **Example**

      ```bash
        python generate.py --file data.json --extension drawio --log-level DEBUG --output ./diagrams
      ```

    This command reads data.json, generates the sunburst chart(s), and saves the output .drawio files in the ./diagrams directory with detailed debug logging enabled.


3. Open the generated XML files in Draw.io:

    - Navigate to Draw.io.

    - Import the XML file to visualize the Feelings Wheel.
    
    
    ![image](https://github.com/user-attachments/assets/8f7fbdef-6949-47cd-91a8-734044c5a769)


## Configuration

Customize various aspects of each chart level through the levels_config section in your JSON file.

### Configuration Parameters

- **levels:** Specifies the level(s) the configuration applies to. Accepts an integer, list, or dictionary with from and to keys.

- **radius:** Defines the outer radius ( only for level 1).

- **outer_radius:** Explicitely sets the outer radius of the level (for levels>=1).

- **outer_radius_increment:** Incremental value added to the outer radius from the previous level (for levels>=1).

- **inner_radius:** Explicitely sets the inner radius of the level (for levels>=1).

- **inner_radius_increment:** Incremental value added to the inner radius from the previous level's outer radius (for levels>=1).

- **opacity:** Opacity percentage (0-100) for the chart segments at this level.
font_size: Font size for text labels at this level.

- **default_color:** Default fill color for segments at this level.



**Example Level Configuration**
```json
"levels_config": [
  {
    "levels": 1,
    "radius": 100,
    "opacity": 100,
    "font_size": 12,
    "default_color": "#1f77b4"
  },
  {
    "levels": {"from": 2, "to": 3},
    "outer_radius_increment": 50,
    "opacity": 80,
    "font_size": 10,
    "default_color": "#ff7f0e"
  },
  {
    "levels": {"from": 4},
    "outer_radius_increment": 40,
    "opacity": 60,
    "font_size": 8,
    "default_color": "#2ca02c"
  }
]

```

### Colors

Define colors for each node using the color key. If a node includes a color list, the script uses these colors for the corresponding levels. If not provided, it adjusts the base color automatically for different levels.


## JSON Structure

Your input JSON file must adhere to a specific structure to ensure proper chart generation.

### Top-Level Keys

- **type:** *(Required)* Must be "generic_wheel" for this script.

- **structures:** *(Required)* An array of chart structures to generate.

### Structure of "structures"
Each structure in the "structures" array should contain:

- **name:** *(Required)* The chart's name.

- **nodes:** *(Required)* An array of nodes representing the chart's hierarchical data.

### Node Structure

Each node within nodes can include:

- **label:** *(Required)* Text label for the chart segment.

- **percentage:** *(Optional)* Percentage of the segment relative to its parent (0-100). If omitted, remaining percentage is equally divided among unspecified nodes.

  >**Important**: If specified, ensure that the total percentage of child nodes does not exceed 100% at any level.

- **color:** *(Optional)* Array of colors for each level.

- **sub_nodes:** *(Optional)* Array of child nodes, following the same structure.

```json
{
  "type": "generic_wheel",
  "levels_config": [
    {
      "levels": 1,
      "radius": 100,
      "opacity": 100,
      "font_size": 12,
      "default_color": "#1f77b4"
    },
    {
      "levels": {"from": 2, "to": 3},
      "outer_radius_increment": 100,
      "opacity": 80,
      "font_size": 10,
      "default_color": "#ff7f0e"
    }
  ],
  "structures": [
    {
      "name": "Company Structure",
      "nodes": [
        {
          "label": "Executive",
          "percentage": 20,
          "color": ["#1f77b4"],
          "sub_nodes": [
            {
              "label": "CEO",
              "percentage": 50,
              "color" : ["1BA1E2"],
              "sub_nodes": [
                {"label": "Assistant", "percentage": 70, "color" : ["8FECFF"]}
              ]
            },
            {
              "label": "CFO",
              "color" : ["1BA1E2"],
              "percentage": 50
            }
          ]
        },
        {
          "label": "Operations",
          "percentage": 80,
          "color": ["#ff7f0e"],
          "sub_nodes": [
            {
              "label": "Manufacturing",
              "percentage": 60
            },
            {
              "label": "Logistics",
              "percentage": 40
            }
          ]
        }
      ]
    }
  ]
}


```

### Notes

- **Percentage Validation:** Ensure that the total percentage of child nodes does not exceed 100% at any level.

- **Unspecified Percentages:** 
If percentage is omitted for some nodes, the script automatically divides the remaining percentage equally among them.