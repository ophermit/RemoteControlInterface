from rest_framework import serializers
from .models import Command

__author__ = 'ophermit'


class CommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Command
        fields = ('status', 'code', 'id', 'status_dsp', 'code_dsp', 'ip')
