import colorama
import cmd
import glob
import os
import sys

import arm


HELP_DIR_NAME = 'help'


class ShellStyle(object):
    ''' Styling for a command shell. '''
    BRIGHT = colorama.Style.BRIGHT
    RESET = colorama.Style.RESET_ALL


    def __init__(self, theme_color, success_color=colorama.Fore.GREEN,
                                    warn_color=colorama.Fore.YELLOW,
                                    error_color=colorama.Fore.RED):
        self.theme_color = theme_color
        self.success_color = success_color
        self.warn_color = warn_color
        self.error_color = error_color


    def theme(self, text):
        ''' Theme style. '''
        return self.theme_color + self.BRIGHT + text + self.RESET


    def _label_desc(self, label, desc, label_color=''):
        ''' Generic styler for a line consisting of a label and description. '''
        return self.BRIGHT +  label_color + label + self.RESET + desc


    def help(self, cmd, desc=''):
        ''' Style for a line of help text. '''
        return self._label_desc(cmd, desc)


    def error(self, cmd, desc=''):
        ''' Style for an error message. '''
        return self._label_desc(cmd, desc, self.error_color)


    def warn(self, cmd, desc=''):
        ''' Style for warning message. '''
        return self._label_desc(cmd, desc, self.warn_color)


    def success(self, cmd, desc=''):
        ''' Style for a success message. '''
        return self._label_desc(cmd, desc, self.success_color)


