from django.contrib import admin
from ipware.ip import get_ip
from .models import Command


@admin.register(Command)
class CommandAdmin(admin.ModelAdmin):
    list_display = ('created', 'code', 'colored_status', 'ip')
    list_filter = ('code', 'status', 'ip')
    fields = (('code', 'status'), )

    def save_model(self, request, obj, form, change):
        if obj.ip is None:
            obj.ip = get_ip(request)
        obj.save()
