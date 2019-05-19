#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Vadym Stupakov"
__maintainer__ = "Vadym Stupakov"
__email__ = "vadim.stupakov@gmail.com"



from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

import platform
import argparse
from pathlib import Path
import socket
import requests


def get_local_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

def get_hostname():
    return socket.gethostname()


def get_global_ip():
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
    parser.add_argument("-g", "--use_global", action="store_true")
    parser.add_argument("--ip", type=str, default=get_hostname())
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

    if "Linux" in platform.system():
        handler.use_sendfile = True

    server = FTPServer((get_local_ip(), args.port), handler)

    print("\n\n\n\n")
    print(f"Local address: ftp://{get_local_ip()}:{args.port}")

    if args.use_global:
        print(f"Global address: ftp://{get_global_ip()}:{args.port}")

    print(f"User: {args.user}")
    print(f"Password: {args.password}")
    print()

    server.serve_forever()
