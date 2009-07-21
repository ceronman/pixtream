"""
Get resources like images
"""

import os

current_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_path)

def get_file(*fileparts):
    return os.path.join(current_dir, *fileparts)
