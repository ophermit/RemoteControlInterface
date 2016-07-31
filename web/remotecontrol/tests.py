import base64
from django.test import TestCase
from django.test import Client
import json
from .models import *

__author__ = 'ophermit'


class CommandTests(TestCase):
    def test_create_command_without_ip(self):
        command = Command(code=CODE_RESUME)
        err = ''
        try:
            command.save()
        except Exception as e:
            err = str(e)
        self.assertEqual(err, 'remotecontrol_command.ip may not be NULL')

    def create_command(self):
        command_new = Command(code=CODE_PAUSE, ip='0.0.0.0')
        command_new.save()
        return command_new.pk

    def test_create_command(self):
        command_get = Command.objects.get(pk=self.create_command())
        self.assertEqual(command_get.status, Command.STATUS_CREATE)

    def test_process_command(self):
        command_get = Command.objects.get(pk=self.create_command())
        command_get.set_process()
        command_new = Command.objects.get(pk=command_get.pk)
        self.assertEqual(command_new.status, Command.STATUS_PROCESS)

    def test_done_command(self):
        command_get = Command.objects.get(pk=self.create_command())
        command_get.set_done()
        command_new = Command.objects.get(pk=command_get.pk)
        self.assertEqual(command_new.status, Command.STATUS_DONE)

    def test_decline_command(self):
        command_get = Command.objects.get(pk=self.create_command())
        command_get.set_decline()
        command_new = Command.objects.get(pk=command_get.pk)
        self.assertEqual(command_new.status, Command.STATUS_DECLINE)


class RESTTests(TestCase):
    TEST_LOGIN = 'test'
    TEST_PASS = 'test'
    URL_PREFIX = '/remotecontrol/'

    def setUp(self):
        def get_auth(login, password):
            cred = ('%s:%s' % (login, password))
            return 'Basic %s' % base64.b64encode(cred.encode('ascii')).decode('ascii')

        from django.contrib.auth.models import User
        User.objects.create_superuser(self.TEST_LOGIN, 'admin@test.com', self.TEST_PASS)
        self.extra = {
            'HTTP_AUTHORIZATION': get_auth(self.TEST_LOGIN, self.TEST_PASS)
        }
        self.client = Client()

    def test_get_commands_list(self):
        response = self.client.get(self.URL_PREFIX + 'commands_available/', **self.extra)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(self.URL_PREFIX + 'commands_available/', **self.extra)
        self.assertEqual(response.status_code, 200)

    def test_send_command(self):
        params = {'code': CODE_PAUSE}
        response = self.client.post(self.URL_PREFIX + 'commands/', data=params, **self.extra)
        self.assertEqual(response.status_code, 201)
        cmd = json.loads(response.content)
        self.assertEqual(cmd['status'], Command.STATUS_CREATE)
        response = self.client.get(self.URL_PREFIX + 'commands/', data=params, **self.extra)
        self.assertEqual(response.status_code, 405)

    def test_get_command_status(self):
        params = {'code': CODE_RESUME}
        response = self.client.post(self.URL_PREFIX + 'commands/', data=params, **self.extra)
        self.assertEqual(response.status_code, 201)
        cmd = json.loads(response.content)
        self.assertEqual(cmd['status'], Command.STATUS_CREATE)
        response = self.client.get(self.URL_PREFIX + 'commands/%d/' % cmd['id'], **self.extra)
        self.assertEqual(response.status_code, 200)
