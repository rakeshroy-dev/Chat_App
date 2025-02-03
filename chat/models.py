from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class ChatRoom(models.Model):
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_chat_rooms')
    users = models.ManyToManyField(User, related_name='accessible_chat_rooms', blank=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    chatroom = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='message_images/', null=True, blank=True)  # Image field


    @property
    def imageURL(self):
        if self.image:
            return self.image.url
        else:
            return ''

    def __str__(self):
        return f"{self.sender.username}: {self.message}"