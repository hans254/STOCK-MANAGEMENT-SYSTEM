from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.http import HttpResponse
import csv
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

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
@login_required
def list_items(request):
    header = 'List of Items'
    form = ItemFilterForm(request.POST or None)
    
    # Start with an empty queryset
    queryset = stock.objects.all().order_by('id')

    # If the form is valid and the user has provided input, filter the queryset
    if request.method == 'POST' and form.is_valid():
        category_name = form.cleaned_data.get('category')
        item_name = form.cleaned_data.get('item_name')

        # Apply filtering based on form input (category and item name)
        if category_name:
            queryset = queryset.filter(category__name__icontains=category_name)
        if item_name:
            queryset = queryset.filter(item_name__icontains=item_name)

        # CSV Export Logic
        if form.cleaned_data.get('export_to_CSV', False):
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="List_of_Stock.csv"'
            writer = csv.writer(response)
            writer.writerow(['CATEGORY', 'ITEM_NAME', 'QUANTITY'])
            
            for item in queryset:
                writer.writerow([item.category.name, item.item_name, item.quantity])
            return response

    # Handle pagination
    paginator = Paginator(queryset, 8)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)

    context = {
        'form': form,
        'queryset': queryset,
        'header': header,
    }

    return render(request, 'web/list_items.html', context)


@login_required
def add_items(request):
    form = StockCreateForm(request.POST or None)
    if request.method == 'POST':
        form = StockCreateForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully Saved')
            return redirect(list_items)
    context = {
        'form': form,
        'title': 'Add Item'
    }
    return render(request, "web/add_items.html", context)

@login_required
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
    return render(request, 'web/add_items.html', context)

@login_required
def delete_items(request, pk):
    queryset = stock.objects.get(id=pk)
    if request.method == 'POST':
        queryset.delete()
        messages.success(request, 'Deleted Successfully')
        return redirect('/list_items')
    return render(request, 'web/delete_items.html')

'''@login_required
def confirm_logout(request):
    #queryset = stock.objects.get(id=pk)
    if request.method == 'POST':
        #queryset.delete()
        messages.success(request, 'Logout Successfull')
        return redirect('/login')
    return render(request, 'web/confirm_logout.html')
'''
@login_required
def stock_detail(request, pk):
    queryset = stock.objects.get(id=pk)
    context = {
        'queryset': queryset,
    }
    return render(request, 'web/stock_detail.html', context)

@login_required
def issue_items(request, pk):
    queryset = stock.objects.get(id=pk)
    form = IssueForm(request.POST or None, instance = queryset)
    if form.is_valid():
        instance = form.save(commit=False)
        #instance.received_quantity = 0
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
    return render(request, 'web/add_items.html', context)

@login_required
def receive_items(request, pk):
    queryset =stock.objects.get(id=pk)
    form = RecieveForm(request.POST or None, instance = queryset)
    if form.is_valid():
        instance = form.save(commit=False)
        #instance.issue_quantity = 0
        instance.quantity += instance.received_quantity
        instance.recieve_by = str(request.user)
        instance.save()
        receive_history = StockHistory(
            id = instance.id,
            last_updated = instance.last_updated,
            category_id = instance.category_id,
            item_name = instance.item_name,
            quantity = instance.quantity,
            received_quantity = instance.received_quantity,
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

    return render(request, 'web/add_items.html', context)

@login_required
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
    return render(request, 'web/add_items.html', context)

@login_required
def list_history(request):
    header = 'HISTORY DATA'
    queryset = StockHistory.objects.all()
    form = StockHistorySearchForm(request.POST or None)
    paginator = Paginator(queryset, 4)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
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
                    writer.writerow([stock.category, stock.item_name, stock.quantity, stock.issue_quantity, stock.received_quantity, stock.receive_by, stock.issue_by, stock.last_updated])
                    return response
            context = {
                'form': form,
                'header': header,
                'queryset': queryset,
            }
    return render(request, 'web/list_history.html', context)
