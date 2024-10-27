import json
import colorsys
import math
import logging
import argparse
import os
import logging
from drawio import DiagramGenerator
from typing import List

logger=None 

def initialize_logger(log_level):
    logger = logging.getLogger('XMLGeneratorLogger')
    logger.setLevel(log_level)
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    return logger

def _get_config_value( value, level):
    return value(level) if callable(value) else value



class Node:
    def __init__(self, label, **kwargs):
        self.label = label
        self.sub_nodes = []
        self.parent_node = None  # Parent node reference
        self.percentage = kwargs.pop('percentage', None)
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.start_angle = None
        self.end_angle = None
        self.resolved_properties = {}

    def resolve_properties(self, level_config, level_number):
        """
        Resolve properties for this node by considering:
        - Node's own properties
        - Parent node's properties
        - Level configuration
        """
        property_names = [
            'text_rotation', 'text_placement', 'font_size', 'shape_color',
            'text_color', 'shape_opacity', 'text_opacity'
        ]

        # Initialize resolved_properties with an empty dict
        self.resolved_properties = {}

        for prop in property_names:
            parent_value = getattr(self.parent_node, 'resolved_properties', {}).get(prop)
            node_value = getattr(self, prop, None)
            level_value = level_config.get(prop)

            # Handle color properties separately
            if prop in ['shape_color', 'text_color']:
                resolved_value = self.resolve_color_property(
                    prop, node_value, level_value, parent_value, level_number
                )
            else:
                resolved_value = self.resolve_generic_property(
                    prop, node_value, level_value, parent_value, level_number
                )

            self.resolved_properties[prop] = resolved_value

    def resolve_generic_property(self, prop, node_value, level_value, parent_value, level):
        """
        Resolve non-color properties by checking node, level, and parent values.
        """
        if node_value is not None:
            return _get_config_value(node_value, level)
        if level_value is not None:
            return _get_config_value(level_value, level)
        return parent_value  # Inherit from parent if available

    def resolve_color_property(self, prop, node_value, level_value, parent_value, level):
        """
        Resolve color properties with special handling for lists and inheritance.
        """
        # First, check node's own property
        if node_value is not None:
            value = _get_config_value(node_value, level)
            return self._extract_color_from_value(value, level)
        # Next, check level configuration
        if level_value is not None:
            value = _get_config_value(level_value, level)
            return self._extract_color_from_value(value, level)
        # Finally, inherit from parent
        return parent_value

    def _extract_color_from_value(self, value, level):
        """
        Handle color values that might be a list or a single value.
        """
        if isinstance(value, list):
            if len(value) >= level:
                return value[level - 1]
            else:
                return value[-1]
        else:
            return value


