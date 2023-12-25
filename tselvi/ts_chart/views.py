from django.shortcuts import render,redirect
from . models import Product
from . forms import ProductForm
from django.urls import reverse_lazy
from django.urls import (get_resolver, get_urlconf, resolve, reverse, NoReverseMatch)
# Create your views here.

def ichart(request):
    products = Product.objects.all()

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ichart')
    else:
        form = ProductForm()        

    context = {
        "products": products,
        "form": form
    }

    return render(request, 'ts_chart/ichart.html', context)

def ichartdata(request): 
    products = Product.objects.all()

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ichartdata')
    else:
        form = ProductForm()        

    context = {
        "products": products,
        "form": form
    }

    return render(request, 'ts_chart/ichartdata.html',context )


def ichartview(request):
    products = Product.objects.all()
    form = ProductForm()
    context = {
        "products": products,
        "form": form
    }
    return render (request,'ts_chart/ichartview.html',context)
