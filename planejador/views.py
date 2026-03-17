from django.shortcuts import render
# Create your views here.

def analise(request):
    return render(request, 'planejador.html')

