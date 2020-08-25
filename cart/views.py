from django.shortcuts import render, redirect, reverse

# Create your views here.


def view_cart(request):
    """A View that renders the cart contents page"""
    return render(request, "checkout.html")


def add_to_cart(request, id):
    """Add a quantity of the specified product to the cart"""
    quantity = 1

    cart = request.session.get('cart', {})
    cart[id] = cart.get(id, quantity)

    request.session['cart'] = cart
    return redirect(reverse('view_cart'))
