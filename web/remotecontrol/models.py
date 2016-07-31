from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from .interface.user_commands import *

__author__ = 'ophermit'


CODE_PAUSE = 1
CODE_RESUME = 2
CODE_RESTART = 3
CODE_REMOTE_OFF = 4

SERVICE_COMMANDS = (
    (CODE_RESTART, 'Restart'),
    (CODE_PAUSE, 'Pause'),
    (CODE_RESUME, 'Resume'),
    (CODE_REMOTE_OFF, 'Disable remote control'),
)


COMMANDS = SERVICE_COMMANDS + USER_COMMANDS


class CommandManager(models.Manager):
    def created(self):
        return super(CommandManager, self).get_queryset().filter(
            status=Command.STATUS_CREATE).order_by('created')

    def processing(self):
        return super(CommandManager, self).get_queryset().filter(
            status=Command.STATUS_PROCESS).order_by('created')


@python_2_unicode_compatible
class Command(models.Model):
    STATUS_CREATE = 1
    STATUS_PROCESS = 2
    STATUS_DONE = 3
    STATUS_DECLINE = 4

    STATUS_CHOICES = (
        (STATUS_CREATE, 'Created'),
        (STATUS_PROCESS, 'In progress...'),
        (STATUS_DONE, 'DONE'),
        (STATUS_DECLINE, 'Declined'),
    )

    STATUS_COLORS = {
        STATUS_CREATE: '000000',
        STATUS_PROCESS: 'FFBB00',
        STATUS_DONE: '00BB00',
        STATUS_DECLINE: 'FF0000',
    }

    COMMAND_CHOICES = COMMANDS

    objects = CommandManager()

    created = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField()
    code = models.IntegerField(choices=COMMAND_CHOICES)
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_CREATE)

    def colored_status(self):
        return '<span style="color: #%s;">%s</span>' % (self.STATUS_COLORS[self.status], self.get_status_display())
    colored_status.allow_tags = True
    colored_status.short_description = 'Status'

    def status_dsp(self):
        return self.get_status_display()

    def code_dsp(self):
        return self.get_code_display()

    def __str__(self):
        return '[%s] "%s" in "%s" from %s'\
               % (self.created.strftime('%Y-%m-%d %H:%M:%S'), self.get_code_display(),
                  self.get_status_display(), self.ip)

    #  ===== Status check methods =====
    def is_created(self):
        return self.status == self.STATUS_CREATE

    def is_processing(self):
        return self.status == self.STATUS_PROCESS

    def is_done(self):
        return self.status == self.STATUS_DONE

    def is_declined(self):
        return self.status == self.STATUS_DECLINE

    #  ===== Status set methods =====
    def set_process(self):
        self.__update_command(Command.STATUS_PROCESS)

    def set_done(self):
        self.__update_command(Command.STATUS_DONE)

    def set_decline(self):
        self.__update_command(Command.STATUS_DECLINE)

    def __update_command(self, status):
        self.status = status
        self.save()
