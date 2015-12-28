import sys, json

class Jsondb:
    def __init__(self, fp):
        self.file_path = fp
        self.store = self.load()

    def save(self):
        try:
            with open(self.file_path, 'w') as f:
                json.dump(obj = self.store, fp = f, indent = 4)
            return True
        except:
            return False

    def load(self):
        store = {}
        try:
            with open(self.file_path, 'r') as f:
                store = json.load(f)
        except:
            print(sys.exc_info()[0])
        return store