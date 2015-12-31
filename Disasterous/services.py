import sys

from .secret import secret_key

def Service(service_name='Dropbox'):
    s = None
    if service_name == 'Dropbox':
        s = DropboxService()
    else: #Default to Dropbox
        s = DropboxService()
    return s

class DropboxService:
    def __init__(self):
        from dropbox.client import DropboxClient
        from dropbox.session import DropboxSession

        try:
            self.service = DropboxClient(oauth2_access_token = secret_key)
            self.service.account_info()
        except:
            sys.exit()



class SSHService:
    def __init__(self):
        pass



class FTPService:
    def __init__(self):
        from ftplib import FTP

        # Init.
        self.ftp = FTP(host='127.0.0.1', user='me', passwd='pass')

        # Login.
        try:
            self.ftp.login()
        except:
            sys.exit()

        # cd
        self.ftp.cwd('/opt/disasterous')

    def put(self):
        f = open('file.bin', 'rb')
        self.ftp.storbinary()