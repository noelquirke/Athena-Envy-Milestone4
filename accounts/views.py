from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib import messages, auth
from django.urls import reverse
from .forms import UserLoginForm, UserRegistrationForm
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required


# Create your views here.

def logout(request):
    #A view that logs the user out and redirects back to the products page#
    auth.logout(request)
    return redirect(reverse('products'))


def login(request):
    # If the submit button is clicked #
    if request.method == 'POST':
        user_form = UserLoginForm(request.POST)
        if user_form.is_valid():
            user = auth.authenticate(request.POST['username_or_email'],
                                     password=request.POST['password'])
            # if user exists #
            if user:
                auth.login(request, user)

                if request.GET and request.GET['next'] !='':
                    next = request.GET['next']
                    return HttpResponseRedirect(next)
                else:

                    return redirect(reverse('index'))
            # if user doesn't exist or details are incorrect #
            else:
                user_form.add_error(None, "Your username or password are incorrect")
    # return the login page #
    else:
        user_form = UserLoginForm()

    args = {'user_form': user_form, 'next': request.GET.get('next', '')}
    return render(request, 'login.html', args)


def register(request):
    # If the submit button is clicked #
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            user_form.save()

            user = auth.authenticate(request.POST.get('email'),
                                     password=request.POST.get('password1'))

            # If details are correctly added #
            if user:
                auth.login(request, user)
                return redirect(reverse('products'))

            else:
                messages.error(request, "unable to log you in at this time!")
    # render the register page #
    else:
        user_form = UserRegistrationForm()

    args = {'user_form': user_form}
    return render(request, 'register.html', args)
