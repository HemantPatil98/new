from django.shortcuts import render
import datetime
from .models import *
from django.http import JsonResponse
import json
from .utils import cookieCart, cartData, guestOrder
from django.contrib.auth.forms import UserCreationForm
# Create your views here.
def store(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {'products':products, 'cartItems': cartItems}
    return render(request,'shop/store.html',context)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    
    context = {'items':items, 'order':order, 'cartItems': cartItems}
    return render(request,'shop/cart.html',context)

def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items':items, 'order':order, 'cartItems': cartItems}
    return render(request,'shop/checkout.html',context)

def updateItem(request):
    data = json.loads(request.body) #converts string into python dictionary
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('productId:', productId)

    # set customer and updateing customers cart
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer,complete=False)
    orderItem, created = OrderItems.objects.get_or_create(order=order, product=product)

    # Item add and remove form cart functionality
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    orderItem.save()
    
    if orderItem.quantity <=0:
        orderItem.delete()
    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer,complete=False)
    
    else:
        customer,order = guestOrder(request,data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer = customer,
            order = order,
            address = data['shipping']['address'],
            city = data['shipping']['city'],
            state = data['shipping']['state'],
            zipcode = data['shipping']['zipcode'],
            
        )
    return JsonResponse('Payment complete', safe=False)

def registerPage(request):
    form = UserCreationForm()
    context = {'form': form}
    return render(request, 'shop/register.html', context)

def loginPage(request):
    context = {}
    return render(request, 'shop/login.html', context)