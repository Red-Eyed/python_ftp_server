#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Vadym Stupakov"
__maintainer__ = "Vadym Stupakov"
__email__ = "vadim.stupakov@gmail.com"


for i in range(2):
    try:
        from pyftpdlib.authorizers import DummyAuthorizer
        from pyftpdlib.handlers import FTPHandler
        from pyftpdlib.servers import FTPServer
        break
    except ImportError:
        import subprocess
        from pathlib import Path
        requirements = Path(__file__).parent / "requirements.txt"
        subprocess.call(["pip3", "install", "--user", "-r", requirements])

import argparse
from pathlib import Path
import socket
import requests


def get_private_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]


def get_public_ip():
    return requests.get('http://ip.42.pl/raw').text


if __name__ == '__main__':
    example_text = "example:\n" \
                   "    {0} -u user -p password\n" \
                   "    {0} -u user -p password --readonly\n" \
                   "    {0} -u user -p password --dir /tmp\n".format(__file__)

    parser = argparse.ArgumentParser(prog="ftp_server",
                                 description="FTP server for file sharing over internet or local network",
                                 epilog=example_text,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("-u", "--user", type=str, required=True)
    parser.add_argument("-p", "--password", type=str, required=True)
    parser.add_argument("-r", "--readonly", action="store_true")
    parser.add_argument("-d", "--dir", type=Path, default=Path().cwd())
    parser.add_argument("--ip", type=str, default=get_private_ip())
    parser.add_argument("--port", type=int, default=60000)
    parser.add_argument("--port_range", default=range(60001, 61001))

    args = parser.parse_args()

    perm_read = "elr"
    perm_write = "adfmw"
    permissions = perm_read + perm_write

    if args.readonly:
        permissions = perm_read

    authorizer = DummyAuthorizer()
    authorizer.add_user(args.user, args.password, str(args.dir), perm=permissions)

    handler = FTPHandler
    handler.passive_ports = args.port_range
    handler.authorizer = authorizer
    handler.use_sendfile = True

    server = FTPServer((get_private_ip(), args.port), handler)

    print("Private address: ftp://{}:{}".format(get_private_ip(), args.port))
    print("Public address: ftp://{}:{}".format(get_public_ip(), args.port))
    print("User: {}".format(args.user))
    print("Password: {}".format(args.password))
    print()

    server.serve_forever()
