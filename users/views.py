from time import strftime, gmtime
import datetime
from calendar import monthrange


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
from users.models import Salary, TimeSheet, User

from common.authorization import group_required, lv
from common.utils import get_time_now

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

@login_required
def timesheet(request):
    year, month, tmp = get_time_now()

    all_days = monthrange(year, month)
    t = []

    for day in range(1, all_days[1]+1):
        try:
            list = TimeSheet.objects.get(user=request.user, day=day)
            checkout = list.checkout.time if (list.checkout is not None) else ''
            late = '' if (list.late == 0) else strftime("%H:%M", gmtime(list.late))
            ot = '' if (list.ot == 0) else strftime("%H:%M", gmtime(list.ot))
            
            t.append({
                'day' : day, 
                'month': month, 
                'year': year, 
                'checkin': list.checkin.time,
                'checkout': checkout, 
                'late': late, 
                'ot': ot, 
                'time': strftime("%H:%M", gmtime(list.time)),
            })
        except:
            t.append({'day' : day, 'month': month, 'year': year, })

    try:
        salary = Salary.objects.get(user=request.user, month=month)
    except:
        salary = ''

    context = {
        't': t,
        'salary': salary,
    }
    return render(request, 'users/timesheet.html', context)

@login_required
def checkin(request):
    year, month, day = get_time_now()
    TimeSheet.objects.get_or_create(user=request.user, year=year, month=month, day=day)
    return redirect('/timesheet')

@login_required
def checkout(request):
    year, month, day = get_time_now()
    try:
        timesheet = TimeSheet.objects.get(user=request.user, year=year, month=month, day=day)
    except:
        messages.warning(request, 'checkin before')
        return redirect('/timesheet')
    timesheet.checkout = timezone.now()

    # timesheet.checkin = datetime.datetime(2022,9,14,7,58,20,123456)
    # timesheet.checkout = datetime.datetime(2022,9,14,18,14,25,123456)

    checkin = timesheet.checkin
    checkout = timesheet.checkout

    if (checkin - datetime.datetime(year,month,day,8,0,0,0)).days > 0 :
        timesheet.late = (checkin - datetime.datetime(year,month,day,8,0,0,0)).seconds

    if (datetime.datetime(year,month,day,17,0,0,0) - checkout).days < 0:
        timesheet.ot = (checkout - datetime.datetime(year,month,day,17,0,0,0)).seconds

    a = range(1, monthrange(year, month)[1]+1) 
    if (day == a[-1]):
        try:
            salary = Salary.objects.get(user=request.user)
        except:
            Salary.objects.filter(user=request.user).delete()
            Salary.objects.create(user=request.user)
    
    timesheet.time = (checkout - checkin).seconds
    timesheet.save()
    # print( strftime("%H:%M:%S", gmtime(timesheet.time)) )
    return redirect('/timesheet')

def export_salary(request, pk):
    user = User.objects.get(id=pk)
    salary = Salary.objects.create(user=user)
    print(salary)
    return redirect('/timesheet')

def manage_timesheet(request):
    year, month, tmp = get_time_now()

    a = monthrange(year, month)

    users = User.objects.all()

    all_timeline = []

    for user in users:
        timeline = []
        for day in range(1, a[1]+1):
            try:
                timesheet = TimeSheet.objects.get(user=user, day=day, month=month)
                w_time = strftime("%H:%M", gmtime(timesheet.time))
            except:
                w_time = ''
            timeline.append(
                {
                    'day': day,
                    'w_time': w_time
                }
            )
        all_timeline.append(
            {
                'user': user,
                'timeline': timeline,
            }
        )

    tl = []
    for day in range(1, a[1]+1):
        tl.append({'day': day,})

    context = {
        'timeline': tl,
        'all_timeline': all_timeline,
        'users': User.objects.all()
    }

    return render (request, 'users/manage-timesheet.html', context)


# importing the necessary libraries
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa  

# defining the function to convert an HTML file to a PDF file
def html_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    # print(html)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

# importing the necessary libraries
from django.http import HttpResponse
from django.views.generic import View
from users import models
from django.template.loader import render_to_string

#Creating a class based view
# class GeneratePdf(View):
#      def get(self, request, *args, **kwargs):
#         data = models.User.objects.all()
#         open('users/templates/temp.html', "w").write(render_to_string('result.html', {'data': data}))

#         # Converting the HTML template into a PDF file
#         pdf = html_to_pdf('temp.html')
         
#          # rendering the template
#         return HttpResponse(pdf, content_type='application/pdf')


class GeneratePdf(View):
    def get(self, request, *args, **kwargs):

        datee =datetime.datetime.strptime(str(timezone.now()), "%Y-%m-%d %H:%M:%S.%f")
        year = datee.year
        month = datee.month
        # day = datee.day

        a = monthrange(year, month)

        users = User.objects.all()

        all_timeline = []

        for user in users:
            timeline = []
            for day in range(1, a[1]+1):
                try:
                    timesheet = TimeSheet.objects.get(user=user, day=day, month=month)
                    x = strftime("%H", gmtime(timesheet.time))
                    y = strftime("%M", gmtime(timesheet.time))
                    w_time = int(x) + round(int(y)/60, 1)
                    # w_time = y
                except:
                    w_time = ''
                timeline.append(
                    {
                        'day': day,
                        'w_time': w_time
                    }
                )
            all_timeline.append(
                {
                    'user': user,
                    'timeline': timeline,
                }
            )

        tl = []
        for day in range(1, a[1]+1):
            tl.append(
                {
                    'day': day,
                }
            )

        data = {
            'timeline': tl,
            'all_timeline': all_timeline,
            'users': User.objects.all()
        }
        # data = models.User.objects.all()
        open('templates/temp.html', "w").write(render_to_string('pdf/report-timesheet.html', {'data': data}))

        # Converting the HTML template into a PDF file
        pdf = html_to_pdf('temp.html')
         
         # rendering the template
        return HttpResponse(pdf, content_type='application/pdf')




