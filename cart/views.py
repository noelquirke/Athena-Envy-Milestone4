from django.shortcuts import render, redirect, reverse
from django.core.paginator import Paginator

import requests


# Create your views here.
def view_cart(request):
    # A View that renders the cart contents page
    return render(requests, "cart.html")


def add_to_cart(requests, id):
    # Add a quantity of the specified product to the cart
    quantity = 1

    cart = requests.session.get('cart', {})
    cart.clear()  # Only allows 1 item to be booked per checkout
    cart[id] = cart.get(id, quantity)
    requests.session['cart'] = cart
    return render(requests, "cart.html")
