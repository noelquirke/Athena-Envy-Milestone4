from django.shortcuts import render
from .forms import ContactForm
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.contrib import messages
import env

# Create your views here.


def contact(request):
    if request.method == 'GET':
        form = ContactForm()
        return render(request, 'contact.html', {'form': form})

    else:
        form = ContactForm(request.POST)
        form_name = form.data['name']
        form_message = form.data['message']
        form_email = form.data['email']
        html_content = '<h3>Sent By: ' + form_email + '</h3> <br> <p>' + form_message + ' </p>'

        email = EmailMessage('This is a message from : ' + form_name, html_content ,'declangbyrne1987@gmail.com', ['declangbyrne1987@gmail.com', form_email])
        email.content_subtype = "html"  # Main content is now text/html
        email.send()
        messages.success(request, 'Thank you your email has been sent!')
        return render(request, 'contact.html', {'form': form})
