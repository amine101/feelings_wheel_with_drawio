import json
import colorsys
import math
import logging
import argparse
import os
import logging

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

class Wheel:
    def __init__(self, center_x, center_y, text_width, text_height, stroke_color, font_color):
        self.center_x = center_x
        self.center_y = center_y
        self.text_width = text_width
        self.text_height = text_height
        self.stroke_color = stroke_color
        self.font_color = font_color

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

class DiagramGenerator:
    def __init__(self):
        self.shapes = []
        self.id_counter = 2  # Start from 2 since 0 and 1 are used
        self.root_cells = [
            '<mxCell id="0"/>',
            '<mxCell id="1" parent="0"/>',
        ]

    def add_pie_slice(self, center_x, center_y, radius, start_angle, end_angle, fill_color, stroke_color, opacity):
        shape_xml = (
            f'<mxCell id="{self.id_counter}" value="" '
            f'style="shape=mxgraph.basic.pie;fillColor={fill_color};strokeColor={stroke_color};opacity={opacity};startAngle={start_angle};endAngle={end_angle};" '
            f'vertex="1" parent="1">\n'
            f'<mxGeometry x="{center_x - radius}" y="{center_y - radius}" width="{2 * radius}" height="{2 * radius}" as="geometry"/>\n'
            f'</mxCell>\n'
        )
        self.shapes.append(shape_xml)
        self.id_counter += 1
        return self.id_counter - 1  # Return the ID of the shape

    def add_annulus_slice(self, center_x, center_y, outer_radius, arc_width, start_angle, end_angle, fill_color, stroke_color, opacity):
        shape_xml = (
            f'<mxCell id="{self.id_counter}" value="" '
            f'style="shape=mxgraph.basic.partConcEllipse;fillColor={fill_color};strokeColor={stroke_color};opacity={opacity};startAngle={start_angle};endAngle={end_angle};arcWidth={arc_width};" '
            f'vertex="1" parent="1">\n'
            f'<mxGeometry x="{center_x - outer_radius}" y="{center_y - outer_radius}" width="{2 * outer_radius}" height="{2 * outer_radius}" as="geometry"/>\n'
            f'</mxCell>\n'
        )
        self.shapes.append(shape_xml)
        self.id_counter += 1
        return self.id_counter - 1  # Return the ID of the shape

    def add_text_element(self, text, x, y, width, height, rotation, font_size, font_color):
        shape_xml = (
            f'<mxCell id="{self.id_counter}" value="{text}" '
            f'style="text;html=1;align=center;verticalAlign=middle;fontSize={font_size};rotation={rotation};fontColor={font_color};" '
            f'vertex="1" parent="1">\n'
            f'<mxGeometry x="{x}" y="{y}" width="{width}" height="{height}" as="geometry"/>\n'
            f'</mxCell>\n'
        )
        self.shapes.append(shape_xml)
        self.id_counter += 1
        return self.id_counter - 1  # Return the ID of the text element

    def generate_xml(self, name):
        xml_content = (
            '<mxfile host="Electron">\n'
            f'<diagram name="Generic Wheel - {name}">\n'
            '<mxGraphModel>\n'
            '<root>\n'
        )
        xml_content += '\n'.join(self.root_cells) + '\n'
        xml_content += ''.join(self.shapes)
        xml_content += '</root>\n</mxGraphModel>\n</diagram>\n</mxfile>'
        return xml_content

