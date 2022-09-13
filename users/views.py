from time import strftime, gmtime

from django.utils import timezone
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from termcolor import colored

from users.forms import RegisterForm, LoginForm, AddUserForm, UpdateProfileForm, UpdateUserForm
from users.models import TimeSheet, User

from common.authorization import group_required, lv

@login_required
def home(request):
    return render(request, 'users/home.html')

class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'users/register.html'

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='/')

        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')

            return redirect(to='/')

        return render(request, self.template_name, {'form': form})


class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)

            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True

        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(CustomLoginView, self).form_valid(form)


@group_required('Sub Admin', 'HR', raise_exception=True)
def user_list(request):
    users = User.objects.all()
    context = {
        'users': users
    }
    return render(request, 'users/users-list.html', context)


@group_required('Sub Admin', 'HR', raise_exception=True)
def add_user(request):
    form = AddUserForm(request.POST or None)
    users = User.objects.all()
    context = {
        'form': form,
    }
    if request.method == 'POST':
        if form.is_valid():
            recent_group = request.user.groups.first().name
            request_group = form.cleaned_data.get('groups')
            print(colored(request_group, 'blue'))
            if lv(recent_group) >= lv(request_group):
                messages.warning(request, "You do not have permission add user at position:" + recent_group)
                context = {
                    'form': form,
                }
                return render(request, 'users/users-add.html', context)

            user = form.save()
            group = Group.objects.get(name=request_group)
            user.groups.add(group)
            messages.success(request, "Succesful")
            return redirect('/users')
        else:
            print(colored('form is not valid', 'red'))
    
    return render(request, 'users/users-add.html', context)


@group_required('Sub Admin', raise_exception=True)
def delete_user(request, pk):
    users = User.objects.all()
    try:
        user = User.objects.get(id=pk)
    except:
        messages.warning(request, "User not exist")
        context = {
            'users': users,
        }
        return render(request, 'users/users-list.html', context)
    User.objects.filter(id=pk).delete()
    messages.success(request, "Delete successfully")
    return redirect('/users')


@login_required
def profile(request, pk):
    target_user = User.objects.get(id=pk)
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=target_user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=target_user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(f"/users/edit/{pk}")
    else:
        user_form = UpdateUserForm(instance=target_user)
        profile_form = UpdateProfileForm(instance=target_user.profile)

    return render(request, 'users/profile.html', {'target_user': target_user, 'user_form': user_form, 'profile_form': profile_form})


def timesheet(request):
    return render(request, 'users/timesheet.html')

def checkin(request):
    TimeSheet.objects.create()
    a = TimeSheet.objects.first()
    a.checkin = timezone.now()
    return redirect('/timesheet')

def checkout(request):
    a = TimeSheet.objects.first()
    a.checkout = timezone.now()
    a.time = (a.checkout - a.checkin).seconds
    a.save()
    # print( strftime("%H:%M:%S", gmtime(a.time)) )
    return redirect('/timesheet')




