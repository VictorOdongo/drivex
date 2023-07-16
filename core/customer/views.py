import paypalrestsdk
import requests
# import stripe
# import firebase_admin
# from firebase_admin import credentials, auth, messaging

from django.views import View
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse
from django.contrib import messages
from drivex.utils import render_to_pdf
from django.db.models import Sum
from core.models import Job
import uuid

from django_daraja.mpesa.core import MpesaClient
from django.views.decorators.csrf import csrf_exempt


from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from core.customer import forms
from core.models import *

# from intasend import APIService
# import os

# cred = credentials.Certificate(settings.FIREBASE_ADMIN_CREDENTIAL)
# firebase_admin.initialize_app(cred)

# stripe.api_key = settings.STRIPE_API_SECRET_KEY


@login_required()
def home(request):
    return redirect(reverse('customer:profile'))


@login_required(login_url="/sign-in/?next=/customer/")
def profile_page(request):
    user_form = forms.BasicUserForm(instance=request.user)
    customer_form = forms.BasicCustomerForm(instance=request.user.customer)
    password_form = PasswordChangeForm(request.user)

    if request.method == "POST":

        if request.POST.get('action') == 'update_profile':
            user_form = forms.BasicUserForm(
                request.POST, instance=request.user)
            customer_form = forms.BasicCustomerForm(
                request.POST, request.FILES, instance=request.user.customer)

            if user_form.is_valid() and customer_form.is_valid():
                user_form.save()
                customer_form.save()

                messages.success(request, 'Your profile has been updated')
                return redirect(reverse('customer:profile'))

        elif request.POST.get('action') == 'update_password':
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)

                messages.success(request, 'Your password has been updated')
                return redirect(reverse('customer:profile'))

    return render(request, 'customer/profile.html', {
        "user_form": user_form,
        "customer_form": customer_form,
        "password_form": password_form
    })

# Payment processing
@csrf_exempt
def payment_method(request):
    # current_customer = request.user.customer

    # has_current_job = Job.objects.filter(
    #     customer=current_customer,
    #     status__in=[
    #         Job.COMPLETED_STATUS,
    #     ]
    # ).exists()
    
    # if has_current_job:
    #     messages.success(request, "Job completed, pay now") 
    # else:
    #     messages.warning(request, "You have no completed jobs")   
        
    cl = MpesaClient()
    reference = "DriveXpress"
    amount = 1
    phone_number = "254797563890"
    transaction_description = "Description"
    callback_url = 'https://96be-105-161-30-98.ngrok-free.app/customer/payment_method/'
    response = cl.stk_push(phone_number, amount,reference, transaction_description, callback_url)

    if request.method == 'POST':
        result = cl.parse_stk_result(request.body)
        if result["ResultCode"] == 0:
            amount = result["Amount"]
            receipt_number = result["MpesaReceiptNumber"]
            transaction_date = result["TransactionDate"]
            phone_number = result["PhoneNumber"]

    return HttpResponse(response)
         
               


# make payment request   
@login_required(login_url="/sign-in/?next=/customer/") 
def payment(request):
    return render(request, 'customer/payment.html')




#Automaticly downloads to PDF file
class DownloadPDF(View):
	def get(self, request, *args, **kwargs):
            # jobs = Job.objects.all()
            
            # Get the current customer
            customer = request.user.customer
            
             # Access the associated user model
            user = customer.user
            
            # Capture the current customer's full name from the associated user model
            full_name = user.get_full_name()  # Retrieve the customer's full name
            
            # Filter the jobs for the current customer with status "completed"
            jobs = Job.objects.filter(customer=customer, status='completed')
            
            # Calculate the total job price using the Sum aggregation function
            total_price = jobs.aggregate(total_price=Sum('price'))['total_price']
            
            # Generate a unique invoice number using UUID
            invoice_number = str(uuid.uuid4())[:8]  # Generate a random UUID and truncate to 8 characters    
                             
            data = {
                "company": "DriveXpress",
                "contact": "+2541107800",
                "website": "www.drivex.com",
                "email": "info@drive.com",
                "jobs": jobs,
                "job_price": total_price,  # Add the total job price to the data dictionary
                "customer_name": full_name,  # Add the customer's full name to the data dictionary
                "invoice_number": invoice_number,  # Add the invoice number to the data dictionary

            }
            
            pdf = render_to_pdf('customer/pdf_template.html', data)
            
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                filename = "JobSummary_%s.pdf" %("12341231")
                content = "attachment; filename='%s'" %(filename)
                download = request.GET.get("download")
                if download:
                    content = "attachment; filename='%s'" %(filename)
                response['Content-Disposition'] = content
                return response
            return HttpResponse("Not found")



