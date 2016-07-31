from django.conf.urls import url
from . import views

__author__ = 'ophermit'

app_name = 'remotecontrol'

urlpatterns = [
    url(r'^commands_available/$', views.commands_available),
    url(r'^commands/$', views.CommandList.as_view()),
    url(r'^commands/(?P<pk>[0-9]+)/$', views.CommandDetail.as_view()),
]