class ArmShell(cmd.Cmd):
    ''' An interactive shell for the ST Robotics arm. '''
    DEFAULT_COLOR = colorama.Fore.BLUE


    def __init__(self, arm, wrapper=None, color=DEFAULT_COLOR):
        super().__init__()
        colorama.init(autoreset=True)

        self.arm = arm
        self.style = ShellStyle(color)

        # Optionally, one can supply a wrapper class that wraps input and
        # output to and from the arm for additional processing.
        self.wrapper = wrapper

        self.intro = self.style.theme('Arm Shell\n') + 'First time? Type \'help\'.'
        self.prompt = self.style.theme('> ')

        self.file = None
        self.help = {
            'shell': '',
            'forth': '',
        }
        self.commands = {
            'shell': [],
            'forth': [],
        }


    def cmdloop(self, intro=None):
        ''' Override the command loop to handle Ctrl-C. '''
        self.preloop()
        if self.use_rawinput and self.completekey:
            try:
                import readline
                self.old_completer = readline.get_completer()
                readline.set_completer(self.complete)
                readline.parse_and_bind(self.completekey + ': complete')
            except ImportError:
                pass
        try:
            if intro is not None:
                self.intro = intro
            if self.intro:
                self.stdout.write(str(self.intro)+"\n")
            stop = None
            while not stop:
                if self.cmdqueue:
                    line = self.cmdqueue.pop(0)
                else:
                    if self.use_rawinput:
                        try:
                            line = input(self.prompt)
                        except EOFError:
                            line = 'EOF'
                        except KeyboardInterrupt:
                            line = 'ctrlc'
                    else:
                        self.stdout.write(self.prompt)
                        self.stdout.flush()
                        line = self.stdin.readline()
                        if not len(line):
                            line = 'EOF'
                        else:
                            line = line.rstrip('\r\n')
                line = self.precmd(line)
                stop = self.onecmd(line)
                stop = self.postcmd(stop, line)
            self.postloop()
        finally:
            if self.use_rawinput and self.completekey:
                try:
                    import readline
                    readline.set_completer(self.old_completer)
                except ImportError:
                    pass


    def do_exit(self, arg):
        ''' Exit the shell. '''
        if self.arm.is_connected():
            self.arm.disconnect()
        print('Bye!')
        return True


    def do_ctrlc(self, arg):
        ''' Ctrl-C sends a STOP command to the arm. '''
        print('STOP')
        if self.arm.is_connected():
            self.arm.write('STOP')


    def do_EOF(self, arg):
        ''' EOF exits the shell. '''
        print()
        return self.do_exit(arg)


    def do_quit(self, arg):
        print('Use \'exit\' to close the shell.')


    def do_help(self, arg):
        ''' Print the shell help message. '''
        print('\n'.join(['', self.help['shell'], self.help['forth']]))


    def do_status(self, arg):
        ''' Print information about the arm. '''
        info = self.arm.get_info()
        max_len = len(max(info.keys(), key=len))

        print(self.style.theme('\nArm Status'))
        for key, value in info.items():
            print(self.style.help(key.ljust(max_len + 2), str(value)))
        print()


    def do_connect(self, arg):
        ''' Connect to the arm. '''
        if self.arm.is_connected():
            print(self.style.error('Error: ', 'Arm is already connected.'))
        else:
            try:
                port = self.arm.connect()
                print(self.style.success('Success: ', 'Connected to \'{}\'.'.format(port)))
            except arm.ArmException as e:
                print(self.style.error('Error: ', str(e)))


    def do_disconnect(self, arg):
        ''' Disconnect from the arm. '''
        if not self.arm.is_connected():
            print(self.style.error('Error: ', 'Arm is already disconnected.'))
        else:
            self.arm.disconnect()
            print(self.style.success('Success: ', 'Disconnected.'))


    def do_run(self, arg):
        ''' Load and run an external FORTH script. '''
        if not self.arm.is_connected():
            print(self.style.error('Error: ', 'Arm is not connected.'))
            return

        # Load the script.
        try:
            with open(arg) as f:
                lines = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            print(self.style.error('Error: ', 'Could not find file \'{}\'.'.format(arg)))
            return

        for line in lines:
            if self.wrapper:
                line = self.wrapper.wrap_input(line)
            self.arm.write(line)
            res = self.arm.read()
            if self.wrapper:
                res = self.wrapper.wrap_output(res)
            print(res)


    def do_dump(self, arg):
        ''' Output all bytes waiting in output queue. '''
        if not self.arm.is_connected():
            print(self.style.error('Error: ', 'Arm is not connected.'))
            return
        print(self.arm.dump())


    def complete_run(self, text, line, b, e):
        ''' Autocomplete file names with .forth ending. '''
        # Don't break on path separators.
        text = line.split()[-1]

        # Try to find files with a forth file ending, .fs.
        forth_files = glob.glob(text + '*.fs')

        # Failing that, just try and complete something.
        if len(forth_files) == 0:
            return [f.split(os.path.sep)[-1] for f in glob.glob(text + '*')]

        forth_files = [f.split(os.path.sep)[-1] for f in forth_files]
        return forth_files


    def emptyline(self):
        ''' Called when an empty line entered. Do nothing. '''
        pass


    def default(self, line):
        ''' Commands with no do_* method fall to here. '''
        # Commands that fall through to this method are interpreted as FORTH,
        # and must be in upper case.
        if not line.isupper():
            print(self.style.error('Error: ', 'Unrecognized command.'))
            return

        if self.arm.is_connected():
            if self.wrapper:
                line = self.wrapper.wrap_input(line)
            self.arm.write(line)
            try:
                res = self.arm.read()
            except KeyboardInterrupt:
                # NOTE interrupts aren't recursively handled.
                self.arm.write('STOP')
                res = self.arm.read()
            if self.wrapper:
                res = self.wrapper.wrap_output(res)
            print(res)
        else:
            print(self.style.error('Error: ', 'Arm is not connected.'))


    def get_names(self):
        ''' Get names for autocompletion. '''
        # Overridden to support autocompletion for the ROBOFORTH commands.
        return (['do_' + x for x in self.commands['shell']]
              + ['do_' + x for x in self.commands['forth']])


    def load_commands(self, file_path):
        ''' Load of list of commands and descriptions from a file. '''
        with open(file_path) as f:
            lines = f.readlines()

        commands = [line.split()[0] for line in lines]
        max_len = len(max(commands, key=len))

        text = ''
        for line in lines:
            tokens = line.strip().split()
            text += self.style.help(tokens[0].ljust(max_len + 2),
                                    ' '.join(tokens[1:]) + '\n')
        return commands, text


    def load_forth_commands(self, help_dir):
        ''' Load completion list for ROBOFORTH commands. '''
        try:
            commands, help_text = self.load_commands(os.path.join(help_dir, 'roboforth.txt'))
        except FileNotFoundError:
            print(self.style.warn('Warning: ', 'Failed to load FORTH command list.'))
            return
        self.commands['forth'] = commands
        self.help['forth'] = '\n'.join([self.style.theme('Forth Commands'), help_text])


    def load_shell_commands(self, help_dir):
        ''' Load completion list for shell commands. '''
        try:
            commands, help_text = self.load_commands(os.path.join(help_dir, 'shell.txt'))
        except FileNotFoundError:
            print(self.style.warn('Warning: ', 'Failed to load shell command list.'))
            return
        self.commands['shell'] = commands
        self.help['shell'] = '\n'.join([self.style.theme('Shell Commands'), help_text])


    def preloop(self):
        ''' Executed before the command loop starts. '''
        script_dir = os.path.dirname(os.path.realpath(__file__))
        help_dir = os.path.join(script_dir, HELP_DIR_NAME)
        self.load_forth_commands(help_dir)
        self.load_shell_commands(help_dir)

