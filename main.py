import os, sys, json
from hashlib import md5
from math import floor
from time import strftime

import dropbox
from dropbox.client import DropboxClient
from dropbox.session import DropboxSession

from secret  import secret_key, app_key
from console import Console

def file_checksum(fp):
    try:
        with open(fp, 'rb') as f:
            return md5(f.read()).hexdigest()
    except: # File does not exist yet.
        return ""

def est_upload_time(length):
    d = [
        0, #h [0]
        0, #m [1] 
        0, #s [2]
    ]
    d[1], d[2] = divmod(length, 60)
    d[0], d[1] = divmod(d[1], 60)

    # Find largest denominator.
    characteristic_index = 2
    for n in range(d.__len__()):
        if d[n] > 0:
            characteristic_index = n
            break
    characteristic = d[characteristic_index]

    # Find second largest.
    mantissa = 0
    mantissa_index = characteristic_index + 1
    if mantissa_index == d.__len__():
        pass
    else:
        mantissa = d[mantissa_index]
    
    # STRING FORMATTING
    time_str_r = '{decimal}{unit}'
    decimal = 0
    unit = ['h', 'm', 's'][characteristic_index]
    # ...
    if characteristic < 1: # 0s - < 1s
        decimal = 0
    else: # N.NN
        decimal = '%.1f' % (characteristic + (mantissa / 60))
    # format
    if characteristic < 10:
        time_str = time_str_r.format(decimal = decimal, unit = unit)
        time_str = time_str.replace('.0', '')
    else:
        time_str = time_str_r.format(decimal = int(characteristic), unit = unit)
    # padding
    return ' ' * (4 - time_str.__len__()) + time_str

class MyApp:
    def __init__(self):
        # Init console.
        self.term = self.init_term()

        # Init API service.
        try:
            self.client = DropboxClient(oauth2_access_token = secret_key)
            self.client.account_info()
        except:
            sys.exit('')

        # Be polite.
        self.term.secho('Welcome!\nLogged in to Dropbox...\n')

        # Init database.
        self.db_file_path = 'branches.json'
        self.db = self.db_load()

        # Populate.
        self.remote_files = self.get_remote_files()
        self.get_local_files(db_obj = self.db)

        # Backup!
        self.push()
    
    def init_term(self):
        expression = '{time} {est} {local_path} => {remote_path}'
        layout = {
            'local_path': {
                'width': 0.5,
                'align': 'left'
            },
            'remote_path': {
                'width': 0.5,
                'align': 'right'
            },
            'time': {
                'width': 5
            },
            'est': {
                'width': 4
            }
        }
        return Console(expression = expression, layout = layout)

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

                    # Print.
                    msg_args = {
                        'local_path': local_path,
                        'remote_path': remote_path,
                        'time': strftime('%I:%M'),
                        'est': est_upload_time(os.path.getsize(local_path) / (500 * 1024))
                    }
                    self.term.echo(args=msg_args)

                    # Do.
                    try:
                        if self.upload_file(remote_path = remote_path, local_path = local_path):
                            self.db_save()
                    except (KeyboardInterrupt, SystemExit):
                        sys.exit('\nGoodbye!')
                    except:
                        pass

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
            print(sys.exc_info()[0])
        return db

def main():
    x = MyApp()
    
if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        sys.exit('\nGoodbye!')