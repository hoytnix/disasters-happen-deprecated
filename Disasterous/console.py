import fcntl, termios, struct, os

from math import floor

from Disasterous.jsondb import Jsondb
from Disasterous.paths  import fp_json

class Console:
    def __init__(self):
        # Stored inits.
        self.json  = Jsondb(fp = fp_json['console'])
        self.store = self.json.store 
        self.expression = self.store['expression']
        self.layout = self.store['layout']

        # Function inits.
        self.term_size = self.get_term_size() #W,H
        self.width = self.term_size[0]
        self.height = self.term_size[1]

    def secho(self, msg, n=False):
        if type(msg) is str:
            if n:
                msg += '\n'
            print(msg)
        if type(msg) is list:
            for x in msg:
                if n:
                    x += '\n'
                print(x)

    def echo(self, args):
        # 1. Determine non-variable space. (For helpful recommendations.)
        _args = {}
        for key in args:
            _args[key] = ''
        non_variable_spacing = self.expression.format(**_args).__len__()
        
        # 2. Padding-alignment.
        # 2a. Determine size allowed after fixed-width variables.
        fixed_variable_spacing = 0
        for key in self.layout:
            k_width = self.layout[key]['width']
            if k_width > 1:
                fixed_variable_spacing += k_width

        # 2b. Do up the percent-based variable spacing.
        percent_variable_spacing = self.width - (non_variable_spacing + fixed_variable_spacing)
        for key in self.layout:
            k_width = self.layout[key]['width']
            if k_width < 1:
                self.layout[key]['width'] = floor(k_width * percent_variable_spacing)

        # 2c. Add blank-space padding to each variable.
        for key in self.layout:
            k_arg = args[key]
            k_format = self.layout[key]

            if 'align' in k_format:
                f_align = k_format['align']
                
                if f_align is 'right':
                    x = k_arg[:k_format['width']]
                    args[key] = (' ' * (k_format['width'] - x.__len__())) + x
                
                else:
                    x = k_arg[:k_format['width']]
                    args[key] = x + (' ' * (k_format['width'] - x.__len__()))
            else: #Default to left
                x = k_arg[:k_format['width']]
                args[key] = x + (' ' * (k_format['width'] - x.__len__()))

        print(self.expression.format(**args))

    def get_term_size(self):
        env = os.environ
        
        def ioctl_GWINSZ(fd):
            try:
                cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,'1234'))
            except:
                return
            return cr

        cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)

        if not cr:
            try:
                fd = os.open(os.ctermid(), os.O_RDONLY)
                cr = ioctl_GWINSZ(fd)
                os.close(fd)
            except:
                pass

        if not cr:
            cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

            ### Use get(key[, default]) instead of a try/catch
            #try:
            #    cr = (env['LINES'], env['COLUMNS'])
            #except:
            #    cr = (25, 80)

        return int(cr[1]), int(cr[0])

    def est_upload_time(self, length):
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