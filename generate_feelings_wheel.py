import json
import colorsys
import math

# Configuration Parameters
CONFIG = {
    # Common Parameters
    'center_x': 320,
    'center_y': 290,
    'text_width': 80,
    'text_height': 30,
    'stroke_color': '#808080',
    'font_color': '#000000',
    'font_sizes': {
        'Level 1': 10,
        'Level 2': 8,
        'Level 3': 7,
    },
    'default_colors': {
        'Level 1': '#a20025',
        'Level 2': '#d73058',
        'Level 3': '#f46a8a',
    },
    # Level-Specific Parameters
    'level_parameters': {
        'Level 1': {
            'radius': 100,        # Radius of Level 1 circle
            'opacity': 100,       # Opacity for Level 1 shapes (0 to 100)
            # No radial_offset for Level 1
        },
        'Level 2': {
            'inner_radius': 100,  # Inner radius of Level 2 annulus
            'outer_radius': 150,  # Outer radius of Level 2 annulus
            'radial_offset': 0,   # Radial offset for Level 2
            'opacity': 80,        # Opacity for Level 2 shapes
        },
        'Level 3': {
            'inner_radius': 150,  # Inner radius of Level 3 annulus
            'outer_radius': 200,  # Outer radius of Level 3 annulus
            'radial_offset': 0,   # Radial offset for Level 3
            'opacity': 60,        # Opacity for Level 3 shapes
        },
    },
}

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))

def rgb_to_hex(rgb_tuple):
    rgb_tuple = [max(0, min(1, c)) for c in rgb_tuple]
    return '#' + ''.join(f'{int(c*255):02X}' for c in rgb_tuple)

def adjust_color(color, amount=0.0):
    rgb = hex_to_rgb(color)
    h, l, s = colorsys.rgb_to_hls(*rgb)
    l = max(0, min(1, l + amount))
    rgb_new = colorsys.hls_to_rgb(h, l, s)
    return rgb_to_hex(rgb_new)

def calculate_mid_angle(start_angle, end_angle):
    if end_angle < start_angle:
        end_angle += 1.0  # Adjust for wrapping around
    mid_angle = (start_angle + end_angle) / 2.0
    if mid_angle >= 1.0:
        mid_angle -= 1.0  # Normalize back to range [0, 1)
    return mid_angle

def compute_text_rotation(mid_angle_deg):
    # Ensure text is upright
    if 90 < mid_angle_deg <= 270:
        rotation = mid_angle_deg + 180  # Flip text to keep upright
    else:
        rotation = mid_angle_deg
    return rotation % 360  # Ensure rotation is between 0 and 360

# Generic Diagram Library
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

    def add_donut(self, x, y, width, height, fill_color, fill_opacity, font_size, dx=0, parent_id="1"):
        style = (
            f'shape=mxgraph.basic.donut;fillColor={fill_color};fillOpacity={fill_opacity};strokeColor=none;'
            f'fontSize={font_size};align=center;html=1;'
        )
        if dx != 0:
            style += f'dx={dx};'
        style += 'verticalLabelPosition=bottom;verticalAlign=top;'

        shape_xml = (
            f'<mxCell id="{self.id_counter}" value="" '
            f'style="{style}" '
            f'vertex="1" parent="{parent_id}">\n'
            f'<mxGeometry x="{x}" y="{y}" width="{width}" height="{height}" as="geometry"/>\n'
            f'</mxCell>\n'
        )
        donut_id = self.id_counter
        self.shapes.append(shape_xml)
        self.id_counter += 1
        return donut_id

    def add_arc(self, x, y, width, height, start_angle, end_angle, stroke_color, stroke_width):
        shape_xml = (
            f'<mxCell id="{self.id_counter}" value="" '
            f'style="shape=mxgraph.basic.arc;strokeColor={stroke_color};strokeWidth={stroke_width};startAngle={start_angle};endAngle={end_angle};verticalLabelPosition=bottom;verticalAlign=top;html=1;" '
            f'vertex="1" parent="1">\n'
            f'<mxGeometry x="{x}" y="{y}" width="{width}" height="{height}" as="geometry"/>\n'
            f'</mxCell>\n'
        )
        self.shapes.append(shape_xml)
        self.id_counter += 1
        return self.id_counter - 1

    def add_circular_dial(self, x, y, width, height, value_text, value_percentage, fill_color, fill_opacity, donut_font_size, value_font_size, font_color):
        # Add the donut shape
        donut_id = self.add_donut(
            x=x, y=y, width=width, height=height,
            fill_color=fill_color, fill_opacity=fill_opacity,
            font_size=donut_font_size, dx=10
        )

        # Add the partConcEllipse as a child of the donut without specifying x and y
        self.add_part_conc_ellipse(
            width=width,
            height=height,
            start_angle=0,
            end_angle=value_percentage,
            arc_width=0.2,
            fill_color=fill_color,
            stroke_color="none",
            opacity=100,
            value=value_text,
            parent_id=str(donut_id),
            font_size=value_font_size,
            font_color=font_color,
            font_style=1,
            align='center',
            verticalLabelPosition='middle',
            verticalAlign='middle'
        )

        return donut_id

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

    def generate_xml(self, language):
        xml_content = (
            '<mxfile host="Electron">\n'
            f'<diagram name="Feelings Wheel - {language}">\n'
            '<mxGraphModel>\n'
            '<root>\n'
        )
        xml_content += '\n'.join(self.root_cells) + '\n'
        xml_content += ''.join(self.shapes)
        xml_content += '</root>\n</mxGraphModel>\n</diagram>\n</mxfile>'
        return xml_content

