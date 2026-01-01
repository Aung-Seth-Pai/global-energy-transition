# plotting utils
from IPython.display import Image

def save_static_img(fig, filename):
    fig.write_image(f"{filename}")
    display(Image(f"{filename}"))

if __name__ == "main":
    pass