class Level:
    def __init__(self, level_number, previous_level=None):
        self.level_number = level_number
        self.nodes = []
        self.level_config = {}
        self.previous_level = previous_level 

    def add_node(self, node):
        self.nodes.append(node)
        node.level = self  #  Set Node level attribute

    def __str__(self):
        return f"Level(level_number={self.level_number}, previous_level={self.previous_level.level_number if self.previous_level else None})"

    @staticmethod
    def default_config(level):
        # Default configuration for levels
        if level == 1:
            return {
                'levels': 1,
                'outer_radius': 100,
                'font_size': 10,
                'shape_color': '#a20025',
                'text_color': '#000000',
                'shape_opacity': 100,
                'text_opacity': 100,
                'text_rotation': 'radial',
                'text_placement': 'centered',
            }
        else:
            return {
                'levels': level,
                'outer_radius_increment': 50,
                'font_size': lambda lvl: max(10 - (lvl - 1), 6),
                'shape_color': lambda lvl: Wheel.adjust_color('#a20025', amount=0.1 * (lvl - 1)),
                'text_color': '#000000',
                'shape_opacity': lambda lvl: max(100 - (lvl - 1) * 10, 30),
                'text_opacity': 100,
                'text_rotation': 'radial',
                'text_placement': 'centered',
            }

    def get_level_config(self, json_levels_config, silent=False):
        # Get default config for the level
        default_level_config = Level.default_config(self.level_number)
        level_config = None
        # Check if there's a configuration for the level in the JSON data
        for config in json_levels_config:
            if self._level_in_config(self.level_number, config.get('levels')):
                if not silent:
                    logger.debug(f"Getting level {self.level_number} config from json data")
                level_config = config.copy()
                break  # Stop after finding the first matching config

        if level_config is None:
            # Use the default config if none found in the JSON
            level_config = default_level_config
            if not silent:
                logger.debug(f"Using default config for level {self.level_number}")
        else:
            # Start with level_config (since level-specific config takes priority)
            merged_config = level_config.copy()
            conflicting_properties = [
                ['outer_radius', 'outer_radius_increment'],
                ['inner_radius', 'inner_radius_increment']
            ]  # List of lists, inner lists contain the properties that conflict with each other

            # Handle radius conflicts for both outer and inner radii
            for conflicting_property_list in conflicting_properties:
                # Check if this is level 1 where increments are not allowed
                if self.level_number == 1:
                    # If any increment property is defined, use the corresponding radius property from default
                    for key in conflicting_property_list:
                        if 'increment' in key and key in level_config:
                            # Override increment with the non-increment default value
                            radius_key = key.replace('_increment', '')
                            if radius_key in default_level_config:
                                merged_config[radius_key] = default_level_config[radius_key]
                                if not silent:
                                    logger.debug(f"[level {self.level_number}]: {radius_key}={default_level_config[radius_key]} (default due to level 1 not accepting increments)")
                else:
                    # For other levels, process the conflicting properties as normal
                    if not any(key in level_config for key in conflicting_property_list):
                        # If none are defined, use the default values
                        for key in conflicting_property_list:
                            if key in default_level_config:
                                value = default_level_config[key]
                                merged_config[key] = value
                                if not silent:
                                    logger.debug(f"[level {self.level_number}]: {key}={value} (default)")
                    else:
                        # Handle the case where properties are present in merged_config
                        for key in conflicting_property_list:
                            if key in merged_config:
                                if not silent:
                                    logger.debug(f"[level {self.level_number}]: {key}={merged_config[key]} (json levels_config)")

            # Merge non-conflicting properties
            for key, value in default_level_config.items():
                if any(key in conflicting_property_list for conflicting_property_list in conflicting_properties):
                    # Skip conflicting properties
                    continue

                # If key not found in level config, use the defaults
                if key not in merged_config:
                    merged_config[key] = value
                    if not silent:
                        logger.debug(f"[level {self.level_number}]: {key}={merged_config[key]} (default)")
                else:
                    if not silent:
                        logger.debug(f"[level {self.level_number}]: {key}={merged_config[key]} (json levels_config)")

            self.level_config = merged_config

        # Prepare the final configuration for the level 
        ## Could need the previous level's config 
        previous_level_config=None
        if self.previous_level:
            previous_level_config = self.previous_level.get_level_config(json_levels_config, silent)
        self.level_config  = self._prepare_level_config(self.level_config, self.level_number, previous_level_config)

        if not silent:
            logger.debug(f"Level {self.level_number} config: {self.level_config }")
        return self.level_config 

    def _level_in_config(self, level_number, levels_entry):
        if levels_entry is None:
            return False
        if isinstance(levels_entry, int):
            return level_number == levels_entry
        elif isinstance(levels_entry, list):
            return level_number in levels_entry
        elif isinstance(levels_entry, dict):
            from_level = levels_entry.get('from', level_number)
            to_level = levels_entry.get('to', level_number)
            return from_level <= level_number <= to_level
        elif callable(levels_entry):
            return levels_entry(level_number)
        else:
            logger.warning(f"Unknown levels format in config: {levels_entry}")
            return False

    def _prepare_level_config(self, config, level, previous_level_config):
        # Prepare level configuration by calculating properties based on the level
        prepared_config = config.copy()
        if level == 1:
            # For Level 1, outer_radius is defined, ensure inner_radius is zero
            prepared_config['inner_radius'] = 0
            prepared_config['outer_radius'] = prepared_config.get('outer_radius')
        else:
            # Get previous level's outer_radius
            prev_outer_radius = previous_level_config['outer_radius']

            # For levels above 1
            # Outer radius
            if "outer_radius" in config and "outer_radius_increment" in config:
                raise ValueError(f"Invalid configuration: both outer_radius and outer_radius_increment are used in level {level}")
            elif "outer_radius_increment" in config:
                outer_increment = _get_config_value(config.get('outer_radius_increment'), level)
                prepared_config['outer_radius'] = prev_outer_radius + outer_increment
            elif "outer_radius" in config:
                prepared_config['outer_radius'] = config.get('outer_radius')
            else:
                raise KeyError(f"Neither 'outer_radius' nor 'outer_radius_increment' were found in the level config of level {level}")

            # Inner radius
            if "inner_radius" in config and "inner_radius_increment" in config:
                raise ValueError(f"Invalid configuration: both inner_radius and inner_radius_increment are used in level {level}")
            elif "inner_radius_increment" in config:
                inner_increment = _get_config_value(config.get('inner_radius_increment'), level)
                prepared_config['inner_radius'] = prev_outer_radius + inner_increment
            elif "inner_radius" in config:
                prepared_config['inner_radius'] = config.get('inner_radius')
            else:
                prepared_config['inner_radius'] = prev_outer_radius  # adjacent to the lower level

            # Validation to ensure inner_radius is not greater than outer_radius
            if prepared_config['inner_radius'] > prepared_config['outer_radius']:
                logger.error(f"inner_radius ({prepared_config['inner_radius']}) cannot be greater than outer_radius ({prepared_config['outer_radius']}) in level {level}")
                raise ValueError(f"Invalid configuration: inner_radius ({prepared_config['inner_radius']}) is greater than outer_radius ({prepared_config['outer_radius']}) in level {level}")

        return prepared_config