def json_to_drawio(json_data, language):
    # Access the emotions for the specified language
    if language not in json_data['languages']:
        raise ValueError(f"Language '{language}' not found in the JSON data.")
    language_data = json_data['languages'][language]
    major_emotions_data = language_data['emotions']

    # Configuration parameters
    center_x = CONFIG['center_x']
    center_y = CONFIG['center_y']
    text_width = CONFIG['text_width']
    text_height = CONFIG['text_height']
    stroke_color = CONFIG['stroke_color']
    font_color = CONFIG['font_color']
    font_sizes = CONFIG['font_sizes']
    default_colors = CONFIG['default_colors']
    level_parameters = CONFIG['level_parameters']

    # Retrieve level parameters
    # Level 1
    R1 = level_parameters['Level 1']['radius']
    opacity_level_1 = level_parameters['Level 1'].get('opacity', 100)
    # Level 2
    R2_inner = level_parameters['Level 2']['inner_radius'] + level_parameters['Level 2'].get('radial_offset', 0)
    R2_outer = level_parameters['Level 2']['outer_radius'] + level_parameters['Level 2'].get('radial_offset', 0)
    opacity_level_2 = level_parameters['Level 2'].get('opacity', 100)
    # Level 3
    R3_inner = level_parameters['Level 3']['inner_radius'] + level_parameters['Level 3'].get('radial_offset', 0)
    R3_outer = level_parameters['Level 3']['outer_radius'] + level_parameters['Level 3'].get('radial_offset', 0)
    opacity_level_3 = level_parameters['Level 3'].get('opacity', 100)

    # Calculate arc widths for Level 2 and Level 3 shapes
    arc_width_L2 = 1 - (R2_inner / R2_outer)
    arc_width_L3 = 1 - (R3_inner / R3_outer)

    # Text label radii (adjusted based on level radii)
    r_text1 = R1 * 0.6  # Bring Level 1 text closer to center
    r_text2 = (R2_inner + R2_outer) / 2  # Middle of Level 2 annulus
    r_text3 = (R3_inner + R3_outer) / 2  # Middle of Level 3 annulus

    # Initialize the Diagram Generator
    diagram = DiagramGenerator()

    total_angle = 1.0  # Total angle from 0 to 1 (representing 0 to 2π radians)
    num_major_emotions = len(major_emotions_data)
    angle_per_major_emotion = total_angle / num_major_emotions
    start_angle_major = 0.0

    for major_emotion, major_emotion_data in major_emotions_data.items():
        sub_emotions = major_emotion_data['sub_emotions']
        colors_list = major_emotion_data.get('color', [])
        base_color = colors_list[0] if len(colors_list) > 0 else default_colors['Level 1']
        end_angle_major = (start_angle_major + angle_per_major_emotion) % 1.0

        # Level 1 (Major Emotions)
        fill_color_level_1 = colors_list[0] if len(colors_list) > 0 else base_color
        diagram.add_pie_slice(
            center_x, center_y, R1,
            start_angle_major, end_angle_major,
            fill_color_level_1, stroke_color, opacity_level_1
        )

        # Add text label for Level 1
        mid_angle_major = calculate_mid_angle(start_angle_major, end_angle_major)
        mid_angle_deg = (mid_angle_major * 360.0) - 90.0
        if mid_angle_deg < 0:
            mid_angle_deg += 360.0

        rotation_major = compute_text_rotation(mid_angle_deg)

        x_text_major = center_x + r_text1 * math.cos(math.radians(mid_angle_deg)) - text_width / 2
        y_text_major = center_y + r_text1 * math.sin(math.radians(mid_angle_deg)) - text_height / 2

        diagram.add_text_element(
            major_emotion, x_text_major, y_text_major,
            text_width, text_height, rotation_major,
            font_sizes['Level 1'], font_color
        )

        # Level 2 (Sub-Emotions)
        total_sub_feelings = sum(len(feelings) for feelings in sub_emotions.values())
        start_angle_sub_emotion = start_angle_major
        fill_color_level_2 = colors_list[1] if len(colors_list) > 1 else adjust_color(base_color, amount=0.1)

        for sub_emotion, sub_feelings in sub_emotions.items():
            num_sub_feelings = len(sub_feelings)
            angle_per_sub_emotion = angle_per_major_emotion * (num_sub_feelings / total_sub_feelings)
            end_angle_sub_emotion = (start_angle_sub_emotion + angle_per_sub_emotion) % 1.0

            diagram.add_annulus_slice(
                center_x, center_y, R2_outer, arc_width_L2,
                start_angle_sub_emotion, end_angle_sub_emotion,
                fill_color_level_2, stroke_color, opacity_level_2
            )

            # Add text label for Level 2
            mid_angle_sub_emotion = calculate_mid_angle(start_angle_sub_emotion, end_angle_sub_emotion)
            mid_angle_deg = (mid_angle_sub_emotion * 360.0) - 90.0
            if mid_angle_deg < 0:
                mid_angle_deg += 360.0

            rotation_sub_emotion = compute_text_rotation(mid_angle_deg)

            x_text_sub_emotion = center_x + r_text2 * math.cos(math.radians(mid_angle_deg)) - text_width / 2
            y_text_sub_emotion = center_y + r_text2 * math.sin(math.radians(mid_angle_deg)) - text_height / 2

            diagram.add_text_element(
                sub_emotion, x_text_sub_emotion, y_text_sub_emotion,
                text_width, text_height, rotation_sub_emotion,
                font_sizes['Level 2'], font_color
            )

            # Level 3 (Sub-Feelings)
            start_angle_sub_feeling = start_angle_sub_emotion
            fill_color_level_3 = colors_list[2] if len(colors_list) > 2 else adjust_color(base_color, amount=0.2)

            angle_per_sub_feeling = angle_per_sub_emotion / num_sub_feelings

            for sub_feeling in sub_feelings:
                end_angle_sub_feeling = (start_angle_sub_feeling + angle_per_sub_feeling) % 1.0

                diagram.add_annulus_slice(
                    center_x, center_y, R3_outer, arc_width_L3,
                    start_angle_sub_feeling, end_angle_sub_feeling,
                    fill_color_level_3, stroke_color, opacity_level_3
                )

                # Add text label for Level 3
                mid_angle_sub_feeling = calculate_mid_angle(start_angle_sub_feeling, end_angle_sub_feeling)
                mid_angle_deg = (mid_angle_sub_feeling * 360.0) - 90.0
                if mid_angle_deg < 0:
                    mid_angle_deg += 360.0

                rotation_sub_feeling = compute_text_rotation(mid_angle_deg)

                x_text_sub_feeling = center_x + r_text3 * math.cos(math.radians(mid_angle_deg)) - text_width / 2
                y_text_sub_feeling = center_y + r_text3 * math.sin(math.radians(mid_angle_deg)) - text_height / 2

                diagram.add_text_element(
                    sub_feeling, x_text_sub_feeling, y_text_sub_feeling,
                    text_width, text_height, rotation_sub_feeling,
                    font_sizes['Level 3'], font_color
                )

                start_angle_sub_feeling = end_angle_sub_feeling

            start_angle_sub_emotion = end_angle_sub_emotion

        start_angle_major = end_angle_major

    # Generate and return the XML content
    xml_content = diagram.generate_xml(language)
    return xml_content

# Main Execution
if __name__ == "__main__":
    # Load JSON data from file
    with open('feelings_wheel.json', 'r', encoding='utf-8') as json_file:
        json_data = json.load(json_file)

    # List of languages available in the JSON data
    languages = json_data['languages'].keys()

    # Generate XML output for each language
    for language in languages:
        xml_output = json_to_drawio(json_data, language)
        output_filename = f"feelings_wheel_{language}.xml"
        with open(output_filename, "w", encoding='utf-8') as file:
            file.write(xml_output)
        print(f"XML representation for {language} has been written to {output_filename}")
