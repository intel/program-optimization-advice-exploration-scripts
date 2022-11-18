import argparse
import os
import tarfile
from io import BytesIO

def main():
    """Extractor of Podman command environment."""
    parser = argparse.ArgumentParser(description="Run container")
    parser.add_argument('-v', help='Mounting drive', required=False, action='append')
    parser.add_argument('--cmd', help='Command to run container', required=True )
    parser.add_argument('--out-tarball', help='Command to run container', required=True )
    args = parser.parse_args()
    mount_map = dict([map.split(":",1) for map in args.v])
    print(args)
    print(mount_map)
    with tarfile.open(args.out_tarball, "w:gz") as tar:
        add_cmd_file(args.cmd, tar)
        for host_dir in mount_map:
            print(host_dir)
            if not os.path.ismount(host_dir):
                print(f"ADDING folder: {host_dir}")
                tar.add(host_dir)
            else:
                print("SKIPPED mounted folder")

def add_cmd_file(cmd, tar):
    data = f'{cmd}\n'.encode('utf-8')
    string = BytesIO(data)

    info = tarfile.TarInfo(name='cmd.txt')
    info.size=len(data)
    tar.addfile(info, fileobj=string)

if __name__ == '__main__':
   main()