class GenericWheel(Wheel):
    def __init__(self, center_x, center_y, text_width, text_height, stroke_color, font_color, json_data):
        super().__init__(center_x, center_y, text_width, text_height, stroke_color, font_color)
        if json_data.get('type') != 'generic_wheel':
            raise ValueError("Unsupported wheel type. This generator can only handle 'generic_wheel' type.")

        self.structures_list = json_data['structures']
        self.json_levels_config = json_data.get('levels_config', [])
        self.base_radius = 100  # Base radius for Level 1



    def get_level_config(self, level, silent=False):
        # First, check if there's a configuration for the level in the JSON data
        prepared_config={}
        for config in self.json_levels_config:
            if self._level_in_config(level, config.get('levels')):
                if not silent:
                    logger.debug(f"Getting level {level} config from json data")
                prepared_config= self._prepare_level_config(config, level)

        if not prepared_config:
            # If no configuration found, use the default configuration function
            prepared_config=self._prepare_level_config(self.default_config(level), level)
            if not silent:
                logger.debug(f"Getting level {level} config from default_config")

        if not silent:
            logger.debug(f"Level {level} config: {prepared_config}")
        return prepared_config

    def _level_in_config(self, level, levels):
        if levels is None:
            return False
        if isinstance(levels, int):
            return level == levels
        elif isinstance(levels, list):
            return level in levels
        elif isinstance(levels, dict):
            from_level = levels.get('from', level)
            to_level = levels.get('to', level)
            return from_level <= level <= to_level
        elif callable(levels):
            return levels(level)
        else:
            logger.warning(f"Unknown levels format in config: {levels}")
            return False

    def _prepare_level_config(self, config, level):
        # Prepare level configuration by calculating properties based on the level
        prepared_config = config.copy()
        if level == 1:
            # For Level 1, outer_radius is defined, ensure inner_radius is zero
            prepared_config['inner_radius'] = 0
            prepared_config['outer_radius'] = prepared_config.get('radius', self.base_radius)
        else:
            # Get previous level's outer_radius
            prev_level_config = self.get_level_config(level - 1, silent=True)
            prev_outer_radius = prev_level_config['outer_radius']

            # For levels above 1
            # Outer radius
            if  "outer_radius" in config and "outer_radius_increment" in config:
                raise ValueError(f"Invalid configuration: both outer_radius and outer_radius_increment are used in level {level}")
            elif "outer_radius_increment" in config:
                outer_increment = self._get_config_value(config.get('outer_radius_increment'), level)
                prepared_config['outer_radius'] = prev_outer_radius + outer_increment
            elif "outer_radius" in config : 
                prepared_config['outer_radius'] = config.get('outer_radius')
            else : 
                raise KeyError(f"Neither 'outer_radius' nor 'outer_radius_increment' were found in the level config of level {level}")

            # Inner radius
            if  "inner_radius" in config and "inner_radius_increment" in config:
                raise ValueError(f"Invalid configuration: both inner_radius and inner_radius_increment are used in level {level}")
            elif "inner_radius_increment" in config:
                inner_increment = self._get_config_value(config.get('inner_radius_increment'), level)
                prepared_config['inner_radius'] = prev_outer_radius + inner_increment
                logger.debug(f"inner radius was incremented by {inner_increment} from previous outer_radius {prev_outer_radius}")
            elif "inner_radius" in config : 
                prepared_config['inner_radius'] = config.get('inner_radius')
            else:
                prepared_config['inner_radius'] = prev_outer_radius # adjacent to the lower level

            # Validation to ensure inner_radius is not greater than outer_radius
            if prepared_config['inner_radius'] > prepared_config['outer_radius']:
                logger.error(f"inner_radius ({prepared_config['inner_radius']}) cannot be greater than outer_radius ({prepared_config['outer_radius']}) in level {level}")
                raise ValueError(f"Invalid configuration: inner_radius ({prepared_config['inner_radius']}) is greater than outer_radius ({prepared_config['outer_radius']}) in level {level}")
            
        prepared_config.pop("levels")

        return prepared_config

    def default_config(self, level):
        # Default configuration if none is provided
        if level == 1:
            return {
                'levels': 1,
                'radius': self.base_radius,
                'opacity': 100,
                'font_size': 10,
                'default_color': '#a20025'
            }
        else:
            return {
                'levels': level,
                'outer_radius_increment': 50,
                'opacity': lambda lvl: max(100 - (lvl - 1) * 10, 30),
                'font_size': lambda lvl: max(10 - (lvl - 1), 6),
                'default_color': lambda lvl: Wheel.adjust_color('#a20025', amount=0.1 * (lvl - 1))
            }

    def _get_config_value(self, value, level):
        return value(level) if callable(value) else value

    def json_to_drawio(self, name):
        logger.debug(f"Generating DrawIO for: {name}")
        # Access the nodes for the specified name
        structure_data = next((entry for entry in self.structures_list if entry['name'] == name), None)
        if not structure_data:
            raise ValueError(f"'{name}' not found in the JSON data.")
        root_nodes = structure_data['nodes']

        # Initialize the Diagram Generator
        diagram = DiagramGenerator()

        # Start recursive processing from Level 1
        self._process_nodes(root_nodes, start_angle=0.0, end_angle=1.0, level=1, diagram=diagram)

        # Generate and return the XML content
        xml_content = diagram.generate_xml(name)
        return xml_content

    def _process_nodes(self, nodes, start_angle, end_angle, level, diagram):
        logger.debug(f"Processing Level {level}, nodes: {[node['label'] for node in nodes]}")

        # Get level configuration
        level_config = self.get_level_config(level)
        if not level_config:
            logger.debug(f"No configuration found for Level {level}. Stopping recursion.")
            return  # No more levels to process

        # Calculate radii and other parameters
        inner_radius = level_config['inner_radius']
        outer_radius = level_config['outer_radius']
        arc_width = 1 - (inner_radius / outer_radius) if level > 1 else 1
        opacity = self._get_config_value(level_config.get('opacity', 100), level)
        font_size = self._get_config_value(level_config.get('font_size', 10), level)
        default_color = self._get_config_value(level_config.get('default_color', '#FFFFFF'), level)
        r_text = (inner_radius + outer_radius) / 2 if level > 1 else outer_radius * 0.6  # Adjust text position

        total_angle = (end_angle - start_angle) % 1.0
        if total_angle <= 0:
            total_angle += 1.0  # Ensure positive total angle

        # Calculate total specified percentage and nodes without 'percentage'
        total_specified_percentage = sum(node.get('percentage', 0) for node in nodes)
        unspecified_nodes = [node for node in nodes if 'percentage' not in node]
        total_unspecified_nodes = len(unspecified_nodes)

        # Validate total specified percentage
        if total_specified_percentage > 100:
            raise ValueError(f"Total specified percentage exceeds 100% at level {level}")

        remaining_percentage = 100 - total_specified_percentage

        current_angle = start_angle

        for node in nodes:
            if 'percentage' in node:
                node_percentage = node['percentage']
            else:
                if total_unspecified_nodes > 0:
                    node_percentage = remaining_percentage / total_unspecified_nodes
                else:
                    node_percentage = 0  # No unspecified nodes left
            angle_proportion = node_percentage / 100  # Convert percentage to proportion
            angle_span = total_angle * angle_proportion
            current_end_angle = (current_angle + angle_span) % 1.0

            logger.debug(f"Processing node: {node['label']} at Level {level}, start_angle: {current_angle}, end_angle: {current_end_angle}")

            colors_list = node.get('color', [])
            base_color = colors_list[0] if len(colors_list) > 0 else default_color
            fill_color = colors_list[level - 1] if len(colors_list) >= level else Wheel.adjust_color(base_color, amount=0.1 * (level - 1))

            if level == 1:
                # Level 1 is a pie slice
                diagram.add_pie_slice(
                    self.center_x, self.center_y, outer_radius,
                    current_angle, current_end_angle,
                    fill_color, self.stroke_color, opacity
                )
            else:
                # Levels above 1 are annulus slices
                diagram.add_annulus_slice(
                    self.center_x, self.center_y, outer_radius, arc_width,
                    current_angle, current_end_angle,
                    fill_color, self.stroke_color, opacity
                )

            # Add text label
            mid_angle = Wheel.calculate_mid_angle(current_angle, current_end_angle)
            mid_angle_deg = (mid_angle * 360.0) - 90.0
            if mid_angle_deg < 0:
                mid_angle_deg += 360.0
            rotation = Wheel.compute_text_rotation(mid_angle_deg)
            x_text, y_text = Wheel.calculate_positions(self.center_x, self.center_y, r_text, mid_angle_deg, self.text_width, self.text_height)
            diagram.add_text_element(
                node['label'], x_text, y_text,
                self.text_width, self.text_height, rotation,
                font_size, self.font_color
            )

            # Process sub-nodes recursively
            sub_nodes = node.get('sub_nodes', [])
            if sub_nodes:
                self._process_nodes(sub_nodes, current_angle, current_end_angle, level + 1, diagram)

            # Update angles and counts
            current_angle = current_end_angle
            if 'percentage' not in node:
                total_unspecified_nodes -= 1
                remaining_percentage -= node_percentage




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

    log_level = getattr(logging, args.log_level.upper(), logging.INFO)
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

    # XML Generation and Output
    # ------------------------------------
    generator = GenericWheel(320, 290, 80, 30, '#808080', '#000000', json_data)

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
            logger.error(f"Failed to generate or write XML for {entry_name}: {e}")

if __name__ == "__main__":
    main()