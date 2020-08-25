from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import MakePaymentForm, OrderForm
from .models import OrderLineItem
from django.conf import settings
from django.utils import timezone
from products.models import Product
import stripe, pycronofy, requests, json, env, os
from datetime import datetime, timedelta

# Create your views here.
stripe.api_key = settings.STRIPE_SECRET


@login_required()
def checkout(request):

    # List Current Calendars
    # cronofy = pycronofy.Client(access_token= os.getenv("PYCRONOFY_TOKEN"))
    # calendars = cronofy.list_calendars()
    # data = (calendars)
    # print(data)

    """Read Calendar Events"""
    start_date = datetime.now().strftime('%Y-%m-%d')
    end_date = datetime.now() + timedelta(days=20)
    print(start_date, end_date)
    cronofy = pycronofy.Client(access_token= os.getenv("PYCRONOFY_TOKEN"))
    events = cronofy.read_events(
    from_date = start_date,
    to_date = end_date,
    tzid='Etc/GMT')
    refine_data = (events.json())
    data_define = []
    try:
        a = refine_data['events'][0]['start'][0:10]
        if not a in data_define:
            data_define.append(a)
    except:
        pass
    try:
        b = refine_data['events'][1]['start']
        if not b in data_define:
            data_define.append(b)
    except:
        pass
    try:
        c = refine_data['events'][2]['start']
        if not c in data_define:
            data_define.append(c)
    except:
        pass
    try:
        d = refine_data['events'][3]['start']
        if not d in data_define:
            data_define.append(d)
    except:
        pass
    try:
        e = refine_data['events'][4]['start']
        if not e in data_define:
            data_define.append(e)
    except:
        pass
    try:
        f = refine_data['events'][5]['start']
        if not f in data_define:
            data_define.append(f)
    except:
        pass
    try:
        g = refine_data['events'][6]['start']
        if not g in data_define:
            data_define.append(g)
    except:
        pass

    data = data_define

    """Add Event To Calendar"""
    # cronofy = pycronofy.Client(access_token= os.getenv("PYCRONOFY_TOKEN"))
    # event = {
    # 'calendar_id': "cal_XYjaVHVZYgBgrZFs_aHPIMeIFb5S5cDeMuyRG6w",
    # 'event_uid': "evt_external_5d9363ef57b3c816a653aab5",
    # 'summary': "Hello Universe",
    # 'description': "Testing456",
    # 'start': "2019-10-08T12:00:00Z",
    # 'end': "2019-10-08T12:30:00Z",
    # 'tzid': 'Etc/GMT',
    # 'location': {
    # 'description': "Hello John"
    # }
# }
    # cronofy.upsert_event(calendar_id='cal_XYjaVHVZYgBgrZFs_aHPIMeIFb5S5cDeMuyRG6w', event=event)

    """Delete Calendar Event"""
    # cronofy = pycronofy.Client(access_token= os.getenv("PYCRONOFY_TOKEN"))
    # cronofy.delete_event(calendar_id='cal_XYjaVHVZYgBgrZFs_aHPIMeIFb5S5cDeMuyRG6w', event_id='0x7f8aacc97d68')

    if request.method == "POST":
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
                    order=order,
                    product=product,
                    quantity=quantity
                )
                order_line_item.save()

            try:
                customer = stripe.Charge.create(
                    amount=int(total * 100),
                    currency="EUR",
                    description=request.user.email,
                    card=payment_form.cleaned_data['stripe_id']
                )
            except stripe.error.CardError:
                messages.error(request, "Your card was declined!")

                if customer.paid:
                    messages.error(request, "You have successfully paid")
                    request.session['cart'] = {}
                    return redirect(reverse('products'))
                else:
                    messages.error(request, "Unable to take payment")
            else:
                print(payment_form.errors)
                messages.error(request, "We were unable to take a payment with that card!") 

    return render(request, "checkout.html", {"order_form": order_form, "payment_form": payment_form, "publishable": settings.STRIPE_PUBLISHABLE, "data": data})