class Wheel:
    def __init__(self, center_x, center_y, text_width, text_height, stroke_color, font_color, json_data):
        self.center_x = center_x
        self.center_y = center_y
        self.text_width = text_width
        self.text_height = text_height
        self.stroke_color = stroke_color
        self.font_color = font_color

        if json_data.get('type') not in [ 'percentage_wheel', 'flavor_wheel' ]:
            raise ValueError("Unsupported wheel type. This generator can only handle 'flavor_wheel' or 'percentage_wheel' types.")

        self.structures_list = json_data['structures']
        self.json_levels_config = json_data.get('levels_config', [])
        self.wheel_structures = []

    def _create_wheel_structures(self):
        for structure in self.structures_list:
            structure_name = structure.get('name', 'Unnamed Structure')
            logger.debug(f"========== Creating wheel structure '{structure_name}'")
            # First, create nodes with their sub_nodes
            nodes = self._create_nodes(structure.get('nodes', []))
            # Then, create levels based on the nodes
            levels = self._create_levels_from_nodes(nodes)
            # Assign angles to nodes
            self._assign_node_angles(nodes, start_angle=0.0, end_angle=1.0)
            # Get level configurations
            self._get_levels_config(levels)
            # Append the structure
            self.wheel_structures.append({'name': structure_name, 'levels': levels})
            logger.debug(f"Created wheel structure '{structure_name}' with {len(levels)} levels")

    def _create_nodes(self, nodes_data, parent_node=None):
        nodes = []
        for node_data in nodes_data:
            node_data_copy = node_data.copy()
            label = node_data_copy.pop('label')
            sub_nodes_data = node_data_copy.pop('sub_nodes', [])
            node = Node(label=label, **node_data_copy)
            node.parent_node = parent_node  # Set parent_node
            if sub_nodes_data:
                node.sub_nodes = self._create_nodes(sub_nodes_data, parent_node=node)
            nodes.append(node)
            logger.debug(f"Created node '{node.label}' with {len(node.sub_nodes)} sub-nodes")
        return nodes


    def _create_levels_from_nodes(self, root_nodes):
        levels_dict = {}
        def traverse(node, level_number, previous_level=None, parent_node=None):
            if level_number not in levels_dict:
                levels_dict[level_number] = Level(level_number=level_number, previous_level=previous_level)
                logger.debug(f"Created level {level_number}")
            level = levels_dict[level_number]
            level.add_node(node)
            logger.debug(f"Added node '{node.label}' to level {level_number}")
            node.parent_node = parent_node
            for child_node in node.sub_nodes:
                traverse(child_node, level_number + 1, previous_level=level, parent_node=node)
        for node in root_nodes:
            traverse(node, level_number=1)
        levels = [levels_dict[level_number] for level_number in sorted(levels_dict.keys())]
        return levels


    def _get_levels_config(self, levels: List[Level]):
        for level in levels:
            level.get_level_config(self.json_levels_config)


    def json_to_drawio(self, name):
        logger.debug(f"Generating DrawIO for: {name}")
        # Access the wheel structure for the specified name
        structure = next((entry for entry in self.wheel_structures if entry['name'] == name), None)
        if not structure:
            raise ValueError(f"'{name}' not found in the wheel structures.")
        levels = structure['levels']

        # Initialize the Diagram Generator
        diagram = DiagramGenerator()

        # Start processing levels
        for level in levels:
            self._process_level(level=level, diagram=diagram)

        # Generate and return the XML content
        xml_content = diagram.generate_xml(name)
        return xml_content


    def _process_level(self, level, diagram=None):
        logger.debug(f"Processing Level {level.level_number}, nodes: {[node.label for node in level.nodes]}")

        level_config = level.level_config
        if not level_config:
            logger.debug(f"No configuration found for Level {level.level_number}. Stopping processing.")
            return

        # Process nodes in order of their start_angle
        nodes_in_order = sorted(level.nodes, key=lambda n: n.start_angle if n.start_angle is not None else 0)

        for node in nodes_in_order:
            # Resolve properties for the node
            node.resolve_properties(level_config, level.level_number)

            start_angle = node.start_angle
            end_angle = node.end_angle
            resolved_properties = node.resolved_properties

            # Extract resolved properties
            fill_color = resolved_properties['shape_color']
            shape_opacity = resolved_properties['shape_opacity']
            font_color = resolved_properties['text_color']
            text_opacity = resolved_properties['text_opacity']
            font_size = resolved_properties['font_size']
            rotation_option = resolved_properties['text_rotation']
            placement_option = resolved_properties['text_placement']

            # Get radii from level configuration
            inner_radius = level_config['inner_radius']
            outer_radius = level_config['outer_radius']
            arc_width = 1 - (inner_radius / outer_radius) if level.level_number > 1 else 1


            # Draw shapes
            if start_angle is None or end_angle is None:
                # Skip the node
                logger.info(f"Skipping Node [level:{level.level_number} |label: {node.label}] start_angle= {start_angle}, end_angle= {end_angle}")
                continue

            angle_diff = (end_angle - start_angle) % 1.0
            if angle_diff == 0 or angle_diff == 1.0:
                # Full circle or annulus
                if level.level_number == 1:
                    logger.info(f" Drawing Node [level:{level.level_number} |label: {node.label}]: Circle ")
                    diagram.add_circle(
                        self.center_x, self.center_y, outer_radius,
                        fill_color, self.stroke_color, shape_opacity
                    )
                else:
                    logger.info(f" Drawing Node [level:{level.level_number} |label: {node.label}]: Annulus ")
                    diagram.add_annulus(
                        self.center_x, self.center_y, outer_radius, inner_radius,
                        fill_color, self.stroke_color, shape_opacity
                    )
            else:
                # Slices
                if level.level_number == 1:
                    logger.info(f" Drawing Node [level:{level.level_number} |label: {node.label}]: Pie Slice    : {start_angle} - {end_angle}")
                    diagram.add_pie_slice(
                        self.center_x, self.center_y, outer_radius,
                        start_angle, end_angle,
                        fill_color, self.stroke_color, shape_opacity
                    )
                else:
                    logger.info(f" Drawing Node [level:{level.level_number} |label: {node.label}]: Annulus Slice : {start_angle} - {end_angle}")
                    diagram.add_annulus_slice(
                        self.center_x, self.center_y, outer_radius, arc_width,
                        start_angle, end_angle,
                        fill_color, self.stroke_color, shape_opacity
                    )

            # Calculate mid-angle
            mid_angle = Wheel.calculate_mid_angle(start_angle, end_angle)
            mid_angle_deg = (mid_angle * 360.0) - 90.0
            if mid_angle_deg < 0:
                mid_angle_deg += 360.0

            # Compute rotation and position
            rotation = self.compute_text_rotation_option(rotation_option, mid_angle_deg)
            x_text, y_text = self.compute_text_position_option(
                placement_option, self.center_x, self.center_y,
                inner_radius, outer_radius, mid_angle_deg,
                self.text_width, self.text_height
            )

            # Add text element
            diagram.add_text_element(
                node.label, x_text, y_text,
                self.text_width, self.text_height, rotation,
                font_size, font_color, text_opacity
            )    

    def compute_text_rotation_option(self, rotation_option, mid_angle_deg):
        if isinstance(rotation_option, dict) and rotation_option.get('type') == 'constant':
            # User specified a constant angle
            rotation = rotation_option.get('angle', 0)
        elif rotation_option == 'horizontal':
            rotation = 0
        elif rotation_option == 'vertical':
            rotation = 90
        elif rotation_option == 'radial':
            rotation = Wheel.compute_text_rotation(mid_angle_deg)
        elif rotation_option == 'perpendicular':
            # Pure Tangential: Text is aligned tangentially without concern for readability
            rotation = (mid_angle_deg + 90) % 360
        elif rotation_option == 'perpendicular_upright':
            # Tangential Upright: Text is aligned tangentially but adjusted to be upright
            rotation = (mid_angle_deg + 90) % 360
            # Ensure text is upright
            if 90 < rotation <= 270:
                rotation = (rotation + 180) % 360
        else:
            # Default to radial
            rotation = Wheel.compute_text_rotation(mid_angle_deg)
        return rotation

    def compute_text_position_option(self, placement_option, center_x, center_y, inner_radius, outer_radius, mid_angle_deg, text_width, text_height):
        if placement_option == 'outside':
            # Place text outside the outer radius
            r_text = outer_radius + text_height / 2 + 5  # Add an offset
        elif placement_option == 'inside_top':
            # Place text at the inner edge of the outer circle
            r_text = outer_radius - text_height / 2
        elif placement_option == 'centered':
            # Place text in the middle of the node
            r_text = (inner_radius + outer_radius) / 2
        else:
            # Default to centered
            r_text = (inner_radius + outer_radius) / 2

        x_text, y_text = Wheel.calculate_positions(center_x, center_y, r_text, mid_angle_deg, text_width, text_height)
        return x_text, y_text


    @staticmethod
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))

    @staticmethod
    def rgb_to_hex(rgb_tuple):
        rgb_tuple = [max(0, min(1, c)) for c in rgb_tuple]
        return '#' + ''.join(f'{int(c*255):02X}' for c in rgb_tuple)

    @staticmethod
    def adjust_color(color, amount=0.0):
        rgb = Wheel.hex_to_rgb(color)
        h, l, s = colorsys.rgb_to_hls(*rgb)
        l = max(0, min(1, l + amount))
        rgb_new = colorsys.hls_to_rgb(h, l, s)
        return Wheel.rgb_to_hex(rgb_new)

    @staticmethod
    def calculate_mid_angle(start_angle, end_angle):
        if end_angle < start_angle:
            end_angle += 1.0  # Adjust for wrapping around
        mid_angle = (start_angle + end_angle) / 2.0
        if mid_angle >= 1.0:
            mid_angle -= 1.0  # Normalize back to range [0, 1)
        return mid_angle

    @staticmethod
    def compute_text_rotation(mid_angle_deg):
        # Ensure text is upright
        if 90 < mid_angle_deg <= 270:
            rotation = mid_angle_deg + 180  # Flip text to keep upright
        else:
            rotation = mid_angle_deg
        return rotation % 360  # Ensure rotation is between 0 and 360

    @staticmethod
    def calculate_positions(center_x, center_y, radius, angle_deg, text_width, text_height):
        x = center_x + radius * math.cos(math.radians(angle_deg)) - text_width / 2
        y = center_y + radius * math.sin(math.radians(angle_deg)) - text_height / 2
        return x, y

    @staticmethod
    def calculate_angle_per_section(total_angle, num_sections):
        return total_angle / num_sections



