from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_POST


def cadastro(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'GET':
        return render(request, 'cadastro.html')

    username = request.POST.get('username', '').strip()
    email    = request.POST.get('email', '').strip()
    password = request.POST.get('password', '').strip()

    erro = None
    if not username or not email or not password:
        erro = 'Preencha todos os campos.'
    elif len(password) < 6:
        erro = 'A senha deve ter pelo menos 6 caracteres.'
    elif User.objects.filter(username=username).exists():
        erro = 'Este nome de usuário já está em uso.'
    elif User.objects.filter(email=email).exists():
        erro = 'Este e-mail já está cadastrado.'

    if erro:
        return render(request, 'cadastro.html', {
            'erro': erro,
            'username': username,
            'email': email,
        })

    user = User.objects.create_user(username=username, email=email, password=password)
    login(request, user)
    messages.success(request, f'Bem-vindo, {username}! Conta criada com sucesso.')
    return redirect('home')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'GET':
        return render(request, 'login.html', {
            'next': request.GET.get('next', ''),
        })

    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '').strip()
    next_url = request.POST.get('next', '').strip() or 'home'

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        # Garante que o next é uma rota relativa (evita redirect aberto)
        if not next_url.startswith('/'):
            next_url = 'home'
        return redirect(next_url)

    return render(request, 'login.html', {
        'erro': 'Usuário ou senha incorretos.',
        'username': username,
        'next': next_url,
    })


@require_POST
def logout_view(request):
    logout(request)
    return redirect('login')
