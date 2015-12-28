import os.path
from hashlib import md5

class File:
    def __init__(self, fp):
        self.full_path = os.path.expanduser(fp)

    def __repr__(self):
        return '<File {path}>'.format(path=self.full_path)

    def obj(self, mode='rb'):
        return open(self.full_path, mode)

    def join(self, path):
        '''
        https://docs.python.org/3/library/os.path.html#os.path.join

        If a component is an absolute path, all previous components are 
        thrown away and joining continues from the absolute path component.
        '''

        if type(path) is str:
            self.full_path = os.path.join(self.full_path, path)
        elif type(path) is list:
            path = [x[1:] if x[0] is '/' else x for x in path]
            self.full_path = os.path.join(self.full_path, *path)

    def checksum(self):
        try:
            with open(self.full_path, 'rb') as f:
                return md5(f.read()).hexdigest()
        except: # File does not exist yet.
            return ""

    def exists(self):
        return os.path.isfile(self.full_path)

    def size(self):
        return os.path.getsize(self.full_path)

    def echoable(self):
        return self.full_path.replace(os.path.expanduser('~/'), '')