class FlavorWheel(Wheel):
    def __init__(self, center_x, center_y, text_width, text_height, stroke_color, font_color, json_data):
        super().__init__(center_x, center_y, text_width, text_height, stroke_color, font_color, json_data)
        if json_data.get('type') != 'flavor_wheel':
            raise ValueError("Unsupported wheel type. This generator can only handle 'flavor_wheel' type.")


        # Create wheel structures
        self._create_wheel_structures()

    def _assign_node_angles(self, nodes, start_angle, end_angle):
        total_angle = (end_angle - start_angle) % 1.0
        if total_angle <= 0:
            total_angle += 1.0  # Ensure positive total angle

        # First, compute the total number of leaf nodes under the nodes
        total_leaves = sum(self._count_leaves(node) for node in nodes)
        current_angle = start_angle

        for node in nodes:
            node_leaves = self._count_leaves(node)
            angle_span = total_angle * (node_leaves / total_leaves)
            node.start_angle = current_angle
            node.end_angle = (current_angle + angle_span) % 1.0

            # Recursively assign angles to sub_nodes
            if node.sub_nodes:
                self._assign_node_angles(node.sub_nodes, node.start_angle, node.end_angle)
            current_angle = node.end_angle

    def _count_leaves(self, node):
        if not node.sub_nodes:
            return 1
        else:
            return sum(self._count_leaves(child) for child in node.sub_nodes)


