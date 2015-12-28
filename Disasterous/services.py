import sys

from .secret import secret_key, app_key

class Dropbox:
    def __init__(self):
        from dropbox.client import DropboxClient
        from dropbox.session import DropboxSession

        try:
            self.service = DropboxClient(oauth2_access_token = secret_key)
            self.service.account_info()
        except:
            sys.exit()