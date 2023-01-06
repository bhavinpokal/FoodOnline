from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required

from vendor.models import Vendor
from menu.models import Category, FoodItem
from marketplace.models import Cart
from marketplace.context_processors import get_cart_amount, get_cart_counter


def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vcount = vendors.count()
    context = {
        'vendors': vendors,
        'vcount': vcount,
    }
    return render(request, 'marketplace/listings.html', context)


def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset=FoodItem.objects.filter(is_available=True)
        )
    )
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/vendor_detail.html', context)


def add_to_cart(request, food_id=None):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:    # If food item exist or not
                fooditem = FoodItem.objects.get(id=food_id)
                try:    # Whether item is already in the cart or not
                    checkCart = Cart.objects.get(
                        user=request.user, fooditem=fooditem)
                    checkCart.quantity += 1  # Increase the counter
                    checkCart.save()
                    return JsonResponse({'status': 'Success', 'message': 'Food item added by + 1!!', 'cart_counter': get_cart_counter(request), 'qty': checkCart.quantity, 'cart_amount': get_cart_amount(request)})
                except:
                    checkCart = Cart.objects.create(
                        user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({'status': 'Success', 'message': 'Cart created and Food added!!', 'cart_counter': get_cart_counter(request), 'qty': checkCart.quantity, 'cart_amount': get_cart_amount(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'Food does not exist!!'})
        else:
            return JsonResponse({'status': 'Success', 'message': 'Invalid Request!!'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})


def decrease_cart(request, food_id=None):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:    # If food item exist or not
                fooditem = FoodItem.objects.get(id=food_id)
                try:    # Whether item is already in the cart or not
                    checkCart = Cart.objects.get(
                        user=request.user, fooditem=fooditem)
                    if checkCart.quantity > 1:  # Decrease counter if qty > 1
                        checkCart.quantity -= 1
                        checkCart.save()
                    else:   # Delete cart if qty =< 1
                        checkCart.delete()
                        checkCart.quantity = 0
                    return JsonResponse({'status': 'Success', 'cart_counter': get_cart_counter(request), 'qty': checkCart.quantity, 'cart_amount': get_cart_amount(request)})
                except:
                    return JsonResponse({'status': 'Failed', 'message': 'Item is not available in the cart!!'})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'Food does not exist!!'})
        else:
            return JsonResponse({'status': 'Success', 'message': 'Invalid Request!!'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})


@login_required(login_url='login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context)


def delete_cart(request, cart_id=None):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status': 'Success', 'message': 'Cart item deleted!!', 'cart_counter': get_cart_counter(request), 'cart_amount': get_cart_amount(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'Cart item does not exist!!'})
        else:
            return JsonResponse({'status': 'Success', 'message': 'Invalid Request!!'})
