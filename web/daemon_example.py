__author__ = 'ophermit'

if __name__ == '__main__':
    import os
    # !!! IMPORTANT !!!
    # Change <MY_SITE_NAME> to the name of your django project
    # !!! IMPORTANT !!!
    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "<MY_SITE_NAME>.settings")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")

    # Import IRemoteControl only after setting DJANGO_SETTINGS_MODULE
    from remotecontrol.interface.control import *
    from time import sleep


    class MyRemoteControl(IRemoteControl):
        """ Example of custom remote control implementation
        """

        # All IP allowed
        IP_WHITE_LIST = []
        # Remove this if you don't want to see the debug messages
        DEBUG = True

        def __init__(self):
            """ Defining callbacks for custom command
            """

            self.user_commands = {
                USER_CODE1: self.command1,
                USER_CODE2: self.command2,
            }
            super(MyRemoteControl, self).__init__()

        def _restart_stuff(self):
            print('... Doing some stuff on restart ...')
            # Emulation of hard work :)
            sleep(5)

        def command1(self, command):
            """ Custom command #1
            """

            self._process_command(command)
            print('... Doing some stuff on Command1 ...')
            # Emulation of hard work :)
            sleep(5)

            # Marks the command as 'done'
            self._done_command(command)
            print('... Command1 complete ...')

        def command2(self, command):
            """ Custom command #2
            """

            raise ValueError('Emulating an error')


    class AbstractDaemon(object):
        """ Abstract superclass for daemon. Just for example.
        """

        def __init__(self):
            super(AbstractDaemon, self).__init__()

        @staticmethod
        def do_something():
            print('Do something....')


    class MyDaemon(AbstractDaemon, MyRemoteControl):
        """ Implementation of daemon with custom remote control
        """

        def __init__(self):
            super(MyDaemon, self).__init__()

        def start(self):
            while True:
                self.check_commands()
                self.do_something()
                sleep(.5)

    daemon = MyDaemon()
    daemon.start()
