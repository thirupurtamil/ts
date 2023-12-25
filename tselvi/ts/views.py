from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from ts.models import Category,Product 

# Create your views here.


class ProductList(ListView):
    model = Product 

class CategoryList(ListView):
    model = Category


def bt(request):
    return render (request,'ts/bt.html')


def bt1(request):
    category=Category.objects.filter(status=0)
    
    cc={'category':category}
    return render (request,'ts/bt1.html',)
