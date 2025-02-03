from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.http import HttpResponse
import csv
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    title = 'Welcome: This is the Home Page'
    context = {
        'title': title,
    }
    return redirect('/list_items.html')
    #return render(request, "home.html", context)


def list_items(request):
    header = 'List of Items'
    queryset = stock.objects.all().order_by('id')  # Fetch all items
    form = StockSearchForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        category = form.cleaned_data.get('category')
        item_name = form.cleaned_data.get('item_name')

        if category:
            queryset = queryset.filter(category=category) 

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

    # Pagination
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
    header = 'Add Item'
    form = StockCreateForm(request.POST or None)
    if request.method == 'POST':
        form = StockCreateForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully Saved')
            return redirect(list_items)
    context = {
        'form': form,
        'header': header,
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

def list_history(request):
    header = 'HISTORY DATA'
    queryset = StockHistory.objects.all()
    form = StockHistorySearchForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        category = form.cleaned_data.get('category')
        item_name = form.cleaned_data.get('item_name')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        # Apply the filters
        if category:
            queryset = queryset.filter(category_id=category)
        if item_name:
            queryset = queryset.filter(item_name__icontains=item_name)
        if start_date and end_date:
            queryset = queryset.filter(last_updated__range=(start_date, end_date))

        # Handle CSV export
        if form.cleaned_data.get('export_to_CSV', False):
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="Stock_History.csv"'
            writer = csv.writer(response)
            writer.writerow([
                'CATEGORY', 'ITEM NAME', 'QUANTITY', 'ISSUE QUANTITY',
                'RECEIVE QUANTITY', 'RECEIVE BY', 'ISSUE BY', 'LAST UPDATED'
            ])

            for stock in queryset:
                writer.writerow([
                    stock.category, stock.item_name, stock.quantity,
                    stock.issue_quantity, stock.received_quantity,
                    stock.receive_by, stock.issue_by, stock.last_updated
                ])
            
            return response  # Return CSV file after writing all rows

    # Pagination after filtering
    paginator = Paginator(queryset, 4)  # Number of items per page
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)

    context = {
        'header': header,
        'queryset': queryset,
        'form': form,
    }

    return render(request, 'web/list_history.html', context)
