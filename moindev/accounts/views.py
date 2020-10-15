from django.shortcuts import render,redirect
from accounts.models import Product,Customer,Order
from accounts.forms import OrderForm,CreateUserForm,CustomerForm
from django.forms import inlineformset_factory
from .filters import OrderFilter
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login , logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user,allowed_users,admin_only
from django.contrib.auth.admin import GroupAdmin as origGroupAdmin
from django.contrib.auth.models import Group, User




# Create your views here.
@unauthenticated_user
def register(request):
    form=CreateUserForm()
    
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user=form.save(commit=True)
            username = form.cleaned_data.get('username')
            group=Group.objects.get(name='customer')
            user.groups.add(group)
            Customer.objects.create(
                user=user,
                name=user.username,
            )
            messages.success(request, "Account created successfully for " + username)
            return redirect("login")
    context= {'form':form}
    return render(request, 'accounts/register.html' , context)

@unauthenticated_user
def loginpage(request):
  
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request , username = username , password = password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username or Password is incorrect')
    context ={}
    return render(request, 'accounts/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')



@login_required(login_url='login')
@admin_only
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()
    total_customers = customers.count()
    total_order = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()
    context = {'orders':orders , 'customers':customers,'total_customers':total_customers,
    'total_order':total_order,'delivered':delivered,'pending':pending }

    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
    orders = request.user.customer.order_set.all()
    total_order = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()
    # print('Orders',orders)
    context= {'orders':orders ,'total_order':total_order,'delivered':delivered,'pending':pending}
    return render(request, 'accounts/user.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
    customer=request.user.customer
    form=CustomerForm(instance=customer)
    if request.method == "POST":
        form=CustomerForm(request.POST,request.FILES,instance=customer)
        if form.is_valid:
            form.save()


    context={'form':form}
    return render(request, 'accounts/account_settings.html',context)



@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()
    return render(request, 'accounts/products.html',{'products':products})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request , pk_test):
    customer =Customer.objects.get(id=pk_test)
    orders = customer.order_set.all()
    total_order = orders.count()
    hisFilter = OrderFilter(request.GET , queryset=orders)
    orders = hisFilter.qs
    context = {'customer':customer,'orders':orders, 'total_order':total_order ,'hisFilter':hisFilter }
    return render(request, 'accounts/customer.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request,pk):
    customer =Customer.objects.get(id=pk)
    orders = customer.order_set.all()

    OrderFormSet = inlineformset_factory(Customer, Order , fields=('product', 'status'))
    customer = Customer.objects.get(id=pk)
    # form = OrderForm(initial={'customer':customer})
    formset=OrderFormSet(instance=customer)
    context ={'formset':formset}
    if request.method == "POST":
        # form=OrderForm(request.POST)
        formset=OrderFormSet(request.POST , instance=customer)

        if formset.is_valid:
            formset.save(commit=True)
            return redirect( '/' )
    return render(request , 'accounts/order_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request , pk):
    order=Order.objects.get(id=pk)
    form= OrderForm(instance=order)
    context ={'form':form}
    if request.method == "POST":
        form=OrderForm(request.POST , instance=order)
        if form.is_valid:
            form.save(commit=True)
            return redirect( '/' )
    return render(request , 'accounts/update_order.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request , pk):
    order=Order.objects.get(id=pk)
    context ={'item':order}
    if request.method == "POST":
        order.delete()
        return redirect( '/' )
    return render(request , 'accounts/delete.html', context)
