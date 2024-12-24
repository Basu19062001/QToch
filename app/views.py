from django.shortcuts import render, redirect
from django.views import View
from . models import Product, Customer, Cart, Payment, OrderPlaced, Wishlist
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.http import HttpResponseBadRequest, JsonResponse
from django.db.models import Q
import razorpay
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Create your views here.
@login_required
def home(request):
  totalitem = 0
  wishlist = 0
  if request.user.is_authenticated:
    totalitem = len(Cart.objects.filter(user=request.user))
    wishlist = len(Wishlist.objects.filter(user=request.user))
  return render(request, 'app/home.html',locals() )

@login_required
def about(request):
  totalitem = 0
  wishlist = 0
  if request.user.is_authenticated:
    totalitem = len(Cart.objects.filter(user=request.user))
    wishlist = len(Wishlist.objects.filter(user=request.user))
  return render(request, 'app/about.html' ,locals())

@login_required
def contact(request):
  totalitem = 0
  wishlist = 0
  if request.user.is_authenticated:
    totalitem = len(Cart.objects.filter(user=request.user))
    wishlist = len(Wishlist.objects.filter(user=request.user))
  return render(request, 'app/contact.html' ,locals())
class CategoryView(View):
  def get(self, request,val):
    totalitem = 0
    wishlist = 0
    if request.user.is_authenticated:
      totalitem = len(Cart.objects.filter(user=request.user))
      wishlist = len(Wishlist.objects.filter(user=request.user))
    product = Product.objects.filter(category=val)
    title = Product.objects.filter(category=val).values('title')
    return render(request, 'app/category.html',locals() )

@method_decorator(login_required, name='dispatch')
class CategoryTitle(View):
  def get(self, request, val):
    product = Product.objects.filter(title=val)
    title = Product.objects.filter(category=product[0].category).values('title')
    totalitem = 0
    wishlist = 0
    if request.user.is_authenticated: 
      totalitem = len(Cart.objects.filter(user=request.user))
      wishlist = len(Wishlist.objects.filter(user=request.user))
    return render(request, 'app/category.html',locals())

@method_decorator(login_required, name='dispatch')
class ProductDetail(View):
  def get(self, request,pk):
    product = Product.objects.get(pk=pk) 
    wishlist =  Wishlist.objects.filter(Q(product=product) & Q(user=request.user))
    totalitem = 0
    wishlist = 0
    if request.user.is_authenticated:
      totalitem = len(Cart.objects.filter(user=request.user))
      wishlist = len(Wishlist.objects.filter(user=request.user))
    return render(request, 'app/productdetail.html',locals() )

@method_decorator(login_required, name='dispatch')
class CustomerRegistrationView(View):
  def get(self, request):
    form = CustomerRegistrationForm()
    totalitem = 0
    wishlist = 0
    if request.user.is_authenticated:
      totalitem = len(Cart.objects.filter(user=request.user))
      wishlist = len(Wishlist.objects.filter(user=request.user))
    return render(request,'app/customerregistration.html',locals() )
  def post(self, request):
    form = CustomerRegistrationForm(request.POST)
    if form.is_valid():
      form.save()
      messages.success(request, 'Congratulations ! User Registered Successfully')
    else:
      messages.warning(request, 'Invalid Input Data')
    return render(request,'app/customerregistration.html',locals() )
    

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
  def get(self, request):
    form = CustomerProfileForm()
    totalitem = 0
    wishlist = 0
    if request.user.is_authenticated:
      totalitem = len(Cart.objects.filter(user=request.user))
      wishlist = len(Wishlist.objects.filter(user=request.user))
    return render(request, 'app/profile.html',locals())
  def post(self, request):
    form = CustomerProfileForm(request.POST)
    if form.is_valid():
      user = request.user
      name = form.cleaned_data['name']
      locality = form.cleaned_data['locality']
      city = form.cleaned_data['city']
      mobile = form.cleaned_data['mobile']
      zipcode = form.cleaned_data['zipcode']
      state = form.cleaned_data['state']
      
      reg= Customer(user = user, name = name, locality=locality, city =city,  mobile = mobile, zipcode = zipcode, state = state)
      reg.save()
      messages.success(request, 'Congratulations ! Profile Saved Successfully')
    else:
      messages.warning(request, 'Invalid Input Data')
    return render(request, 'app/profile.html',locals())

@login_required
def address(request):
  add = Customer.objects.filter(user=request.user)
  totalitem = 0
  wishlist = 0
  if request.user.is_authenticated:
    totalitem = len(Cart.objects.filter(user=request.user))
    wishlist = len(Wishlist.objects.filter(user=request.user))
  return render(request, 'app/address.html',locals())


@method_decorator(login_required, name='dispatch')
class updateAddress(View):
  def get(self, request,pk):
    add = Customer.objects.get(pk=pk)
    form = CustomerProfileForm(instance=add)
    totalitem = 0
    wishlist = 0
    if request.user.is_authenticated:
      totalitem = len(Cart.objects.filter(user=request.user))
      wishlist = len(Wishlist.objects.filter(user=request.user))
    return render(request, 'app/updateAddress.html',locals())
  def post(self, request,pk):
    form = CustomerProfileForm(request.POST)
    if form.is_valid():
      add = Customer.objects.get(pk=pk)
      add.name = form.cleaned_data['name']
      add.locality = form.cleaned_data['locality']
      add.city = form.cleaned_data['city']
      add.mobile = form.cleaned_data['mobile']
      add.zipcode = form.cleaned_data['zipcode']
      add.state = form.cleaned_data['state']
      add.save()
      messages.success(request, 'Congratulations ! Profile Updated Successfully')
    else:
      messages.warning(request, 'Invalid Input Data')
    return redirect('address')
  
  
