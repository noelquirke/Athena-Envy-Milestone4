from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import MakePaymentForm, OrderForm
from .models import OrderLineItem
from django.conf import settings
from django.utils import timezone
from products.models import Product
from datetime import datetime, timedelta
import stripe, pycronofy, os, env, json

# Create your views here.
stripe.api_key = settings.STRIPE_SECRET


@login_required()
def checkout(request):

 if request.method=="POST":
    order_form = OrderForm(request.POST)
    payment_form = MakePaymentForm(request.POST)

    if order_form.is_valid() and payment_form.is_valid():
        order = order_form.save(commit=False)
        order.date = timezone.now()
        order.save()

        cart = request.session.get('cart', {})
        total = 0
        for id, quantity in cart.items():
            product = get_object_or_404(Product, pk=id)
            total += quantity * product.price
            order_line_item = OrderLineItem(
                order = order,
                product = product,
                quantity = quantity
                )
            order_line_item.save()

        try:
            customer = stripe.Charge.create(
                amount = int(total * 100),
                currency = "EUR",
                description = request.user.email,
                card = payment_form.cleaned_data['stripe_id'],
            )
            except stripe.error.CardError:
                messages.error(request, "Your card was declined!")

        if customer.paid:
            what_button = request.POST.get('what-button')
            b = "{},'"
            for char in b:
                what_button = what_button.replace(char,"")
            refine_what_button = what_button.split(' ')
            print(refine_what_button[3])

            cronofy = pycronofy.Client(access_token= os.getenv("PYCRONOFY_TOKEN"))
            event = {
            'calendar_id': "cal_XYjaVHVZYgBgrZFs_aHPIMeIFb5S5cDeMuyRG6w",
            'event_uid': refine_what_button[3],
            'summary': "Yes",
            'description': "Bingo",
            'start': refine_what_button[9],
            'end': refine_what_button[11],
            'tzid': 'Europe/Dublin',
            'location': {
                'description': "email:  " + request.user.email + "  Username:  " + request.user.username 
            }
            }
            cronofy.upsert_event(calendar_id='cal_XYjaVHVZYgBgrZFs_aHPIMeIFb5S5cDeMuyRG6w', event=event)
            request.session['cart'] = {}
            messages.success(request, 'Thank you for your book!')
            return render(request, 'success.html')
        else:
            messages.error(request, "Unable to take payment")
    else:
        print(payment_form.errors)
        messages.error(request, "We were unable to take a payment with that card!")
else:
    print(payment_form.errors)
    messages.error(request, "We were unable to take a payment with that card!") 

get_date = datetime.now() + timedelta(days=1)
start_date = datetime.strftime(get_date, '%Y-%m-%dT%H:%M:%SZ')
future_date = datetime.now() + timedelta(days=14)
end_date = datetime.strftime(future_date, '%Y-%m-%dT%H:%M:%SZ')
print(start_date, end_date)
cronofy = pycronofy.Client(access_token= os.getenv("PYCRONOFY_TOKEN"))
events = cronofy.read_events(
from_date = start_date,
to_date = end_date,
tzid='Europe/Dublin')
refine_data = (events.json())
data = refine_data
return render(request, "checkout.html", {'order_form': order_form, 'payment_form': payment_form, 'publishable': settings.STRIPE_PUBLISHABLE, 'data': data})   
