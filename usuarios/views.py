from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')

    if User.objects.filter(username=username).exists():
        return HttpResponse('Usuário já existe')

    if User.objects.filter(email=email).exists():
        return HttpResponse('Email já está em uso')

    User.objects.create_user(username=username, email=email, password=password)
    return HttpResponse('Usuário cadastrado com sucesso')

    
    

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse('Login bem-sucedido')
        else:
            return HttpResponse('Credenciais inválidas')
    else:

        return render(request, 'login.html')
    

# faz com que necessite de login para acessar o planejador, caso contrário, exibe uma mensagem de boas-vindas
#melhorar essa parte
# def planejador(request):
#     if request.user.is_authenticated:
#         return HttpResponse('aqui é o planejador')
     
#     return HttpResponse('Bem-vindo ao planejador, ' + request.user.username + '!')