@login_required
def add_to_cart(request):
    print(request.GET)
    user = request.user
    product_id = request.GET.get('prod_id')
    try:
        product_id = int(product_id)  # Ensure product_id is an integer
        product = Product.objects.get(id=product_id)
        Cart(user=user, product=product).save()
        return redirect('/cart')
    except ValueError:
        return HttpResponseBadRequest("Invalid product ID.")
    except Product.DoesNotExist:
        return HttpResponseBadRequest("Product not found.")

@login_required
def show_cart(request):
  user = request.user
  cart = Cart.objects.filter(user=user)
  amount = 0
  for p in cart:
    value = p.quantity * p.product.discounted_price
    amount = amount + value
  totalamount = amount + 40
  totalitem = 0
  wishlist = 0
  if request.user.is_authenticated:
    totalitem = len(Cart.objects.filter(user=request.user))
    wishlist = len(Wishlist.objects.filter(user=request.user))
  return render(request, 'app/addToCart.html',locals())

@method_decorator(login_required, name='dispatch')
class Checkout(View):
  def get(self, request):
    totalitem = 0
    wishlist = 0
    if request.user.is_authenticated:
      totalitem = len(Cart.objects.filter(user=request.user))
      wishlist = len(Wishlist.objects.filter(user=request.user))
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items=Cart.objects.filter(user=user)
    amount = 0
    for p in cart_items:
      value = p.quantity * p.product.discounted_price
      amount += value
    totalamount = amount + 40
    razoramount = int(totalamount * 100)
    client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    data = { "amount": razoramount, "currency": "INR", "receipt": "order_rcptid_12"}
    payment_response = client.order.create(data=data)
    print(payment_response)
    
    # {'amount': 105500, 'amount_due': 105500, 'amount_paid': 0, 'attempts': 0, 'created_at': 1734979133, 'currency': 'INR', 'entity': 'order', 'id': 'order_PaifoJMETC47Ov', 'notes': [], 'offer_id': None, 'receipt': 'order_rcptid_12', 'status': 'created'}
    
    order_id = payment_response['id']
    order_status = payment_response['status']
    if order_status == 'created':
      payment = Payment(
        user = user,
        amount = totalamount,
        razorpay_order_id = order_id,
        razorpay_payment_status = order_status
      )
      payment.save()
    
    return render(request, 'app/checkout.html',locals())
  
@login_required
def payment_done(request):
  order_id = request.GET.get('order_id')
  payment_id = request.GET.get('payment_id')
  cust_id = request.GET.get('cust_id')
  user = request.user
  customer = Customer.objects.get(id=cust_id)
  payment = Payment.objects.get(razorpay_order_id=order_id)
  payment.paid = True
  payment.razorpay_payment_id = payment_id
  payment.save()
  cart = Cart.objects.filter(user=user)
  for c in cart:
    OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity, payment=payment).save()
    c.delete()
  return redirect('orders')

@login_required
def orders(request):
  order_placed = OrderPlaced.objects.filter(user=request.user)
  totalitem = 0
  wishlist = 0
  if request.user.is_authenticated:
    totalitem = len(Cart.objects.filter(user=request.user))
    wishlist = len(Wishlist.objects.filter(user=request.user))
  return render(request, 'app/orders.html',locals())
  

def plus_cart(request):
  if request.method == 'GET':
    prod_id = request.GET['prod_id']
    c= Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
    c.quantity+=1
    c.save()
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    for p in cart:
      value = p.quantity * p.product.discounted_price
      amount = amount + value
    totalamount = amount + 40
    data={
      'quantity':c.quantity,
      'amount':amount,
      'totalamount':totalamount,      
    }
    return JsonResponse(data)
  
def minus_cart(request):
  if request.method == 'GET':
    prod_id = request.GET['prod_id']
    c= Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
    c.quantity -= 1
    c.save()
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    for p in cart:
      value = p.quantity * p.product.discounted_price
      amount = amount + value
    totalamount = amount + 40
    data={
      'quantity':c.quantity,
      'amount':amount,
      'totalamount':totalamount,      
    }
    return JsonResponse(data)

def remove_cart(request):
  if request.method == 'GET':
    prod_id = request.GET['prod_id']
    c= Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
    c.delete()
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    for p in cart:
      value = p.quantity * p.product.discounted_price
      amount = amount + value
    totalamount = amount + 40
    data={
      'quantity':c.quantity,
      'amount':amount,
      'totalamount':totalamount,      
    }
    return JsonResponse(data)
  
  
def plus_wishlist(request):
  if request.method == 'GET':
    prod_id = request.GET['prod_id']
    product = Product.objects.get(id=prod_id)
    user = request.user
    Wishlist(user=user, product=product).save()
    data = {
      'message': 'Added to Wishlist Successfully'
    }
    return JsonResponse(data)
  
def minus_wishlist(request):
  if request.method == 'GET':
    prod_id = request.GET['prod_id']
    product = Product.objects.get(id=prod_id)
    user = request.user
    Wishlist.objects.filter(user=user, product=product).delete()
    data = {
      'message': 'Removed from Wishlist Successfully'
    }
    return JsonResponse(data)
  
@login_required
def search(request):
  query = request.GET['search']
  totalitem = 0
  wishlist = 0
  if request.user.is_authenticated:
    totalitem = len(Cart.objects.filter(user=request.user))
    wishlist = len(Wishlist.objects.filter(user=request.user))
  product = Product.objects.filter(Q(title__icontains=query))
  return render(request, 'app/search.html',locals())