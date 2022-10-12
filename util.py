import os

# routine providing api usable for chaining
def make_dir(path):
    os.makedirs(path)
    return path

