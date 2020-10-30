from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.

User = get_user_model()

class Message(models.Model):
    author = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}".format(self.pk) 

class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name='chats')
    messages = models.ManyToManyField(Message, blank=True)

    def __str__(self):
        return "{}".format(self.pk) 

    def get_roomname(username, friend):
        def get_userList(user):
            chats = Chat.objects.filter(participants=user.id)
            lst_user = []
            for chat in chats:
                lst_user.append(chat.id)
            return lst_user

        user_1 = User.objects.filter(username=username)[0]
        lst_user_1 = get_userList(user_1)

        user_2 = User.objects.filter(username=friend)[0]
        lst_user_2 = get_userList(user_2)
        
        res = list(set(lst_user_1).intersection(lst_user_2))
        if len(res) != 0:
            return res
        else:
            new_chat = Chat.objects.create()
            new_chat.participants.add(user_1)
            new_chat.participants.add(user_2)
            new_chat.save()
            return [new_chat.id]
    
    def get_friendname(roomname, username):
        chat = Chat.objects.filter(id=roomname)[0] 

        participants = chat.participants.all()
        user1 = participants[0].username

        if user1 != username:
            return user1
        else:
            return participants[1].username

    def last_10_messages(roomname):
        chat = Chat.objects.filter(id=roomname)[0]
        return chat.messages.order_by('-timestamp').all()[:10]
