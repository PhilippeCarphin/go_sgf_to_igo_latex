import os

def tex_dir():
    tex_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tex')
    print(tex_dir)
    return tex_dir
