from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.http import HttpResponse
import csv
from django.contrib import messages
from django.core.paginator import Paginator

# Create your views here.
def home(request):
    title = 'Welcome: This is the Home Page'
    context = {
        'title': title,
    }
    return redirect('/list_items.html')
    #return render(request, "home.html", context)

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
    header = 'List of Items'
    form = ItemFilterForm(request.POST or None)
    queryset = stock.objects.all().order_by('id')
    category_name = request.GET.get('category_name')
    if category_name:
        queryset = queryset.filter(category__name__icontains=category_name)
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)

    if request.method == 'POST' and form.is_valid():
        category_name = form.cleaned_data.get('category')
        item_name = form.cleaned_data.get('item_name')
        if category_name and item_name:
            queryset = queryset.filter(category__name__icontains=category_name)

            if form['export_to_CSV'].value()== True:
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
        'title': 'Add Item'
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

def stock_detail(request, pk):
    queryset = stock.objects.get(id=pk)
    context = {
        'queryset': queryset,
    }
    return render(request, 'stock_detail.html', context)

def issue_items(request, pk):
    queryset = stock.objects.get(id=pk)
    form = IssueForm(request.POST or None, instance = queryset)
    if form.is_valid():
        instance = form.save(commit=False)
        #instance.recieved_quantity = 0
        instance.quantity -= instance.issue_quantity
        instance.issue_by = str(request.user)
        messages.success(request, 'Issued SUCCESSFULLY.' + str(instance.quantity) + ' ' + str(instance.item_name) + 's now left in store')
        instance.save()
        issue_history = StockHistory(
            id = instance.id,
            last_updated = instance.last_updated,
            category_id = instance.category_id,
            item_name = instance.item_name,
            quantity = instance.quantity,
            issue_to = instance.issue_to,
            issue_by = instance.issue_by,
            issue_quantity = instance.issue_quantity
        )
        issue_history.save()
        return redirect('/stock_detail/' + str(instance.id))

    context = {
        'title': 'Issue ' + str(queryset.item_name),
        'queryset': queryset,
        'form': form,
        'username': 'Issue By: ' + str(request.user),
    }
    return render(request, 'add_items.html', context)

def receive_items(request, pk):
    queryset =stock.objects.get(id=pk)
    form = RecieveForm(request.POST or None, instance = queryset)
    if form.is_valid():
        instance = form.save(commit=False)
        #instance.issue_quantity = 0
        instance.quantity += instance.recieved_quantity
        instance.recieve_by = str(request.user)
        instance.save()
        receive_history = StockHistory(
            id = instance.id,
            last_updated = instance.last_updated,
            category_id = instance.category_id,
            item_name = instance.item_name,
            quantity = instance.quantity,
            recieved_quantity = instance.recieved_quantity,
            receive_by = instance.receive_by
        )
        receive_history.save()
        messages.success(request, 'Recieved SUCCESSFULLY. ' + str(instance.quantity) + ' ' + str(instance.item_name))

        return redirect('/stock_detail/' + str(instance.id))
    context = {
        'title': 'Recieve ' + str(queryset.item_name),
        'instance': queryset,
        'form': form,
        'username': 'Recieve By: ' + str(request.user),
    }

    return render(request, 'add_items.html', context)

def reorder_level(request, pk):
    queryset = stock.objects.get(id=pk)
    form = ReorderLevelForm(request.POST or None, instance=queryset)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, 'Reorder level for ' + str(instance.item_name) + ' is updated to' + str(instance.reorder_level))
        
        return redirect('/list_items')
    context = {
        'instance': queryset,
        'form': form,
    }
    return render(request, 'add_items.html', context)

def list_history(request):
    header = 'HISTORY DATA'
    queryset = StockHistory.objects.all()
    form = StockHistorySearchForm(request.POST or None)
    context = {
        'header': header,
        'queryset': queryset,
        'form': form,
    }
    
    if request.method == 'POST':
        category = form['category'].value()
        queryset = StockHistory.objects.filter(
    item_name__icontains=form['item_name'].value(), 
    last_updated__range=(form['start_date'].value(), form['end_date'].value())
)

        if (category != ''):
            queryset = queryset.filter(category_id = category)
            if form['export_to_CSV'].value() == True:
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="Stock History.csv"'
                writer = csv.writer(response)
                writer.writerow(['CATEGORY', 'ITEM NAME', 'QUANTITY', 'ISSUE QUANTITY', 'RECIEVE QUANTITY', 'RECIEVE BY', 'ISSUE BY', 'LAST UPDATED'])
                instance = queryset
                for stock in instance:
                    writer.writerow([stock.category, stock.item_name, stock.quantity, stock.issue_quantity, stock.recieved_quantity, stock.receive_by, stock.issue_by, stock.last_updated])
                    return response
            context = {
                'form': form,
                'header': header,
                'queryset': queryset,
            }
    return render(request, 'list_history.html', context)

