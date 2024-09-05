import base64

with open('svg_test.svg', 'w') as svg_file:
    svg_file.write(r'<svg width="4144" height="2822" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">' + '\n')
    with open(r'C:\Users\luisp\Pictures\Siril\2024.07.27_M31_02\results\2024.07.25_M31_02_LPro_v1.0.png', 'rb') as png_file:
        encoded_string = base64.b64encode(png_file.read())
    svg_file.write(r'<image width="100%" height="100%" xlink:href="data:image/png;base64,' + encoded_string.decode('utf-8') + '" />' + '\n')
    svg_file.write(r'</svg>')
