import os.path

# ../Disasterous
dir_app = os.path.dirname(os.path.realpath(__file__))

# ../
dir_top = os.path.abspath(os.path.join(dir_app, os.pardir))

# ../Json
dir_json = os.path.join(dir_top, 'Json')
fp_json = {}
for dirpath, dirnames, filenames in os.walk(dir_json):
    for file_name in filenames:
        key = '.'.join(file_name.split('.')[:-1])
        fp_json[key] = os.path.join(dir_json, file_name)