# Remote Control Interface

Simple remote control for daemon.

This is an example of how to write REST API client for android on Python.
However if you are interested on the improvements - create an issue and describe your idea.

Android app based on the Kivy framework. Works on Python 2.7 and 3.x.
Server-side code based on Django (tested on 1.9.6), uses Django REST framework.


Demo
====

https://www.youtube.com/watch?v=EqxDIJOSegw


Features
========

Project content:

* ui_app - Android app folder
    * main.py - app implementation
    * android.txt - settings for Kivy launcher
    * buildozer.spec - configuration for build .apk
* web - Django project folder
    * remotecontrol - Django app with REST API implementation
        * interface - server-side API
            * control.py - implementation of IRemoteControl class
            * user_commands.py - custom commands definition
        * another Django app modules
    * daemon_example.py - demo daemon with IRemoteControl usage

Usage example:

    class MyDaemon(IRemoteControl):
        def core(self):
            # daemon logic

        def main_loop(self):
            while True:
                self.check_commands()
                self.core()

Current version supports following service commands:

* CODE_PAUSE - Pausing daemon execution (check_commands() has a loop until CODE_RESUME is received)
* CODE_RESUME - Resuming daemon execution
* CODE_RESTART - Restarting daemon (requires custom logic)
* CODE_REMOTE_OFF - Disabling remote control (all the next commands are ignored)

NOTE:

    Receiving CODE_RESTART has no effect. Implement method _restart_stuff() in your subclass to get effect.
    Otherwise CODE_RESTART is ignored.


If you want to use custom commands, you need:

* write custom commands definition (user_commands.py):

        USER_COMMANDS = (
            (101, 'Command #1'),
            (102, 'Command #2'),
        )
        
* implement logic for each command:

        class MyDaemon(IRemoteControl):
            def __init__(self):
                self.user_commands = {
                    101: self.command1,
                    102: self.command2,
                }
                super(MyDaemon, self).__init__()

            def command1(self, command):
                # command #1 logic
                self._done_command(command)
    
            def command2(self, command):
                # command #2 logic
                self._done_command(command)
                
NOTE:

    The custom command logic must mark command as 'done' (._done_command()) or as 'declined' (._ignore_command()).
                
That's all!
    
    
Installation & Requirements
===========================

SERVER-SIDE

0. Python 2.7 (or higher) or Python 3.4 (or higher)

1. Django (1.9.6 recommended)

2. Django apps

        pip install django-ipware
        pip install djangorestframework
        
3. Download and unpack `RemoteControlInterface`

4. Make preparations

        python web\manage.py makemigrations remotecontrol
        python web\manage.py migrate remotecontrol

5. Run server:
        
        python web\manage.py runserver

6. Run demo daemon:
        
        python mysite\daemon_example.py


CLIENT-SIDE (on android via Kivy launcher)

1. Install `Kivy launcher` (http://play.google.com/store/apps/details?id=org.kivy.pygame)

2. Download and unpack `XPopup` to `ui_app` folder
   (https://github.com/kivy-garden/garden.xpopup)

3. Copy `ui_app` folder to `/sdcard/kivy/`


CLIENT-SIDE (as android app)

1. Install `Kivy` library
   (https://kivy.org/#download)

2. Install `Kivy Garden` (if not already installed)

        pip install kivy-garden

3. Install `Buildozer`
   (http://kivy.org/docs/guide/packaging-android.html#buildozer)

4. Build app from `ui_app` folder

        buildozer android debug
        
5. The resulting .apk install on your android device


CLIENT-SIDE (on desktop)

1. Install `Kivy` library
   (https://kivy.org/#download)

2. Install `Kivy Garden` (if not already installed)

        pip install kivy-garden

3. Install `XPopup` extension
    
        garden install xpopup
    
4. Run `RemoteControl` app

        python ui_app\main.py


Version history
===============
* 0.1
    
    Initial release