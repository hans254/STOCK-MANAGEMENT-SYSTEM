from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.http import HttpResponse
import csv
from django.contrib import messages

# Create your views here.
def home(request):
    title = 'Welcome: This is the Home Page'
    context = {
        'title': title,
    }
    return render(request, "home.html", context)

'''
def list_items(request):
    header = 'List of Items'
    form = StockSearchForm(request.POST or None)
    queryset = stock.objects.all()
    context = {
        'header': header,
        'queryset': queryset,
        'form': form,
    }
    if request.method == 'POST':
        queryset = stock.objects.filter(category__icontains=form['category'].value(), 
        item_name__icontains=form['item_name'].value())
        context = {
            "form": form,
            "header": header,
            "queryset": queryset
        }
'''
def list_items(request):
    form = ItemFilterForm(request.POST or None)
    queryset = stock.objects.all()

    if request.method == 'POST' and form.is_valid():
        category_name = form.cleaned_data.get('category')
        if category_name:
            queryset = queryset.filter(category__name__icontains=category_name)

            if form['export_to_CSV']. Value()== True:
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="List of stock.csv"'
                writer = csv.writer(response)
                writer.writerow(['CATEGORY','ITEM_NAME','QUANTITY'])
                isinstance =queryset
                for Stock in isinstance:
                    writer.writerow([Stock.category, Stock.item_name, Stock.quantity])
                    return response


    context = {
        'form': form,
        'queryset': queryset,
    }

    return render(request, 'list_items.html', context)


def add_items(request):
    form = StockCreateForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Successfully Saved')
        return redirect(list_items)
    context = {
        'form': form,
        'title': 'add_item'
    }
    return render(request, "add_items.html", context)

def update_items(request, pk):
    queryset = stock.objects.get(id=pk)
    form = StockUpdateForm(instance=queryset)
    if request.method == 'POST':
        form = StockUpdateForm(request.POST, instance=queryset)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully Saved')
            return redirect('/list_items')
    context = {
        'form': form
    }
    return render(request, 'add_items.html', context)

def delete_items(request, pk):
    queryset = stock.objects.get(id=pk)
    if request.method == 'POST':
        queryset.delete()
        messages.success(request, 'Deleted Successfully')
        return redirect('/list_items')
    return render(request, 'delete_items.html')