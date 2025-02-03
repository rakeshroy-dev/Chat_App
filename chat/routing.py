from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatRoomConsumer.as_asgi()),
]

# from django.urls.converters import register_converter, StringConverter

# class AlphanumericConverter(StringConverter):
#     regex = '[a-zA-Z0-9]+'

# register_converter(AlphanumericConverter, 'alnum')

# websocket_urlpatterns = [
#     re_path('ws/chat/<alnum:room_name>/', consumers.ChatRoomConsumer.as_asgi()),
# ]