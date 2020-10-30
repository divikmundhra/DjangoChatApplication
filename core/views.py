from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.utils.safestring import mark_safe
import json


def registerPage(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user + '. Login to continue' )
                return redirect("/")
            else:
                messages.info(request, 'Please fill the details properly')

        context = {'form': form}
        return render(request, 'core/register.html', context)
    

def loginPage(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                print('|| incorrect login credentials')
                messages.info(request, 'Username OR password is incorrect')


        context = {}
        return render(request, 'core/login.html', context)


def logoutPage(request):
    logout(request)
    print('|| user logged out')
    return redirect('login/')


@login_required(login_url="login/")
def homePage(request):
    return redirect('create/connect/')


def get_current_users():
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    user_id_list = []
    for session in active_sessions:
        data = session.get_decoded()
        user_id_list.append(data.get('_auth_user_id', None))
    # Query all logged in users based on id list
    return User.objects.filter(id__in=user_id_list)


@login_required(login_url="login/")
def room(request, room_name):
    current_users = get_current_users()
    return render(request, 'core/chat.html', {
        'room_name': mark_safe(json.dumps(room_name)),
        'username': mark_safe(json.dumps(request.user.username)),
        # 'current_users': mark_safe(json.dumps(current_users))
        'current_users': current_users
    })


def forward(request):
    return redirect("login/")

