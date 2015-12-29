from string import ascii_letters, digits, punctuation
from random import choice

from Disasterous.console import Console

def rand_str(length=8):
    c = ''.join([ascii_letters, digits])
    s = ''
    for i in range(length):
      s += choice(c)
    return s

def main():
    # Init term.
    term = Console()

    # Test link.
    msg = []
    msg.append('Navigate to =>    https://www.dropbox.com/developers/apps/create')
    msg.append('Select Dropbox API')
    msg.append('Select either option; App folder is recommended.')
    msg.append('Here\'s a suggested app name: disaster_recovery_{s}'.format(s=rand_str(length=8)))
    msg.append('Navigate down to "Generate access token."')

    for step in range(msg.__len__()):
        s = '{n}) {s}'.format(n = step + 1, s = msg[step])
        term.secho(s)
        input("Hit break to continue...")

    key = input('Paste that baby here: ')
    code = '{name} = \'{value}\''.format(name='secret_key', value=key)
    with open('./Disasterous/secret.py', 'w+') as f:
        f.write(code)

if __name__ == '__main__':
    main()