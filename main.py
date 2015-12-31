import os, sys, json

from time import strftime

from Disasterous.console  import Console
from Disasterous.fs       import File, LocalFS, RemoteFS
from Disasterous.services import Service
from Disasterous.config   import Config
from Disasterous.paths    import fp_json
from Disasterous.jsondb   import Jsondb

import dropbox

class MyApp:
    def __init__(self):
        # Init self.
        self.config = Config()
        if self.config.verbosity:
            self.term = Console()

        # Be polite.
        if self.config.verbosity:
            self.term.secho('Hello!', n=True)

        # Init API service.
        try:
            self.service = Service(self.config.service)
        except:
            sys.exit('Unable to login to API service!')
        
        # FS.
        local  = LocalFS(config=self.config)
        remote = RemoteFS(config=self.config)

        # Backup!
        if not self.config.development:
            self.push()

    def push(self):
        # Init.
        file_mode = dropbox.files.WriteMode('overwrite')
        local_branch  = self.branch_store['local']
        remote_branch = self.branch_store['remote'] 

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
                    # File obj
                    local_file = File(fp=local_path)

                    # Verbosity.
                    if self.config.verbosity:
                        msg_args = {
                            'local_path': local_file.echoable(),
                            'remote_path': remote_path,
                            'time': strftime('%I:%M'),
                            'est': self.term.est_upload_time(local_file.size() / (500 * 1024))
                        }
                        self.term.echo(args=msg_args)

                    # Do.
                    if self.upload_file(remote_path = remote_path, local_path = local_path):
                        if not self.config.development:
                            self.branch_json.save()
                        

    def upload_file(self, local_path, remote_path):
        # Uploader.
        file_obj = File(fp=local_path)
        uploader = self.service.get_chunked_uploader(file_obj.obj(), length = file_obj.size())
        while uploader.offset < file_obj.size():
            try:
                upload = uploader.upload_chunked(chunk_size=self.config.chunks)
            except:
                print(sys.exc_info()[0], sys.exc_info()[2].tb_lineno)
                return False
                # perform error handling and retry logic
        uploader.finish(path = remote_path, overwrite = True)
        return True

    def get_remote_files(self):
        #return [entry for entry in self.service.files_list_folder('').entries]
        return None

def main():
    x = MyApp()
    
if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        sys.exit('\nGoodbye!')