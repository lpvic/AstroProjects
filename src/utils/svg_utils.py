from pathlib import Path
import base64

from PIL import Image
from matplotlib import pyplot as plt
from astropy.io import fits
import numpy as np
import subprocess


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

    arr = fits.getdata('test.fit')
    r = arr[0, :, :]
    g = arr[1, :, :]
    b = arr[2, :, :]
    rgb = np.zeros((2822, 4144, 3))
    rgb[:, :, 0] = r
    rgb[:, :, 1] = g
    rgb[:, :, 2] = b
    print(rgb.shape)

    dpi = 1000.
    fig = plt.figure(frameon=False)
    fig.set_size_inches(w=4144/dpi, h=2822/dpi)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    plt.imshow(rgb, origin='lower')
    plt.show()
    fig.savefig('iiii.png', dpi=dpi)

    subprocess.run('inkscape --export-type="png" svg_test.svg')
