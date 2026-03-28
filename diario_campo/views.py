from django.shortcuts import render

# Create your views here.

def diario_campo(request):
    return render(request,'diario_campo.html')