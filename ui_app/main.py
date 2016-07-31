# -*- coding: utf-8 -*-
__author__ = 'ophermit'
__version__ = '0.1.5'

import kivy
kivy.require('1.9.1')

from kivy import platform
if platform != 'android':
    from kivy.config import Config
    Config.set('graphics', 'show_cursor', '1')
    Config.set('kivy', 'log_level', 'warning')

from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, Clock, NumericProperty,\
    DictProperty, BooleanProperty
from kivy.uix.button import Button
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy import metrics
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
try:
    from kivy.garden.xpopup import XError, XProgress, XAuthorization, XConfirmation
except:
    from xpopup import XError, XProgress, XAuthorization, XConfirmation
from json import dumps
import base64


class AuthEx(XAuthorization):
    """Customizes an auth popup - adds a "host" field
    """
    width = NumericProperty(metrics.dp(400))
    required_fields = DictProperty(
        {'login': 'Login', 'password': 'Password', 'host': 'Host'})

    host = StringProperty(u'')

    def _get_form(self):
        layout = super(AuthEx, self)._get_form()
        pnl = BoxLayout(size_hint_y=None, height=metrics.dp(28), spacing=5)
        pnl.add_widget(Label(text='Host:', halign='right',
                             size_hint_x=None, width=metrics.dp(80)))
        pnl.add_widget(TextInput(id='host', multiline=False, font_size=14,
                                 text=self.host))
        layout.add_widget(pnl)
        layout.add_widget(Widget())
        return layout


