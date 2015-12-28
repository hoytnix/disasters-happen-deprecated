import fcntl, termios, struct, os

from math import floor

class Console:
    def __init__(self, expression, layout):
        # 0. Variable init.
        self.term_size = self.get_term_size() #W,H
        self.width = self.term_size[0]
        self.height = self.term_size[1]
        self.expression = expression
        self.layout = layout

    def secho(self, msg):
        print(msg)

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

if __name__ == '__main__':
    msg_r = '{foo} {bar} => {hello} {spam}'
    msg_args = {
        'foo': '1',
        'bar': 'abc',
        'spam': 'no',
        'hello': 'world'
    }
    msg_format = {
        'foo': {
            'width': 4,
            'align': 'left'
        },
        'bar': {
            'width': 0.5,
            'align': 'right'
        },
        'spam': {
            'width': 0.25,
            'align': 'right'
        },
        'hello': {
            'width': 0.25,
            'align': 'left'
        }
    }

    term = Console(expression = msg_r, layout = msg_format)
    term.echo(msg_args)