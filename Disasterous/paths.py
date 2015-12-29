import os.path

def dir_to_json(d):
    j = {}
    for dirpath, dirnames, filenames in os.walk(d):
        for file_name in filenames:
            key = '.'.join(file_name.split('.')[:-1])
            j[key] = os.path.join(d, file_name)
    return j

# ../Disasterous
dir_app = os.path.dirname(os.path.realpath(__file__))

# ../
dir_top = os.path.abspath(os.path.join(dir_app, os.pardir))

# ../Json
dir_json = os.path.join(dir_top, 'Json')
fp_json = dir_to_json(d=dir_json)

# ../Branches
dir_branches = os.path.join(dir_top, 'Branches')
fp_branches = dir_to_json(d=dir_branches)