class RemoteControlUI(BoxLayout):
    """The main app layout
    """

    # Auth properties
    login = StringProperty(u'')
    password = StringProperty(u'')
    host = StringProperty('')

    # Represents the last command which was accepted
    last_accepted_command = StringProperty('')

    # Bound to the "Info" label
    info_text = StringProperty('')

    # Command execution confirmation flag
    need_confirm = BooleanProperty(True)

    def __init__(self, **kwargs):
        # ID of the command being executed
        self._cmd_id = None

        # List of the "completed" statuses.
        # The first status should be "Done"
        self._completed = []

        # If True - sends a request to retrieve a command status
        self._wait_completion = False

        # requested command
        self._command = (0, '')

        super(RemoteControlUI, self).__init__(
            orientation='vertical', spacing=2, padding=3, **kwargs)

        # Control buttons panel
        pnl_controls = BoxLayout(size_hint_y=None, height=metrics.dp(35))
        pnl_controls.add_widget(
            Button(text='Refresh', on_release=self._get_commands))
        pnl_controls.add_widget(
            Button(text='Close', on_release=App.get_running_app().stop))
        self.add_widget(pnl_controls)

        # Command buttons panel
        self._pnl_commands = BoxLayout(orientation='vertical')
        self.add_widget(self._pnl_commands)

        # Info panel
        lbl_info = Label(
            text=self.info_text, size_hint_y=None, height=metrics.dp(35))
        self.bind(info_text=lbl_info.setter('text'))
        self.add_widget(lbl_info)

    # ============= HTTP REQUEST ==============
    def _get_auth(self):
        # Encodes basic authorization data
        cred = ('%s:%s' % (self.login, self.password))
        return 'Basic %s' %\
               base64.b64encode(cred.encode('ascii')).decode('ascii')

    def _send_request(self, url, success=None, error=None, params=None):
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-type': 'application/json',
            'Authorization': self._get_auth()
        }

        UrlRequest(
            url=self.host + url, timeout=30, req_headers=headers,
            req_body=None if params is None else dumps(params),
            on_success=success, on_error=error, on_failure=error)

    # =========== GET COMMAND LIST ===========
    def _get_commands(self, instance=None):
        # Implements API-call "Get available command list"
        self._progress_start('Trying to get command list')
        self._send_request(
            'commands_available/', params=[],
            success=self._get_commands_result, error=self._get_commands_error)

    def _get_commands_result(self, request, response):
        # Parses API-call response
        try:
            self._pnl_commands.clear_widgets()

            # Create command buttons
            for code, command in sorted(
                    response['commands'].items(),
                    key=lambda x: int(x[0])):
                btn = Button(
                    id=code, text=command, on_release=self._btn_command_click)
                self._pnl_commands.add_widget(btn)

            self._completed = response['completed']

            # Save correct host and login in the app configuration
            App.get_running_app().config.set('auth', 'login', self.login)
            App.get_running_app().config.set('auth', 'host', self.host)

            self._progress_complete('Command list received successfully')
        except Exception as e:
            self._get_commands_error(request, str(e))

    def _get_commands_error(self, request, error):
        self._progress_complete()
        XError(text=str(error)[:256], buttons=['Retry', 'Re-enter', 'Exit'],
               on_dismiss=self._get_commands_error_dismiss)

    def _get_commands_error_dismiss(self, instance):
        if instance.button_pressed == 'Exit':
            App.get_running_app().stop()
        elif instance.button_pressed == 'Re-enter':
            self._login()
        elif instance.button_pressed == 'Retry':
            self._get_commands()

    # ============= SEND COMMAND =============
    def _btn_command_click(self, button):
        self._command = (button.id, button.text)
        if self.need_confirm:
            XConfirmation(
                text='Send command "%s" ?' % button.text,
                on_dismiss=self._send_command)
        else:
            self._send_command(None)

    def _send_command(self, instance):
        # Implements API-call "Create command"
        if instance and not instance.is_confirmed():
            return

        self._cmd_id = None
        self._wait_completion = True
        self._progress_start('Processing command "%s"' % self._command[1])
        self._send_request(
            'commands/', params={'code': self._command[0]},
            success=self._send_command_result, error=self._send_command_error)

    def _send_command_result(self, request, response):
        # Parses API-call response
        try:
            if response['status'] not in self._completed:
                # Executing in progress
                self._cmd_id = response['id']
                if self._wait_completion:
                    Clock.schedule_once(self._get_status, 1)
            else:
                # Command "completed"
                if response['status'] == self._completed[0]:
                    self.last_accepted_command = response['code_dsp']
                self._progress_complete(
                    'Command "%s" is %s' %
                    (response['code_dsp'], response['status_dsp']))
        except Exception as e:
            XError(text=str(e)[:256])

    def _send_command_error(self, request, error):
        self._progress_complete()
        XError(text=str(error)[:256])

    # ========== GET COMMAND STATUS ==========
    def _get_status(self, pdt=None):
        # Implements API-call "Get command status"
        if not self._cmd_id:
            return

        self._send_request(
            'commands/%s/' % self._cmd_id, success=self._send_command_result,
            error=self._send_command_error)

    # ============= LOGIN POPUP ==============
    def _login(self):
        AuthEx(login=self.login, password=self.password, host=self.host,
               autologin=None, pos_hint={'top': 0.99},
               on_dismiss=self._login_dismiss)

    def _login_dismiss(self, instance):
        if instance.is_canceled():
            App.get_running_app().stop()
            return

        self.login = instance.get_value('login')
        self.password = instance.get_value('password')
        self.host = instance.get_value('host')

        self._get_commands()

    # ============= PROGRESS BAR ==============
    def _progress_start(self, text):
        self.popup = XProgress(
            title='RemoteControl', text=text, buttons=['Close'],
            on_dismiss=self._progress_dismiss)
        self.popup.autoprogress()

    def _progress_dismiss(self, instance):
        self._wait_completion = False

    def _progress_complete(self, text=''):
        if self.popup is not None:
            self.popup.complete(text=text, show_time=0 if text is None else 1)

    # =========================================
    def on_last_accepted_command(self, instance, value):
        self.info_text = 'Last accepted command: %s' % value
        App.get_running_app().config.set(
            'common', 'last_accepted_command', value)

    def start(self):
        if not self.login or not self.password or not self.host:
            self._login()
        else:
            self._get_commands()


class RemoteControlApp(App):
    remote = None

    def open_settings(self, *largs):
        # Prevents the settings panel opening
        pass

    def build_config(self, config):
        # Setting up default configuration
        config.setdefaults('auth', {
            'host': 'http://localhost:8000/remotecontrol/',
            'login': '',
        })
        config.setdefaults('common', {
            'last_accepted_command': 'None'
        })

    def build(self):
        config = self.config

        # Building app layout
        self.remote = RemoteControlUI(
            login=config.get('auth', 'login'), password='',
            host=config.get('auth', 'host'),
            last_accepted_command=config.get(
                'common', 'last_accepted_command'))

        if platform != 'android':
            self.remote.need_confirm = False

        return self.remote

    def on_pause(self):
        # Prevents application stop on pause mode
        return True

    def on_stop(self):
        # Saving configuration changes
        self.config.write()

    def on_start(self):
        self.remote.start()


RemoteControlApp().run()
