import base64

with open(r'../../templates/landscape_template.svg', 'r') as svg_template:
    template_content = svg_template.read()

with open(r'test.png', 'rb') as png_file:
    encoded_string = base64.b64encode(png_file.read()).decode('utf-8')

with open('svg_test.svg', 'w') as svg_file:
    svg_file.write(template_content.replace('{{image_data}}', encoded_string))
