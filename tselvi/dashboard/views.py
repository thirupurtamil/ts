from django.shortcuts import render


# Create your views here.


def pis(request):
    return render(request,'homepage/index.html')

