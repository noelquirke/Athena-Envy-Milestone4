from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import MakePaymentForm, OrderForm
from .models import OrderLineItem
from django.conf import settings
from django.utils import timezone
from products.models import Product
from datetime import datetime, timedelta
import stripe, pycronofy, os, json
#import env

stripe.api_key = settings.STRIPE_SECRET


@login_required()  # User Must be logged in to access this page
def checkout(request):
    if request.method == "POST":  # If the user is attempting to make an appointment do the following#
                order_form = OrderForm(request.POST)
                payment_form = MakePaymentForm(request.POST)
                # If the Order Form, Payment Form and Booking Radio Type Button has a value #
                if order_form.is_valid() and payment_form.is_valid() and request.POST.get('what-button') is not None:
                    order = order_form.save(commit=False)
                    order.date = timezone.now()
                    order.save()
                    # Get the details of the product the user is trying to book #
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
                    # Try to charge the users card for the ammount of the product #
                    try:
                        customer = stripe.Charge.create(
                            amount = int(total * 100),
                            currency = "EUR",
                            description = request.user.email,
                            card = payment_form.cleaned_data['stripe_id'],
                        )
                    # If Stripe returns an error give an error message #
                    except stripe.error.CardError:
                        messages.error(request, "Your card was declined!")

                    # If the payment id succesfull do the following #
                    if customer.paid:
                    # Get the value of the button clicked #
                        what_button = request.POST.get('what-button')
                        # Remove the characters and split at each space #
                        b = "{},'"
                        for char in b:
                            what_button = what_button.replace(char, "")
                        refine_what_button = what_button.split(' ')

                        # Access the Cronofy Api and use the details from 'what_button' value to update a booking in the google calendar #
                        cronofy = pycronofy.Client(access_token= os.getenv("PYCRONOFY_TOKEN"))
                        event = {
                        'event_uid': refine_what_button[3],  # The id of the event in google calendar that's to be updated #
                        'summary': "Your Booking with Athena Envy",
                        # Add the users details to the event so we know who has booked what appointment #
                        'description': "A Booking has been made, Username:  " + request.user.username  + " email: " + request.user.email,
                        'start': refine_what_button[10], # Start time of the event #
                        'end': refine_what_button[12], # End time of the event #
                        'tzid': 'Europe/Dublin', # Timezone to use#
                        'location': {
                            'description': "Google Building Gordon House, 4 Barrow St, Dublin, D04 E5W5",  # The address for where the booking is for, !! Address used for development only#
                        },
                        "attendees": {
                            "invite": [
                              {
                                "email": request.user.email, # Sends an invitation to the user by email that they can accept and it will add it to their calender #
                                "display_name": "Your Booking with Athena Envy"
                              }
                            ],
                        },    
                         "reminders": [ # Reminder notifications 15, 60 mins before start time and 1 day before #
                            { "minutes": 60 },
                            { "minutes": 1440 },
                            { "minutes": 15 }
                          ]
                        }
                        event_2 = { # If the booking is for groups then this is used#
                        'event_uid': refine_what_button[3],
                        'summary': "Your Booking with Athena Envy",
                        'description': "A Booking has been made, Username:  " + request.user.username  + " email: " + request.user.email,
                        'start': refine_what_button[22],
                        'end': refine_what_button[24],
                        'tzid': 'Europe/Dublin',
                        'location': {
                            'description': "N Wall Quay, North Dock, Dublin 1", 
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
                        try: # Try Add event and if it's sucesful set the cart to 0 and send the user to the success page #
                            cronofy.upsert_event(calendar_id = refine_what_button[1], event=event)
                            request.session['cart'] = {}
                            return render(request, 'success.html')
                        except: # If the event fails then it must be a group booking #
                            cronofy.upsert_event(calendar_id = refine_what_button[1], event=event_2)
                            request.session['cart'] = {}
                            return render(request, 'success.html')    
                    else:
                        messages.warning(request, "Unable to take payment")
                else: # Give the user feedback if they haven't picked a time/date button #
                    messages.warning(request, "We were unable to take a payment with that card!")
                    messages.warning(request, "Please pick a Date and Time!") 
    else:
        # Generate the page with the forms#
        user_details = {'full_name': request.user.first_name + " " + request.user.last_name}
        payment_form = MakePaymentForm()
        order_form = OrderForm(user_details)
    # Get what product the user picked# 
    cart = request.session.get('cart', {}) 
    what_calendar = []
    # Gets the events from a particular calendar depending on what item is picked by the user #
    if '7' in cart:
        what_calendar = ['cal_XYjaVHVZYgBgrZFs_HEpo3dw86uG4SHGyFZb0lA']
    elif '8' in cart:
        what_calendar = ['cal_XYjaVHVZYgBgrZFs_dUC2DLLCz8SKCrL07bzZmg']
    elif '9' in cart:    
        what_calendar = ['cal_XYjaVHVZYgBgrZFs_dzk27HOsMzv32vRQOsmyaQ']    
    # Get todays date and get the events for the next 20 days #
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