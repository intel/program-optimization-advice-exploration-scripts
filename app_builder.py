import os

def exec(src_dir, compiler_dir, relative_binary_path):
    print(f'MOCKUP: building binary to be compiled by {compiler_dir}')
    orig_binary = os.path.join(src_dir, relative_binary_path)
    print(f'MOCKUP OUTPUT: orig binary {orig_binary}')
    return orig_binary