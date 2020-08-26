from django.shortcuts import render
from .forms import ContactForm
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.contrib import messages
# import env

# Renders the Contact us page with the form #
def contact(request):
    if request.method == 'GET':
        form = ContactForm()
        return render(request, 'contact.html', {'form': form})

# If a message is sent it is sent to my email and a copy is sent to the user.  #
    else:
        form = ContactForm(request.POST)
        form_name = form.data['name']
        form_message = form.data['message']
        form_email = form.data['email']
        html_content = '<h3>Sent By: ' + form_email + '</h3> <br> <p>' + form_message + '</p>'

        email = EmailMessage('This is a message from : ' + form_name, html_content, 'noelquirke90@gmail.com', ['noelquirke90@gmail.com', form_email])
        email.content_subtype = "html"  # Main content is now text/html
        email.send()
        messages.success(request, 'Thank you your email has been sent!')
        return render(request, 'contact.html', {'form': form})
