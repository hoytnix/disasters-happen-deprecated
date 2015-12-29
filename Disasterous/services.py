import sys

from .secret import secret_key

def Service(service_name):
    s = None
    if service_name == 'Dropbox':
        s = Dropbox()
    else: #Default to Dropbox
        s = Dropbox()
    return s

class Dropbox:
    def __init__(self):
        from dropbox.client import DropboxClient
        from dropbox.session import DropboxSession

        try:
            self.service = DropboxClient(oauth2_access_token = secret_key)
            self.service.account_info()
        except:
            sys.exit()