from django import forms
from .models import Order

# Choices available to the user in the dropdown menus in the checkout page


class MakePaymentForm(forms.Form):

    MONTH_CHOICES = [(i, i) for i in range(1, 12)]
    YEAR_CHOICES = [(i, i) for i in range(2019, 2036)]

# Fieldset for credit card details in the checkout page for stripe
    credit_card_number = forms.CharField(label='Credit card number', required=False)
    cvv = forms.CharField(label='Security code (CVV)', required=False)
    expiry_month = forms.ChoiceField(label='Month', choices=MONTH_CHOICES, required=False)
    expiry_year = forms.ChoiceField(label='Year', choices=YEAR_CHOICES, required=False)
    stripe_id = forms.CharField(widget=forms.HiddenInput)  # Hidden field for the stripe token


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = (
            'full_name', 'street_address1', 'street_address2', 'town_or_city', 'postcode', 'county', 'phone_number',

        )
