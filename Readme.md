# Sunburst Chart Generator with DrawIO


## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [JSON Structure](#json-structure)

## Overview


The Sunburst Chart Generator is a Python script designed to create sunburst charts (or wheel diagrams) in [Draw.io](https://drawio-app.com/) (XML) format from hierarchical JSON data. It supports two types of wheels:

  - **Percentage Wheel:** Generates a sunburst chart where each node's angular width is determined by its specified percentage.

  - **Flavor Wheel:** Generates a sunburst chart where all nodes at the deepest level (outermost nodes) have equal angular widths, and the angular widths of inner nodes are determined by the sum of their descendant leaf nodes.


## Features
 - **Generate Sunburst Charts:** Create multi-level, circular hierarchical charts based on JSON input.

 - **Support for Two Wheel Types:** Generate either a Percentage Wheel or a Flavor Wheel, depending on your data and requirements.

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


## Shape Types


The wheel diagram supports various shape types based on the radii values:

- **Circle:**  
  - **Description:** A complete circle representing a single "central" node without subdivisions.
  - **Radii Requirements:** Defined only by `outer_radius`.
  - **Used on level:** 1
  - **Used when:**  there is a single node at level 1 with 100% percentage.

- **Pie Slice:**  
  - **Description:** A sector of a circle representing a node's portion of the wheel.
  - **Radii Requirements:** Defined only by `outer_radius`.
  - **Used on level:** 1
  - **Used when:**  the node has a percentage < 100%

- **Annulus:**  
  - **Description:** A ring shape representing a level with a defined `inner_radius` and `outer_radius`.
  - **Radii Requirements:** Both `inner_radius` and `outer_radius` must be set.
  - **Used on level:** >=2
  - **Used when:**  it's parent node covers the full possible angular width of 2Pi ( means all the parent nodes have 100% percentage ) and the current node have 100% percentage 

- **Annulus Slice:**  
  - **Description:** A sector of an annulus representing a node's portion within a concentric ring.
  - **Radii Requirements:** Both `inner_radius` and `outer_radius` are set, and the slice is a portion of the annular area.
  - **Used on level:** >=2
  - **Used when:**  there are more than 1 node at the level 


## Configuration

This section provides a detailed description of the configuration parameters that can be set at different levels of the hierarchy:
  - Actual node
  - Actual level
  - Parent Node
  - Default

### Parameters 


| Parameter       | Applicable Wheel Type | Settable At      | Possible Values / Examples                       | Description |
|-----------------|-----------------------|------------------|--------------------------------------------------|-------------|
| `percentage`    | Percentage Wheel                   | Node             | `integer` (0 to 100)                             | **(Percentage Wheel Only)** Defines the percentage of the parent node's angular width that the current node will occupy. Example: `50` means the node takes up 50% of the parent's angle. If not defined, the remaining space is evenly distributed among unspecified nodes. |
| `font_size`     | All                   | Node, Level, Parent Node (Inherited)      | `integer`, `lambda` function                     | Defines the size of the text for a node. Can be a fixed number or calculated dynamically. Example: `10` or `lambda lvl: max(10 - (lvl - 1), 6)`. |
| `shape_color`   | All                   | Node, Level, Parent Node (Inherited) | Hex color string, `lambda` function             | Sets the color of the node's shape. Example: `'#a20025'`, or `lambda lvl: Wheel.adjust_color('#a20025', amount=0.1 * (lvl - 1))`. |
| `text_color`    | All                   | Node, Level, Parent Node (Inherited) | Hex color string                                | Sets the color of the node's text. Example: `'#000000'`. |
| `font_size`     | All                   | Node, Level      | `integer`, `lambda` function                     | Defines the size of the text for a node. Can be a fixed number or calculated dynamically. Example: `10` or `lambda lvl: max(10 - (lvl - 1), 6)`. |
| `shape_color`   | All                   | Node, Level, Parent Node (Inherited) | Hex color string, `lambda` function             | Sets the color of the node's shape. Example: `'#a20025'`, or `lambda lvl: Wheel.adjust_color('#a20025', amount=0.1 * (lvl - 1))`. |
| `text_color`    | All                   | Node, Level, Parent Node (Inherited) | Hex color string                                | Sets the color of the node's text. Example: `'#000000'`. |
| `shape_opacity` | All                   | Node, Level, Parent Node (Inherited) | `integer` (0 to 100), `lambda` function         | Sets the opacity of the shape. Example: `100` for fully opaque, or `lambda lvl: max(100 - (lvl - 1) * 10, 30)`. |
| `text_opacity`  | All                   | Node, Level, Parent Node (Inherited) | `integer` (0 to 100)                            | Sets the opacity of the text. Example: `100` for fully opaque. |
| `text_rotation` | All                   | Node, Level, Parent Node (Inherited) | `horizontal`, `vertical`, `radial`, `perpendicular`, `perpendicular_upright`, `constant` (`{'type': 'constant', 'angle': 45}`)                                        | Controls how the text is rotated. Can be set explicitly or inherited. |
| `text_placement`| All                   | Node, Level, Parent Node (Inherited) | `outside`, `inside_top`, `centered`                                         | Controls where the text is placed within the shape. |
| `inner_radius`  | Concentric           | Level  >=2          | `float`, `lambda` function                       | Sets the inner radius of the node's shape in concentric layouts. Example: `100` or `lambda lvl: prev_outer_radius + 20`. |
| `outer_radius`  | Concentric           | Level (all)          | `float`, `lambda` function                       | Sets the outer radius of the node's shape. Example: `100` or `lambda lvl: prev_outer_radius + 50`. |
| `outer_radius_increment` | Concentric   | Level >=2   | `float`, `lambda` function                       | Increases the outer radius based on the previous level. Example: `50` or `lambda lvl: 40 + lvl * 5`. |
| `inner_radius_increment` | Concentric   | Level >=2  | `float`, `lambda` function                       | Increases the inner radius based on the previous level. Example: `20` or `lambda lvl: 10 + lvl * 2`. |


#### `percentage`:

* **Percentage Wheel:**

  The `percentage` parameter controls the **angle width** that a node occupies relative to its parent node's space. It defines how much of the parent node's angular area is dedicated to each of its sub-nodes. The sum of the `percentage` values for all sub-nodes under a parent node must not exceed 100%, as they represent portions of the parent's total angle width.

  When `percentage` is not explicitly defined for a node, the remaining available angle width (based on the parent's space) is distributed evenly among the nodes without a specified percentage.

  - **Explicit `percentage`:** Defines the exact angle width a node should occupy. For example, if a node has a `percentage` of 30%, it will occupy 30% of the parent node’s angle.
    
  - **Implicit `percentage`:** If some sub-nodes have their `percentage` set and others do not, the system subtracts the total specified percentage from 100% and distributes the remaining space equally among the unspecified nodes.
    
  - **No `percentage`:** If no sub-nodes under a parent node have a defined `percentage`, they will equally divide the parent's total angular area.

  ##### Example:
  - If a parent node has 4 sub-nodes, and two of them have their `percentage` set to 30% and 20%, the remaining two sub-nodes will share the leftover 50% of the parent's angular width, each receiving 25%.
  - If no sub-nodes have a defined `percentage`, each sub-node will receive an equal share of the parent's space. For example, if there are 4 sub-nodes, each will receive 25% of the parent's angle width.

  This percentage system ensures that each node's angular size in the diagram reflects its proportionate importance or size in relation to its parent node.

* **Flavor Weel:** 

  All the nodes percentages will be ignored, the nodes on the deepest level will get uniform angles.

#### `text_rotation`:

- `horizontal`: The text will always be displayed horizontally, no matter the orientation of the node.
- `vertical`: The text will always be displayed vertically.
- `radial`: The text will follow the radial direction of the shape (aligned along the radius).
- `perpendicular`: The text will be aligned tangentially to the shape without adjustment for readability.
- `perpendicular_upright`: The text will be aligned tangentially but adjusted to remain upright.
- `constant`: A specific constant angle can be provided (e.g., `{'type': 'constant', 'angle': 45}`).


#### `text_placement` :

- `outside`: The text is placed outside the outer radius of the node.
- `inside_top`: The text is placed inside the outer radius, aligned to the inner edge.
- `centered`: The text is placed in the center of the node (default).


#### `inner_radius` :

- **Defined for:** Levels 2 and above.
- **Default Value:** For Level 1, `inner_radius` is always 0. For other levels, it defaults to the `outer_radius` of the previous level.
- **Description:** This parameter sets the inner edge of a shape when there are multiple levels, such as annuli or slices. 
- **Example:** `0.5` or `lambda lvl: prev_outer_radius + 20`.
- **Shape Type:** Used for annulus or annulus slices, where it defines the boundary between the outer radius of the current and the previous level.
- **Note:** Cannot be set alongside `inner_radius_increment`; if both are defined, it will raise a conflict.


#### `outer_radius` :

- **Defined for:** All levels.
- **Default Value:** For Level 1, it's equal to `radius`. For Levels 2 and above, it should be defined explicitly or calculated based on `outer_radius_increment`.
- **Description:** Defines the outer edge of the shape. This is the size of the circle, annulus, or pie slice's outer boundary.
- **Example:** `1.0` or `lambda lvl: prev_outer_radius + 50`.
- **Shape Type:** Applies to circles, annuli, pie slices, or annulus slices.
- **Note:** If both `outer_radius` and `outer_radius_increment` are defined, the system raises a conflict, and only one should be used.


#### `outer_radius_increment` :

- **Defined for:** Levels 2 and above.
- **Default Value:** Increments by a value defined by the user, often `50`. 
- **Description:** Adds an increment to the `outer_radius` from the previous level, creating larger concentric rings (annuli) or slices.
- **Example:** `lambda lvl: 40 + lvl * 5`.
- **Shape Type:** Annulus or annulus slices.
- **Note:** Conflicts arise if both `outer_radius` and `outer_radius_increment` are defined; the system allows only one method of defining the outer boundary.

#### `inner_radius_increment` :

- **Defined for:** Levels 2 and above.
- **Default Value:** It defaults to a value based on the `outer_radius` of the previous level.
- **Description:** Increases the `inner_radius` value, which shifts the inner boundary outward in concentric layouts like annuli.
- **Example:** `lambda lvl: 10 + lvl * 2`.
- **Shape Type:** Annulus or annulus slices.
- **Note:** Conflicts arise if both `inner_radius` and `inner_radius_increment` are defined. Only one should be set at a time.





### Inheritance Behavior

Inheritance in the configuration system allows for efficient reuse of settings across multiple levels and nodes. When a parameter is not explicitly set at a given level or node, it will inherit the value from its parent configuration. If the parameter is not set in the parent, it will use the default configuration for the level.

#### Inheritance Rules:
1. **Node-level Parameters**: These are given the highest priority. If a parameter is defined at the node level, it will override both level and inherited values.
2. **Level-specific Parameters**: If not defined at the node level, the system will check for the parameter in the level configuration.
3. **Parent Inheritance**: If not set at either node or level, the value will inherit from its parent level or node, moving upward in the hierarchy.
4. **Default Values**: If no value is found through inheritance, the default values provided for the level will be used.

#### Example of Inheritance:
- `text_rotation` is set to `radial` at Level 1. Nodes at Level 1 will use this value unless overridden at the node level. If a node in Level 2 has no `text_rotation` defined, it will inherit from Level 1 unless explicitly set at Level 2.

By leveraging this inheritance structure, configurations can be customized at any level while maintaining flexibility and consistency throughout the diagram.



## JSON Structure

The `GenericWheel` class expects a specific JSON structure as input. This JSON structure defines the type of wheel, the configurations for each level, and the nodes that will be rendered in the diagram.

### Overall Structure
```json
{
  "type": "percentage_wheel", // or "flavor_wheel",
  "structures": [
    {
      "name": "Example Name",
      "nodes": [
        {
          "label": "Node Label",
          "percentage": 50,   // Used For percentage_wheel only
          "sub_nodes": []
        }
      ]
    }
  ],
  "levels_config": [
    {
      "levels": 1,
      "radius": 100,
      "font_size": 10,
      "shape_color": "#FF0000",
      "text_color": "#000000"
    }
  ]
}
```

As you can see, the json file must have the following fields:
- **`type`**

- **`structures`** 

- **`levels_config`** 

### Type

#### `percentage_wheel`  :

 - **Usage of percentage:** The percentage parameter is used to define the angular width of nodes.

 - **Angle Calculation:** For each set of sibling nodes (node with the same parent node),  the angular widths are determined by their specified percentages. If percentage is not specified, the remaining angular space is distributed equally among unspecified nodes.


#### `flavor_wheel` :

 - **Usage of percentage:** The percentage parameter is ignored.

- **Angle Calculation:** All leaf nodes (nodes without sub-nodes at the deepest level) have equal angular widths. Inner nodes' angular widths are determined by the sum of their descendant leaf nodes.



### Structure 

  A list where each structure in the list represents a separate wheel, with its own set of nodes and levels, all of them share the same `levels_config`
  
   Here's an overview of the fields:

  - **name**: A unique name for the wheel. It is used to reference and generate the wheel.

    Will be used as the **filename** for the generated `.drawio` file, and the nodes array defines the structure and content of the chart. This approach allows multiple charts using a single common levels configuration and all defined within a single JSON input file.


  - **nodes**: An array that defines the nodes (or sections) of the wheel. Each node represents a slice of the wheel at a certain level, and can have nested `sub_nodes` for multi-level wheels.


  ```json
"structures": [
  {
    "name": "Wheel 1",
    "nodes": [
      {
        "label": "Node Label",
        "sub_nodes": [
          {
            "label": "Sub Node Label",
          }
        ]
      }
    ]
  },

  {
    "name": "Wheel 2",
    "nodes": [
      {
        "label": "Node Label",
        "sub_nodes": [
          {
            "label": "Sub Node Label",
          }
        ]
      }
    ]
  }

]
  ```

### Nodes

The `nodes` array defines the structure of nodes and sub-nodes in the wheel. Each node represents a section or slice of the wheel, and nodes can have nested sub-nodes to represent additional levels. Here’s a breakdown of the fields, with required and optional parameters:

- **`label` (required):** The text label to be displayed for this node.
- **`percentage` (optional, Percentage Wheel only):** Specifies the percentage of the wheel that this node should occupy.

- **`sub_nodes` (optional):** An array of sub-nodes that belong to this node. Each sub-node has the same structure as a node and can be nested further for deeper levels.

#### Optional Config Parameters for Each Node:
These are config parameters that can be set on individual nodes, allowing customization of the appearance or behavior at the node level. If not specified, the values will be inherited from the `levels_config`.

- **`font_size` (optional):** Sets the font size for this specific node.
- **`shape_color` (optional):** Sets the shape color for this specific node.
- **`text_color` (optional):** Sets the text color for this specific node.
- **`shape_opacity` (optional):** Sets the opacity level for the shape.
- **`text_opacity` (optional):** Sets the opacity level for the text.
- **`text_rotation` (optional):** Defines how the text is rotated.
- **`text_placement` (optional):** Defines where the text will be placed.




#### Example Node Entry:

- Example Node Entry for ***Percentage Wheel:***
  ```json
  {
    "label": "Node A",
    "percentage": 50,
    "font_size": 12,
    "shape_color": "#00ff00",
    "text_color": "#000000",
    "shape_opacity": 80,
    "text_opacity": 100,
    "text_rotation": "radial",
    "text_placement": "centered",
    "sub_nodes": [
      {
        "label": "Sub Node A1",
        "percentage": 50
      }
    ]
  }
  ```
 - Example Node Entry for ***Flavor Wheel:***
    ```json
    {
      "label": "Node A",
      "font_size": 12,
      "shape_color": "#00ff00",
      "text_color": "#000000",
      "shape_opacity": 80,
      "text_opacity": 100,
      "text_rotation": "radial",
      "text_placement": "centered",
      "sub_nodes": [
        {
          "label": "Sub Node A1"
        }
      ]
    }
    ```




### levels_config 

The `levels_config` section in the JSON input allows you to define configuration settings for different levels of the wheel. Each configuration can specify details like radius increments, colors, font size, and opacity for the elements at a specific level. If no configuration is provided for a level (and none in the node itself), default settings will be applied.


#### Fields:

- **levels:** (Required) Defines the levels where this configuration applies. It can take several forms:
  - A single integer (e.g., `1`) for a specific level.
  - A list of integers (e.g., `[1, 2, 3]`) to apply the configuration to multiple levels.
  - A dictionary with `from` and `to` fields (e.g., `{"from": 1, "to": 3}`) for a range of levels.
  - A dictionary with only`from` field (e.g., `{"from": 5}`) for levels >= a certain number.

- **outer_radius:** (optional) The absolute outer radius for the given level. If defined, it overrides any radius increments for this level.

- **outer_radius_increment:** (optional) The amount by which the outer radius should increase compared to the previous level. It is used when `outer_radius` is not defined. 

- **inner_radius:** (optional) The absolute inner radius for the given level. 

- **inner_radius_increment:** (optional) The amount by which the inner radius should increase compared to the previous level’s outer radius. It is used when `inner_radius` is not defined.

- **font_size:** (optional) Defines the font size for text labels in this level. This can either be a fixed integer (e.g., `12`) or a function that returns the font size based on the level.

- **shape_color:** (optional) Specifies the color of the shapes (segments) in the given level. It can be a hexadecimal color string (e.g., `#FF5733`) or a function that returns the color based on the level.

- **text_color:** (optional) Specifies the color of the text labels in this level. It can be a fixed color (e.g., `#FFFFFF`) or a function based on the level.

- **shape_opacity:** (optional) Determines the opacity of the shapes (segments) in this level. This can be a value between `0` and `100`, or a function returning the opacity based on the level.

- **text_opacity:** (optional) Determines the opacity of the text in this level. Like `shape_opacity`, it can be a value between `0` and `100`.

- **text_rotation:** (optional) Controls how the text is rotated. This can be:
  - `"radial"` (default) to rotate text radially.
  - `"horizontal"` to keep text horizontally aligned.
  - `"vertical"` to rotate text vertically.
  - `"perpendicular"` for tangential alignment.
  - `"perpendicular_upright"` for tangential alignment with upright orientation.

- **text_placement:** (optional) Specifies where to place the text within the segment. Common values include:
  - `"centered"` (default): Places the text in the center of the segment.
  - `"outside"`: Positions the text outside the segment.
  - `"inside_top"`: Positions the text near the inner edge of the segment.

#### Example of a `levels_config` Entry:

```json
{
"levels_config": [
  {
    "levels": 1,
    "outer_radius": 100,
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
  },
  {
    "levels": {"from": 4},
    "outer_radius_increment": 120,
    "opacity": 60,
    "font_size": 8,
    "default_color": "#2ca02c"
  }
]
}
```
