import os, sys, json, time, math
from hashlib import md5

import dropbox
from dropbox.client import DropboxClient
from dropbox.session import DropboxSession

from secret  import secret_key, app_key
from console import getTerminalSize

def file_checksum(fp):
    try:
        with open(fp, 'rb') as f:
            return md5(f.read()).hexdigest()
    except: # File does not exist yet.
        return ""

def est_upload_time(file_size=549453824, web_speed=500):
    # .35s
    # 4.5s
    # 3.9m

    web_speed *= 1024
    length = file_size / web_speed
    m, s = divmod(length, 60)
    h, m = divmod(m, 60)

    if h > 0:
        x = ('%.3f' % h)[:3]
        c = 'h'
    elif m > 0:
        x = ('%.3f' % m)[:3]
        c = 'm'
    elif s > 0:
        x = ('%.3f' % s)[:3]
        c = 's'
    if x[-1] == '.':
        x = ' ' + x[:-1]
    return x + c

class MyApp:
    def __init__(self):
        # Init API service.
        try:
            self.client = DropboxClient(oauth2_access_token = secret_key)
            self.client.account_info()
        except:
            sys.exit('')

        # Init database.
        self.db_file_path = 'branches.json'
        self.db = self.db_load()

        # Populate.
        self.remote_files = self.get_remote_files()
        self.db['local'] = self.get_local_files(db_obj = self.db)

        # Backup!
        self.push()
    
    def push(self):
        # Init.
        file_mode = dropbox.files.WriteMode('overwrite')
        local_branch  = self.db['local']
        remote_branch = self.db['remote'] 

        # Iterate through packages.
        for package_name in local_branch:
            # Get package.
            package = local_branch[package_name]

            # Create remote package if not exists.
            if package_name not in remote_branch:
                remote_branch[package_name] = {}

            # Iterate files.
            for file_key in package['files']:
                # Path must end in / for path-joining.
                discovery_path = os.path.expanduser(package['dir']) + '/'

                # ...
                if file_key[0] == '/':
                    file_name = file_key[1:]
                else:
                    file_name = file_key

                # Paths.
                local_path  = os.path.join(discovery_path, file_name)
                remote_path = '/{package}/{file}'.format(package = package_name,
                    file = file_name
                )

                # Compare checksums.
                upload = False
                local_checksum = package['files'][file_key]['checksum']
                if file_key not in remote_branch[package_name]:
                    remote_branch[package_name][file_key] = {}
                    remote_branch[package_name][file_key]['checksum'] = local_checksum
                    upload = True
                else:
                    if local_checksum != remote_branch[package_name][file_key]['checksum']:
                        remote_branch[package_name][file_key]['checksum'] = local_checksum
                        upload = True

                # Do upload?
                if upload:
                    file_size = os.path.getsize(local_path)
                    # UI.
                    web_speed = 500 #KBps
                    term_width = getTerminalSize()[0]
                    term_left = math.floor( (term_width - 15) / 2 )

                    # Time.
                    time_str = time.strftime('%I:%M') # 10 / 80; inc. spaces
                    time_est = est_upload_time(file_size = file_size, web_speed = web_speed)
                    # Paths.
                    local_path_str = local_path
                    if local_path.__len__() > term_left:
                        local_path_str = local_path_str[(term_left * -1):] # Last N characters
                        x = local_path_str.split('/')
                        if x.__len__() > 1:
                            local_path_str = '/'.join(x[1:]) # Right-to-Left
                    local_path_str += ' ' * (term_left - local_path_str.__len__())

                    remote_path_str = remote_path[:term_left] # First N characters
                    x = remote_path_str.split('/')
                    if x.__len__() > 1:
                        remote_path_str = '/'.join(x[:-1])

                    # Print.
                    print('{time} {est} {local_path} => {remote_path}'.format(local_path = local_path_str,
                            remote_path = remote_path_str,
                            time = time_str,
                            est = time_est
                        )
                    )

                    # Do.
                    if self.upload_file(remote_path = remote_path, local_path = local_path):
                        self.db_save()

    def upload_file(self, local_path, remote_path, chunk_mb = 4):
        # Uploader.
        file_size = os.path.getsize(local_path)
        f = open(local_path, 'rb')
        uploader = self.client.get_chunked_uploader(f, length = file_size)
        while uploader.offset < file_size:
            try:
                upload = uploader.upload_chunked(chunk_size=(chunk_mb * 1048576))
            except:
                return False
                # perform error handling and retry logic
        uploader.finish(path = remote_path, overwrite = True)
        return True

    def get_local_files(self, db_obj):
        # Init.
        local_files = []
        branch = db_obj['local']
        packages = [key for key in branch]
        
        # Iterate packages.
        for package_name in packages:
            # Get package. 
            package = branch[package_name]
            
            # Is discoverable mode?
            if package['discoverable']:
                # Path must end in / for path-joining.
                discovery_path = os.path.expanduser(package['dir']) + '/'

                # Iterate files and directories.
                for dirpath, dirnames, filenames in os.walk(discovery_path):
                    sub_package_name = dirpath.replace(discovery_path, '')

                    # Iterate files.
                    for filename in filenames:
                        # Init.
                        file_key = "{sub_package}/{file_name}".format(sub_package=sub_package_name, 
                            file_name=filename
                        )
                        full_path = os.path.join(discovery_path, sub_package_name, filename)

                        # Discovery should be bi-directional.
                        checksum = file_checksum(full_path)
                        if file_key in package:
                            # Compare checksums.
                            if package['files'][file_key]['checksum'] != checksum:
                                package['files'][file_key]['checksum'] = checksum
                        else:
                            # Insert.
                            package['files'][file_key] = {
                                'checksum': checksum
                            }
            
            # Not discoverabe, probably secret.
            else:
                for file_key in package['files']:
                    discovery_path = os.path.expanduser(package['dir']) + '/'
                    full_path = os.path.join(discovery_path, file_key)
                    checksum = file_checksum(full_path)
                    package['files'][file_key]['checksum'] = checksum

            # Update branch.
            branch[package_name] = package

        return branch

    def get_remote_files(self):
        #return [entry for entry in self.service.files_list_folder('').entries]
        return None

    def db_save(self):
        try:
            with open(self.db_file_path, 'w') as db_file:
                json.dump(obj = self.db, fp = db_file, indent = 4)
            return True
        except:
            return False

    def db_load(self):
        db = {}
        try:
            with open(self.db_file_path, 'r') as db_file:
                db = json.load(db_file)
        except:
            pass
        return db

def main():
    x = MyApp()
    
if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        sys.exit('\nGoodbye!')