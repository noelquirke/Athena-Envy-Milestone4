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

            cronofy = pycronofy.Client(access_token= os.getenv("PYCRONOFY_TOKEN"))
            event = {
            'calendar_id': "cal_XYjaVHVZYgBgrZFs_aHPIMeIFb5S5cDeMuyRG6w",
            'event_uid': refine_what_button[3],
            'summary': "Your Booking with Athena Envy",
            'description': "A Booking has been made, Username:  " + request.user.username  + " email: " + request.user.email,
            'start': refine_what_button[10],
            'end': refine_what_button[12],
            'tzid': 'Europe/Dublin',
            'location': {
                'description': "email:  " + request.user.email + "  Username:  " + request.user.username,
                },
                "attendees": {
                    "invite": [
                      {
                        "email": request.user.email,
                        "display_name": "Your Booking with Athena Envy"
                      }
                    ],
                },
                 "reminders": [
                    { "minutes": 60 },
                    { "minutes": 1440 },
                    { "minutes": 15 }
                  ]

            }
            cronofy.upsert_event(calendar_id='cal_XYjaVHVZYgBgrZFs_aHPIMeIFb5S5cDeMuyRG6w', event=event)
            request.session['cart'] = {}
            return render(request, 'success.html')
        else:
            messages.error(request, "Unable to take payment")
    else:
        print(payment_form.errors)
        messages.error(request, "We were unable to take a payment with that card!")
else:
    print(payment_form.errors)
    messages.error(request, "We were unable to take a payment with that card!") 
else:
        user_details = {'full_name': request.user.first_name + " " + request.user.last_name}
        payment_form = MakePaymentForm()
        order_form = OrderForm(user_details)

    cart = request.session.get('cart', {})
    what_calendar = []
    if '1' in cart:
        what_calendar = ['cal_XYjaVHVZYgBgrZFs_HEpo3dw86uG4SHGyFZb0lA']
    elif '2' in cart:
        what_calendar = ['cal_XYjaVHVZYgBgrZFs_dUC2DLLCz8SKCrL07bzZmg']
    elif '3' in cart:
        what_calendar = ['cal_XYjaVHVZYgBgrZFs_dzk27HOsMzv32vRQOsmyaQ']    
    get_date = datetime.now() + timedelta(days=1)
    start_date = datetime.strftime(get_date, '%Y-%m-%dT%H:%M:%SZ')
    future_date = datetime.now() + timedelta(days=20)
    end_date = datetime.strftime(future_date, '%Y-%m-%dT%H:%M:%SZ')
    cronofy = pycronofy.Client(access_token= os.getenv("PYCRONOFY_TOKEN"))
    events = cronofy.read_events(
    calendar_ids = what_calendar,    
    from_date = start_date,
    to_date = end_date,
    tzid='Europe/Dublin')
    refine_data = (events.json())
    return render(request, "checkout.html", {'order_form': order_form, 'payment_form': payment_form, 'publishable': settings.STRIPE_PUBLISHABLE, 'data': refine_data})
    ###List Current Calendars, needed if adding further products to the range at a later date####
    #cronofy = pycronofy.Client(access_token= os.getenv("PYCRONOFY_TOKEN"))
    #calendars = cronofy.list_calendars()
    #data = (calendars)
    #print(data)
        #return render(request, "checkout.html", {'order_form': order_form, 'payment_form': payment_form, 'publishable': settings.STRIPE_PUBLISHABLE, 'data': refine_data}) 