class PercentageWheel(Wheel):
    def __init__(self, center_x, center_y, text_width, text_height, stroke_color, font_color, json_data):
        logger.debug("Initializing Percentage Wheel with provided JSON data")
        super().__init__(center_x, center_y, text_width, text_height, stroke_color, font_color, json_data)
        if json_data.get('type') != 'percentage_wheel':
            raise ValueError("Unsupported wheel type. This generator can only handle 'percentage_wheel' type.")

        # Create wheel structures
        self._create_wheel_structures()

    def _assign_node_angles(self, nodes, start_angle, end_angle):
        total_angle = (end_angle - start_angle) % 1.0
        if total_angle <= 0:
            total_angle += 1.0  # Ensure positive total angle

        # Firt calculate the percentages of the Nodes 
        #========================================
        total_specified_percentage = sum(node.percentage for node in nodes if node.percentage and node.percentage > 0)
        unspecified_nodes = [node for node in nodes if node.percentage is None ]
        total_unspecified_nodes = len(unspecified_nodes)
        if total_specified_percentage > 100:
            raise ValueError(f"Total specified percentage exceeds 100%")

        remaining_percentage = 100 - total_specified_percentage

        current_angle = start_angle

        for node in nodes:
            if node.label == 'Level2_Node4':
                logger.warning(f"Node '{node.label}' has percentage {node.percentage}")
            if node.percentage is None :
                logger.debug(f"Node '{node.label}' has no percentage specified. Assigning percentage based on remaining percentage {remaining_percentage} and total unspecified nodes {total_unspecified_nodes}")
                node.percentage = remaining_percentage / total_unspecified_nodes if total_unspecified_nodes > 0 else 0


        # Second assign the angles
        #========================================

        # Check if any node has 100% percentage
        nodes_with_100_percent = [node for node in nodes if node.percentage == 100]
        if nodes_with_100_percent:
            #if len(nodes_with_100_percent) > 1:
            #    raise ValueError(f"Total specified percentage exceeds 100%")
            # Only assign angles to the node with 100% percentage
            node = nodes_with_100_percent[0] 
            node.start_angle = start_angle
            node.end_angle = end_angle
            logger.debug(f"Assigned angles to node '{node.label}' (100%): start_angle={node.start_angle}, end_angle={node.end_angle}")
            # Recursively assign angles to sub_nodes
            if node.sub_nodes:
                self._assign_node_angles(node.sub_nodes, node.start_angle, node.end_angle)
            # Other nodes will not be assigned angles
            for other_node in nodes:
                if other_node != node:
                    logger.debug(f"Skipping node '{other_node.label}' at this level due to 100% node '{node.label}'")
            return
        else:
            for node in nodes:
                if node.percentage == 0:
                    logger.debug(f"Skipping node '{node.label}' at this level due to 0% percentage")
                    continue
                angle_proportion = node.percentage / 100.0
                angle_span = total_angle * angle_proportion
                node.start_angle = current_angle
                if current_angle + angle_span == 1.0:
                    node.end_angle = 1.0
                else:
                    node.end_angle = (current_angle + angle_span) % 1.0


                logger.debug(f"Assigned angles to node '{node.label}': start_angle={node.start_angle}, end_angle={node.end_angle}")

                # Recursively assign angles to sub_nodes
                if node.sub_nodes:
                    self._assign_node_angles(node.sub_nodes, node.start_angle, node.end_angle)

                current_angle = node.end_angle

                #if node.percentage == 0:
                #    total_unspecified_nodes -= 1
                #    remaining_percentage -= node_percentage



