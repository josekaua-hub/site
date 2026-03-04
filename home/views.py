from django.shortcuts import render
# Create your views here.

def home(request):
    print('Acessando a view home')
    return render(request, 'home.html')