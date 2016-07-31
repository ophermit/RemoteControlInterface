from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics
from ipware.ip import get_ip
from .models import Command
from .serializers import CommandSerializer

__author__ = 'ophermit'


@api_view(['GET', 'POST'])
def commands_available(request):
    """ API method "Get available command list"
    """
    response = {
        'commands': dict(Command.COMMAND_CHOICES),
        # The first status should be "Done"
        'completed': [Command.STATUS_DONE, Command.STATUS_DECLINE],
    }
    return Response(response)


class CommandList(generics.CreateAPIView):
    """ API method "Create command"
    """
    serializer_class = CommandSerializer

    def post(self, request, *args, **kwargs):
        request.data[u'ip'] = u'' + get_ip(request)
        return super(CommandList, self).post(request, *args, **kwargs)


class CommandDetail(generics.RetrieveAPIView):
    """ API method "Get command status"
    """
    queryset = Command.objects.all()
    serializer_class = CommandSerializer
