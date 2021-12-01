# FTP server to transfer files between machines with zero configuration
## Usage
1. `python3 -m pip install python-ftp-server`
2. `python3 -m python_ftp_server -d "dirctory/to/share"`
will print:
```bash
Local address: ftp://<IP>:60000
User: <USER>
Password: <PASSWORD>
```
3. Copy and paste your `IP`, `USER`, `PASSWORD`, `PORT` into [FileZilla](https://filezilla-project.org/) (or any other FTP client):
![](https://github.com/Red-Eyed/python_ftp_server/raw/master/img.png)
