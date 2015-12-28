from Disasterous.jsondb import Jsondb
from Disasterous.paths  import fp_json

class Config:
    def __init__(self):
        self.jsondb = Jsondb(fp_json['config'])
        self.__dict__.update(**self.jsondb.store)

        # ...
        self.chunk_size()

    def chunk_size(self):
        try:
            chunk_mult = {'KB': 1024, 'MB': 1024 ** 2, 'GB': 1024 ** 3}[self.chunks[-2:]]
            chunk = int(self.config.chunks[:-2]) * chunk_mult
        except: #4MB
            chunk = 4 * (1024 ** 2)
        self.chunks = chunk

    def __repr__(self): 
        return '< Config\n    {store}\n>'.format(store='\n    '.join(['{k} => {v}'.format(k=k, v=self.__dict__[k]) for k in self.__dict__]))