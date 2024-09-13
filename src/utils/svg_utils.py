from pathlib import Path
import base64


def sign_svg(svg_image: Path, png_image: Path, title: str = '', signture: str = '') -> None:
    with open(r'../../templates/landscape_template.svg', 'r') as svg_template:
        template_content = svg_template.read()

    with open(png_image, 'rb') as png_file:
        encoded_string = base64.b64encode(png_file.read()).decode('utf-8')

    with open(svg_image, 'w', encoding='utf-8') as svg_file:
        svg_file.write(template_content.replace('{{image_data}}', encoded_string)
                       .replace('{{title}}', title)
                       .replace('{{signature}}', signture))


if __name__ == '__main__':
    sign_svg(Path(r'svg_test.svg'), Path(r'test.png'), 'Galaxia de Andrómeda (M31)',
             r'13/09/2024, Luis Pedro Vicente Matilla')
