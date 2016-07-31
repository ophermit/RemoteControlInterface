import django
django.setup()

from time import sleep
from remotecontrol.models import *

__author__ = 'ophermit'


class IRemoteControl(object):
    """ Remote Control Interface. Abstract class.
    Do not use it directly.

    Usage example:
        class MyDaemon(IRemoteControl):
            def core(self):
                # daemon logic

            def main_loop(self):
                while True:
                    self.check_commands()
                    self.core()
    """

    DEBUG = False
    IP_WHITE_LIST = ['127.0.0.1']

    REMOTE_ENABLED = True
    ''' Used by command CODE_REMOTE_OFF
    '''

    user_commands = {}
    ''' Dictionary for custom commands (key - command code, value - callable or class method).
    Fill it in your subclass if you want use custom commands.
    '''

    def __get_command(self):
        """ Gets the first unprocessed command.
        Marks the command as declined if it has wrong IP or remote is disabled.

        :return: Command object
        """

        try:
            commands = Command.objects.processing()
            if len(commands) == 0:
                commands = Command.objects.created()
        except Exception as e:
            print('Exception: %s' % str(e))
            commands = []

        if len(commands) == 0:
            return None

        command = commands[0]
        self._debug('Received command "%s" in status "%s"'
                    % (command.get_code_display(), command.get_status_display()))

        if self.IP_WHITE_LIST and command.ip not in self.IP_WHITE_LIST:
            self._debug('Wrong IP: %s' % command.ip)
        elif not self.REMOTE_ENABLED:
            self._debug('Remote is disabled')
        else:
            return command

        self._ignore_command(command)

    def __restart(self, command):
        """ Wrapper for the restart method.

        :param command: Command object
        """

        if command.is_created():
            self._process_command(command)
            print('... Restarting ...')
            try:
                self._restart_stuff()
            except:
                self._ignore_command(command)
        self._done_command(command)
        print('... Restart complete ...')

    def __update_command(self, method):
        """ Wrapper for update the command.

        :param method: Command update method
        """

        try:
            method()
        except Exception as e:
            self._debug('Cannot update command. Reason: %s' % e)

    def _debug(self, message):
        if self.DEBUG:
            print('    --> %s' % message)

    def _ignore_command(self, command):
        self._debug('Unexpected command "%s" - ignoring' % command.get_code_display())
        self.__update_command(command.set_decline)

    def _process_command(self, command):
        self._debug('Processing command "%s"' % command.get_code_display())
        self.__update_command(command.set_process)

    def _done_command(self, command):
        self._debug('Done command "%s"' % command.get_code_display())
        self.__update_command(command.set_done)

    def _check_user_commands(self, command):
        """ Processes the user commands.

        :param command: Command object
        """

        method = self.user_commands.get(command.code, None)
        if callable(method):
            try:
                method(command)
                return
            except Exception as e:
                print('Exception: %s' % str(e))
        self._ignore_command(command)

    def _restart_stuff(self):
        """ Implement restart logic in your subclass.
        """
        raise NotImplementedError

    def check_commands(self):
        """ Logic of service commands.
        If the received CODE_REMOTE_OFF - all the next commands are ignored.
        If the received CODE_RESTART - pause flag is set to False.
        If the received CODE_PAUSE - there will be a loop until CODE_RESUME is received.
            All other commands are ignored.
        """

        pause = False
        enter = True
        while enter or pause:
            enter = False
            command = self.__get_command()
            if command is not None:
                if command.code == CODE_REMOTE_OFF:
                    self._done_command(command)
                    print('... !!! WARNING !!! Remote control is DISABLED ...')
                    self.REMOTE_ENABLED = False
                elif command.code == CODE_RESTART:
                    self.__restart(command)
                    # ignore the current pause after restart
                    pause = False
                elif pause:
                    if command.code == CODE_RESUME:
                        self._done_command(command)
                        print('... Resuming ...')
                        pause = False
                    else:
                        self._ignore_command(command)
                else:
                    if command.code == CODE_PAUSE:
                        self._done_command(command)
                        print('... Waiting for resume ...')
                        pause = True
                    else:
                        self._check_user_commands(command)
            elif pause:
                sleep(1)
