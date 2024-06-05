from django.shortcuts import render, redirect
from .models import *
from .forms import *

# Create your views here.
def home(request):
    title = 'Welcome: This is the Home Page'
    context = {
        'title': title,
    }
    return render(request, "home.html", context)

def list_items(request):
    title = 'list of Items'
    queryset = stock.objects.all()
    context = {
        'title': title,
        'queryset': queryset
    }
    return render(request, "list_items.html", context)

def add_items(request):
    form = StockCreateForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect(list_items)
    context = {
        'form': form,
        'title': 'add_item'
    }
    return render(request, "add_items.html", context)