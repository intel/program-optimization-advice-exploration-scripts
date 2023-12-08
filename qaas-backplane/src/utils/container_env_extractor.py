# -*- coding: utf-8 -*-

###############################################################################
# MIT License

# Copyright (c) 2023 Intel-Sandbox
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
###############################################################################
# HISTORY
# Created October 2022
# Contributors: David/Hafid

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
