from django.contrib.auth import get_user_model
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from . import models
from .models import Chat, Message


User = get_user_model()

class ChatConsumer(WebsocketConsumer):

    def get_roomname(self, data):
        res = Chat.get_roomname(username=data["user"], friend=data["friend"])
        if len(res) == 1:
            content = {
            'command': 'get_roomname',
            'roomname': res[0]
            }
            self.send_message(content)

    def get_friendname(self, data):
        friendname = Chat.get_friendname(roomname=data["roomname"], username=data["username"])
        if friendname != None:
            content = {
            'command': 'get_friendname',
            'friendname': friendname
            }
            self.send_message(content)

    def fetch_messages(self, data):
        if data["roomname"] != "connect":
            messages = Chat.last_10_messages(data["roomname"])
            content = {
                'command': 'fetch_message',
                'messages': self.messages_to_json(messages)
            }
            self.send_message(content)
    

    def new_message(self, data):
        author = data['from']
        author_user = User.objects.filter(username=author)[0]
        message = models.Message.objects.create(author=author_user, content=data['message'])
        chat = Chat.objects.filter(id=data["roomname"])[0]
        chat.messages.add(message)
        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        return self.send_chat_message(content)

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        return {
            'author': message.author.username,
            'content': message.content,
            'timestamp': str(message.timestamp)
        }
    
    commands = {
        'get_roomname': get_roomname,
        'fetch_messages': fetch_messages,
        'new_message': new_message,
        'get_friendname': get_friendname
    }
    
    # Join room group
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'create_%s' % self.room_name

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    # Leave room group
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data) # call the function fetch_message or new_message

    def send_chat_message(self, message):
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps(message))

    