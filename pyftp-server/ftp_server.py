#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
import tempfile

__author__ = "Vadym Stupakov"
__maintainer__ = "Vadym Stupakov"
__email__ = "vadim.stupakov@gmail.com"

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import TLS_FTPHandler
from pyftpdlib.servers import FTPServer
from OpenSSL import crypto

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


def create_self_signed_cert(cert_file: Path, key_file: Path):
    cert_file.unlink()
    key_file.unlink()

    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)

    # create a self-signed cert
    cert = crypto.X509()
    cert.set_version(2)
    cert.set_serial_number(random.randint(50000000, 100000000))
    cert.get_subject().CN = get_hostname()
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha256')

    with open(str(cert_file), "wt") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf8"))

    with open(str(key_file), "wt") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode("utf8"))


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

    handler = TLS_FTPHandler

    cert_file = Path(tempfile.gettempdir(), "cert_file.crt")
    key_file = Path(tempfile.gettempdir(), "key_file.key")
    create_self_signed_cert(cert_file, key_file)

    handler.certfile = str(cert_file.absolute())
    handler.keyfile = str(key_file.absolute())
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
