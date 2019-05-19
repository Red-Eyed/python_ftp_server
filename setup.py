from setuptools import setup

setup(
   name='pyftp-server',
   version='1.0',
   description='FTP server on python to simplify file sharing',
   author='Vadym Stupakov',
   author_email='vadim.stupakov@gmail.com',
   packages=['pyftp-server'],
   install_requires=['requests', 'pyftpdlib']
)
