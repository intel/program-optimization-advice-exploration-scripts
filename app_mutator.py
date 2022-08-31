import os

def exec(src_dir, compiler_dir, relative_binary_path):
    print(f'MOCKUP: tuning source code from {src_dir} to be compiled by {compiler_dir}')
    opt_binary = os.path.join(src_dir, relative_binary_path)
    print(f'MOCKUP OUTPUT: optimized binary {opt_binary}')
    return opt_binary