# Job creation
@login_required(login_url="/sign-in/?next=/customer/")
def create_job_page(request):
    current_customer = request.user.customer

    # if not current_customer.stripe_payment_method_id:
    #     return redirect(reverse('customer:payment_method'))

    has_current_job = Job.objects.filter(
        customer=current_customer,
        status__in=[
            Job.PROCESSING_STATUS,
            Job.PICKING_STATUS,
            Job.DELIVERING_STATUS
        ]
    ).exists()

    if has_current_job:
        messages.warning(request, "You are currently processing a job")
        return redirect(reverse('customer:current_jobs'))

    creating_job = Job.objects.filter(customer=current_customer, status=Job.CREATING_STATUS).last()
    step1_form = forms.JobCreateStep1Form(instance=creating_job)
    step2_form = forms.JobCreateStep2Form(instance=creating_job)
    step3_form = forms.JobCreateStep3Form(instance=creating_job)

    if request.method == "POST":
        if request.POST.get('step') == '1':
            step1_form = forms.JobCreateStep1Form(request.POST, request.FILES, instance=creating_job)
            if step1_form.is_valid():
                creating_job = step1_form.save(commit=False)
                creating_job.customer = current_customer
                creating_job.save()
                return redirect(reverse('customer:create_job'))

        elif request.POST.get('step') == '2':
            step2_form = forms.JobCreateStep2Form(request.POST, instance=creating_job)
            if step2_form.is_valid():
                creating_job = step2_form.save()
                return redirect(reverse('customer:create_job'))

        elif request.POST.get('step') == '3':
            step3_form = forms.JobCreateStep3Form(request.POST, instance=creating_job)

            if step3_form.is_valid():
                creating_job = step3_form.save()

                try:
                    r = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json?origins={}&destinations={}&mode=driving&key={}".format(
                        creating_job.pickup_address,
                        creating_job.delivery_address,
                        settings.GOOGLE_API_KEY
                    ))
                    print(r.json()['rows'])

                    distance = r.json()['rows'][0]['elements'][0]['distance']['value']
                    duration = r.json()['rows'][0]['elements'][0]['duration']['value']
                    creating_job.distance = round(distance / 1000, 2)
                    creating_job.duration = int(duration / 60)
                    creating_job.price = round(creating_job.distance * 0.25, 2)  # $ 0.25 per Km
                    creating_job.save()

                except Exception as e:
                    print(e)
                    messages.error(request, "Unfortunately, we do not support deliveries at this distance.")

                return redirect(reverse('customer:create_job'))

        elif request.POST.get('step') == '4':
            if creating_job.price:
                
                creating_job.status = Job.PROCESSING_STATUS
                creating_job.save()
                
            return redirect(reverse('customer:current_jobs'))
    # Determine the current step
    if not creating_job:
        current_step = 1
    elif creating_job.delivery_name:
        current_step = 4
    elif creating_job.pickup_name:
        current_step = 3
    else:
        current_step = 2

    return render(request, 'customer/create_job.html', {
        "GOOGLE_API_KEY": settings.GOOGLE_API_KEY,
        "job": creating_job,
        "step": current_step,
        "step1_form": step1_form,
        "step2_form": step2_form,
        "step3_form": step3_form,
    })


@login_required(login_url="/sign-in/?next=/customer/")
def current_jobs_page(request):
    jobs = Job.objects.filter(
        customer=request.user.customer,
        status__in=[
            Job.PROCESSING_STATUS,
            Job.PICKING_STATUS,
            Job.DELIVERING_STATUS
        ]
    )

    return render(request, 'customer/jobs.html', {
        "jobs": jobs
    })


@login_required(login_url="/sign-in/?next=/customer/")
def archived_jobs_page(request):
    jobs = Job.objects.filter(
        customer=request.user.customer,
        status__in=[
            Job.COMPLETED_STATUS,
            Job.CANCELLED_STATUS,
        ]
    )

    return render(request, 'customer/jobs.html', {
        "jobs": jobs
    })


@login_required(login_url="/sign-in/?next=/customer/")
def job_page(request, job_id):
    job = Job.objects.get(id=job_id)

    if request.method == "POST" and job.status == Job.PROCESSING_STATUS:
        job.status = Job.CANCELLED_STATUS
        job.save()
        return redirect(reverse('customer:archived_jobs'))

    return render(request, 'customer/job.html', {
        "GOOGLE_API_KEY": settings.GOOGLE_API_KEY,
        "job": job
    })
