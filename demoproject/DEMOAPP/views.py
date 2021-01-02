import logging

from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .models import Invoice, Stock, Product
from .forms import InvoiceForm, StockForm, ProductForm
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError


def mylogin(request):
    if request.method == "GET":
        return render(request, "DEMOAPP/login.html")
    else:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/products')
        else:
            e = 'Wrong username or password'
            return render(request, "DEMOAPP/login.html", context={'error': e})

def logout(request):
    auth.logout(request)
    return redirect('/login')


def register(request):
     if request.method == "POST":
         try:
            first_name =request.POST['first_name']
            last_name = request.POST['last_name']
            username = request.POST['username']
            password = request.POST['password']
            email = request.POST['email']
            user = User.objects.create_user(first_name=first_name,last_name=last_name,username=username,password=password,email=email)
            user.save()
            return redirect('/products')
         except IntegrityError:
             e = 'this data already exists in the database'
             return render(request, "DEMOAPP/register.html", context={'error': e})
     else:
         return render(request, "DEMOAPP/register.html")

@login_required(login_url="/login")
def productUpdate(request, productId):
    product = Product.objects.get(pk=productId)
    if request.method == "GET":
        context = {"units": Product.getUnits(), 'product': product}
        return render(request, "DEMOAPP/ProductUpdate.html", context)
    else:
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('/productlist')


@login_required(login_url="/login")
def productCreate(request):
    if request.method == "GET":
        context = {"units": Product.getUnits()}
        return render(request, "DEMOAPP/Product.html", context)
    else:
        form = ProductForm(request.POST)
        if Product.ProductValidation(request.POST['Name']):
            form.save()
            return redirect('/products')
        else:
            e = 'this product already exists in the database'
            return render(request, "DEMOAPP/Product.html", context={'error': e, "units": Product.getUnits()})


@login_required(login_url="/login")
def Productlist(request):
    if request.method == "POST":
        Product.objects.filter(pk=request.POST["selectedProductId"]).delete()
    context = {'products': Product.productlist()}
    return render(request, "DEMOAPP/ProductList.html", context)


@login_required(login_url="/login")
def invoiceCreate(request):
    if request.method == "GET":
        context = {'products': Product.productlist()}
        return render(request, "DEMOAPP/invoiceCreate.html", context)
    else:
        form = InvoiceForm(request.POST)
        if form.is_valid():
            editedform = form.save(commit=False)
            editedform.user = request.user
            editedform.save()
            return redirect('/invoice')


@login_required(login_url="/login")
def invoiceList(request):
    if request.method == "POST":
        invoice = Invoice.objects.filter(pk=request.POST["selectedInvoiceId"]).first()
        invoice.delete()
        Stock.objects.filter(invoiceid=request.POST["selectedInvoiceId"]).delete()
    context = {'invoices': Invoice.invoicelist()}
    return render(request, "DEMOAPP/invoiceList.html", context)


@login_required(login_url="/login")
def Stockout(request):
    if request.method == "GET":
        context = {'products': Product.productlist()}
        return render(request, "DEMOAPP/stockOut.html", context)
    else:
        form = StockForm(request.POST)
        if form.is_valid():
            try:
                form.save()
            except Exception:
                context = {'products': Product.productlist(), "outOfStock": True}
                return render(request, "DEMOAPP/stockOut.html", context)
            return redirect('/stockout')

def Stockout2(request):
    if request.method == "GET":
        context = {'products': Stock.quickstockout()}
        return render(request, "DEMOAPP/stockout2.html", context)
    else:
        Stock.stockOutByOne(request.POST["productid"])
        return redirect('/stockout2')


@login_required(login_url="/login")
def Stocklist(request):
    if request.method == "GET":
        context = {'stocks': Stock.StocklistNative()}
        return render(request, "DEMOAPP/stocklist.html", context)


@login_required(login_url="/login")
def Notification(request):
    context = {'notify': Product.notificationlist()}
    return render(request, "DEMOAPP/notification.html", context)

@login_required(login_url="/login")
def saleinformation(request):
    context = {'info': Stock.mostsold()}
    return render(request,"DEMOAPP/saleinformation.html",context)