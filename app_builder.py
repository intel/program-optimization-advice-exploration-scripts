import os

def exec(src_dir, relative_binary_path):
    print('MOCKUP: building binary')
    orig_binary = os.path.join(src_dir, relative_binary_path)
    print(f'MOCKUP OUTPUT: orig binary {orig_binary}')
    return orig_binary