def main():
    global logger

    # Argument Parsing
    # ---------------------------
    parser = argparse.ArgumentParser(description="Generate XML drawio output from a JSON file.")
    parser.add_argument('--file', required=True, help='The input JSON file path')
    parser.add_argument('--extension', required=False, default='drawio', 
                        choices=['drawio', 'xml'], 
                        help='The output file extension (default: .drawio)')
    parser.add_argument('--log-level', required=False, default='INFO', 
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], 
                        help='Set the logging level (default: INFO)')
    parser.add_argument('--output', required=False, default='./output', 
                        help='The output folder where the generated XML/drawio files will be saved (default: ./output)')

    args = parser.parse_args()

    log_level = getattr(logging, args.log_level.upper(), logging.DEBUG)
    logger = initialize_logger(log_level)

    # JSON Loading
    # -----------------------
    input_filepath = args.file
    filename_without_extension = os.path.splitext(os.path.basename(input_filepath))[0]
    
    try:
        with open(input_filepath, 'r', encoding='utf-8') as json_file:
            json_data = json.load(json_file)
            logger.info(f"Successfully loaded JSON data from {input_filepath}")
    except Exception as e:
        logger.error(f"Failed to load JSON file: {input_filepath} - Error: {e}")
        exit(1)

    # Output Directory Handling
    # ------------------------------------
    output_folder = args.output
    if not os.path.exists(output_folder):
        try:
            os.makedirs(output_folder)
            logger.info(f"Created output directory: {output_folder}")
        except Exception as e:
            logger.error(f"Failed to create output directory: {output_folder} - Error: {e}")
            exit(1)

    # Dynamically choose the wheel class based on 'type' in JSON
    # ------------------------------------
    wheel_type = json_data.get('type')
    if wheel_type == 'flavor_wheel':
        generator = FlavorWheel(320, 290, 80, 30, '#808080', '#000000', json_data)
    elif wheel_type == 'percentage_wheel':
        generator = PercentageWheel(320, 290, 80, 30, '#808080', '#000000', json_data)
    else:
        logger.error(f"Unsupported wheel type: {wheel_type}")
        exit(1)

    # XML Generation and Output
    # ------------------------------------
    for entry in generator.structures_list:
        entry_name = entry['name']
        logger.debug(f"Starting XML generation for: {entry_name}")
        
        try:
            xml_output = generator.json_to_drawio(entry_name)

            output_extension = args.extension 
            output_filename = os.path.join(output_folder, f"{filename_without_extension}_{entry_name}.{output_extension}")

            with open(output_filename, "w", encoding='utf-8') as file:
                file.write(xml_output)

            logger.info(f"XML representation for {entry_name} has been written to {output_filename}")
            print(f"XML representation for {entry_name} has been written to {output_filename}")
        
        except Exception as e:
            logger.error(f"Failed to generate or write XML for {entry_name}: {e}", exc_info=True)


if __name__ == "__main__":
    main()