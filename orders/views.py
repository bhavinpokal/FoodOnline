import simplejson as json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from accounts.utils import send_notification
from marketplace.models import Cart
from marketplace.context_processors import get_cart_amount
from orders.forms import OrderForm
from orders.models import Order, OrderFood, Payment
from orders.utils import generate_order_number


@login_required(login_url='login')
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')

    subtotal = get_cart_amount(request)['subtotal']
    total_tax = get_cart_amount(request)['tax']
    grand_total = get_cart_amount(request)['grand_total']
    tax_data = get_cart_amount(request)['tax_dict']

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.pin_code = form.cleaned_data['pin_code']
            order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            order.total_tax = total_tax
            order.payment_method = request.POST['payment_method']
            order.save()
            order.order_number = generate_order_number(order.id)
            order.save()
            context = {
                'order': order,
                'cart_items': cart_items,
            }
            return render(request, 'orders/place_order.html', context)
        else:
            print(form.errors)
    return render(request, 'orders/place_order.html')


@login_required(login_url='login')
def payments(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        # Get order and payment data
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('txn_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('txn_status')

        # Save payment data to Payment
        order = Order.objects.get(user=request.user, order_number=order_number)
        payment = Payment(user=request.user, transaction_id=transaction_id,
                          payment_method=payment_method, amount=order.total, status=status)
        payment.save()

        # Update Order model
        order.payment = payment
        order.is_ordered = True
        order.save()

        # Update cart items in OrderFood model
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            order_food = OrderFood()
            order_food.order = order
            order_food.payment = payment
            order_food.user = request.user
            order_food.fooditem = item.fooditem
            order_food.quantity = item.quantity
            order_food.price = item.fooditem.price
            order_food.amount = item.fooditem.price * item.quantity
            order_food.save()

        # Send Order Confirmation Email to customer
        mail_subject = 'Order confirmed'
        mail_template = 'orders/order_confirmation_email.html'
        context = {
            'user': request.user,
            'order': order,
            'to_email': order.email,
        }
        send_notification(mail_subject, mail_template, context)

        # Send Order Details Email to vendor
        mail_subject = 'New Order Details'
        mail_template = 'orders/new_order_details.html'
        to_emails = []
        for i in cart_items:
            if i.fooditem.vendor.user.email not in to_emails:
                to_emails.append(i.fooditem.vendor.user.email)

        context = {
            'order': order,
            'to_email': to_emails,
        }
        send_notification(mail_subject, mail_template, context)

        # # Clear cart
        # cart_items.delete()

        # Return statement to AJAX request
        response = {
            'order_number': order_number,
            'transaction_id': transaction_id,
        }
        return JsonResponse(response)
    return HttpResponse('Response')


def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('txn_id')

    try:
        order = Order.objects.get(
            order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        order_food = OrderFood.objects.filter(order=order)

        subtotal = 0
        for item in order_food:
            subtotal += (item.price * item.quantity)
        tax_data = json.loads(order.tax_data)
        context = {
            'order': order,
            'order_food': order_food,
            'subtotal': subtotal,
            'tax_data': tax_data,
        }
        return render(request, 'orders/order_complete.html', context)
    except:
        return redirect('home')
