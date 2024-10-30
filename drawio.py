class DiagramGenerator:
    def __init__(self):
        self.shapes = []
        self.text_elements = []
        self.edges = []
        self.id_counter = 2  # Start from 2 since 0 and 1 are used
        self.root_cells = [
            '<mxCell id="0"/>',
            '<mxCell id="1" parent="0"/>',
        ]

    def add_pie_slice(self, center_x, center_y, radius, start_angle, end_angle, fill_color, stroke_color, opacity):
        element_id = self.id_counter
        shape_xml = (
            f'<mxCell id="{self.id_counter}" value="" '
            f'style="shape=mxgraph.basic.pie;fillColor={fill_color};strokeColor={stroke_color};opacity={opacity};startAngle={start_angle};endAngle={end_angle};" '
            f'vertex="1" parent="1">\n'
            f'<mxGeometry x="{center_x - radius}" y="{center_y - radius}" width="{2 * radius}" height="{2 * radius}" as="geometry"/>\n'
            f'</mxCell>\n'
        )
        self.shapes.append(shape_xml)
        self.id_counter += 1
        return element_id

    def add_annulus_slice(self, center_x, center_y, outer_radius, arc_width, start_angle, end_angle, fill_color, stroke_color, opacity):
        element_id = self.id_counter
        shape_xml = (
            f'<mxCell id="{self.id_counter}" value="" '
            f'style="shape=mxgraph.basic.partConcEllipse;fillColor={fill_color};strokeColor={stroke_color};opacity={opacity};startAngle={start_angle};endAngle={end_angle};arcWidth={arc_width};" '
            f'vertex="1" parent="1">\n'
            f'<mxGeometry x="{center_x - outer_radius}" y="{center_y - outer_radius}" width="{2 * outer_radius}" height="{2 * outer_radius}" as="geometry"/>\n'
            f'</mxCell>\n'
        )
        self.shapes.append(shape_xml)
        self.id_counter += 1
        return element_id

    
    
    def add_circle(self, center_x, center_y, radius, fill_color, stroke_color, opacity):
        element_id = self.id_counter
        shape_xml = (
            f'<mxCell id="{self.id_counter}" value="" '
            f'style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor={fill_color};strokeColor={stroke_color};opacity={opacity};" '
            f'vertex="1" parent="1">\n'
            f'<mxGeometry x="{center_x - radius}" y="{center_y - radius}" width="{2 * radius}" height="{2 * radius}" as="geometry"/>\n'
            f'</mxCell>\n'
        )
        self.shapes.append(shape_xml)
        self.id_counter += 1
        return element_id


    def add_annulus(self, center_x, center_y, outer_radius, inner_radius, fill_color, stroke_color, opacity):
        element_id = self.id_counter        
        dx = outer_radius - inner_radius
        shape_xml = (
            f'<mxCell id="{self.id_counter}" value="" '
            f'style="verticalLabelPosition=bottom;verticalAlign=top;html=1;'
            f'shape=mxgraph.basic.donut;dx={dx};strokeColor={stroke_color};'
            f'fillColor={fill_color};opacity={opacity};" '
            f'vertex="1" parent="1">\n'
            f'<mxGeometry x="{center_x - outer_radius}" y="{center_y - outer_radius}" '
            f'width="{2 * outer_radius}" height="{2 * outer_radius}" as="geometry"/>\n'
            f'</mxCell>\n'
        )
        self.shapes.append(shape_xml)
        self.id_counter += 1
        return element_id



    def add_text_element(self, text, x, y, width, height, rotation, font_size, font_color, opacity):
        element_id = self.id_counter        
        shape_xml = (
            f'<mxCell id="{self.id_counter}" value="{text}" '
            f'style="text;html=1;align=center;verticalAlign=middle;fontSize={font_size};rotation={rotation};fontColor={font_color};opacity={opacity};" '
            f'vertex="1" parent="1">\n'
            f'<mxGeometry x="{x}" y="{y}" width="{width}" height="{height}" as="geometry"/>\n'
            f'</mxCell>\n'
        )
        self.text_elements.append(shape_xml)
        self.id_counter += 1
        return element_id



    def add_arrow(self, source_id, target_id, style="rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=none;endFill=0;"):
        element_id = self.id_counter
        edge_xml = (
            f'<mxCell id="{self.id_counter}" style="{style}" edge="1" parent="1" source="{source_id}" target="{target_id}">\n'
            f'<mxGeometry relative="1" as="geometry"/>\n'
            f'</mxCell>\n'
        )
        self.edges.append(edge_xml)
        self.id_counter += 1
        return element_id



    def add_line(self, source_id, target_id, x1, y1, x2, y2, style_dict=None):
        if style_dict is None:
            style_dict = {}
        # Default styles
        style_defaults = {
            "strokeColor": "#000000",
            "strokeWidth": "1",
            "endArrow": "none"
        }
        # Merge default styles with provided styles
        style = ";".join(f"{k}={v}" for k, v in {**style_defaults, **style_dict}.items())
        element_id = self.id_counter
        edge_xml = (
            f'<mxCell id="{element_id}" style="{style}" edge="1" parent="1" source="{source_id}" target="{target_id}">\n'
            f'  <mxGeometry relative="1" as="geometry">\n'
            f'    <mxPoint x="{x1}" y="{y1}" as="sourcePoint"/>\n'
            f'    <mxPoint x="{x2}" y="{y2}" as="targetPoint"/>\n'
            f'  </mxGeometry>\n'
            f'</mxCell>\n'
        )
        self.edges.append(edge_xml)
        self.id_counter += 1
        return element_id
        

    def generate_xml(self, name):
        xml_content = (
            '<mxfile host="Electron">\n'
            f'<diagram name="Generic Wheel - {name}">\n'
            '<mxGraphModel>\n'
            '<root>\n'
        )
        xml_content += '\n'.join(self.root_cells) + '\n'
        xml_content += ''.join(self.shapes)        # Add shapes first
        xml_content += ''.join(self.text_elements) # Add text elements after shapes
        xml_content += ''.join(self.edges)         # Add edges after text elements
        xml_content += '</root>\n</mxGraphModel>\n</diagram>\n</mxfile>'
        return xml_content



    def save_to_file(self, filename, content):
        with open(filename, 'w') as file:
            file.write(content)
        print(f"Diagram saved to {filename}")





def main():
    # Create an instance of the DiagramGenerator
    diagram = DiagramGenerator()

    # Example 1: Adding a circle and connecting it to a text element
    circle_id = diagram.add_circle(360, 390, 50, "#10739E", "none", 100)
    text_id1 = diagram.add_text_element("Circle Text", 390, 330, 80, 20, 0, 12, "#000000", 100)
    diagram.add_arrow(text_id1, circle_id)

    # Example 2: Adding a pie slice and attaching a text element
    pie_id = diagram.add_pie_slice(600, 400, 60, 0.25, 0.1, "#FF5733", "none", 100)
    text_id2 = diagram.add_text_element("Pie Slice", 620, 350, 80, 20, 0, 12, "#000000", 100)
    diagram.add_arrow(text_id2, pie_id)

    # Example 3: Adding another circle and a different text element
    circle_id2 = diagram.add_circle(200, 200, 40, "#00FF00", "#000000", 80)
    text_id3 = diagram.add_text_element("Green Circle", 180, 150, 80, 20, 0, 12, "#000000", 100)
    diagram.add_arrow(text_id3, circle_id2)


    xml_output = diagram.generate_xml(" Example Diagram")
    diagram.save_to_file("Example_diagram.drawio", xml_output)

if __name__ == "__main__":
    main()
