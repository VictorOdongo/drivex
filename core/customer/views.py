import paypalrestsdk
import requests
# import stripe
# import firebase_admin
# from firebase_admin import credentials, auth, messaging

from io import BytesIO
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa

from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse
from django.contrib import messages

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from core.customer import forms
from core.models import *

from django.http import JsonResponse
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
@login_required(login_url="/sign-in/?next=/customer/")
def payment_method_page(request):
    current_customer = request.user.customer

    has_current_job = Job.objects.filter(
        customer=current_customer,
        status__in=[
            Job.COMPLETED_STATUS,
        ]
    ).exists()

    if has_current_job:
        messages.success(request, "Job completed, pay now") 
        
        # Fetch the completed job related to the current customer
        # current_job = Job.objects.filter(
        #     customer=current_customer,
        #     status=Job.COMPLETED_STATUS
        # ).first()

        # if current_job:
        #     current_courier = current_job.courier

        #     if current_courier and current_courier.paypal_email:
        #         courier_paypal_email = current_courier.paypal_email

        #         # Initialize PayPal SDK
        #         paypalrestsdk.configure({
        #             "mode": settings.PAYPAL_MODE,  
        #             "client_id": settings.PAYPAL_CLIENT_ID,
        #             "client_secret": settings.PAYPAL_SECRET_KEY
        #         })

        #         # Create PayPal payment object
        #         payment = paypalrestsdk.Payment({
        #             "intent": "sale",
        #             "payer": {
        #                 "payment_method": "paypal"
        #             },
        #             "transactions": [{
        #                 "amount": {
        #                     "total": "10.00",  # Set the transaction amount here
        #                     "currency": "USD"  # Set the currency code here
        #                 },
        #                 "payee": {
        #                     "email": courier_paypal_email
        #                 },
        #                 "description": "Payment for job"
        #             }],
        #             "redirect_urls": {
        #                 "return_url": request.build_absolute_uri('/payment/success/'), 
        #                 "cancel_url": request.build_absolute_uri('/payment/cancel/')
        #             }
        #         })

        #         # Perform API call to create PayPal payment
        #         if payment.create():
        #             # Redirect user to PayPal approval URL
        #             redirect_url = next(link.href for link in payment.links if link.method == 'REDIRECT')
        #             return redirect(redirect_url)
        #         else:
        #             messages.error(request, "Failed to create PayPal payment")
        #     else:
        #         messages.error(request, "Courier email not found")
        # else:
        #     messages.error(request, "No completed job found for payment")
    else:
        messages.warning(request, "You have no completed jobs")          
       
    return render(request, 'customer/payment_method.html')


@login_required(login_url="/sign-in/?next=/customer/")
def render_to_pdf(template_src, context_dict={}):
	template = get_template(template_src)
	html  = template.render(context_dict)
	result = BytesIO()
	pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
	if not pdf.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	return None


data = {
	"company": "DriveXpress Delivery LTD",
	"contact": "+2541107800",
	"website": "drivex.com",
	"email": "info@drive.com",
	}

#Automaticly downloads to PDF file
class DownloadPDF(View):
	def get(self, request, *args, **kwargs):
		
		pdf = render_to_pdf('customer/pdf_template.html', data)

		response = HttpResponse(pdf, content_type='application/pdf')
		filename = "Invoice_%s.pdf" %("12341231")
		content = "attachment; filename='%s'" %(filename)
		response['Content-Disposition'] = content
		return response



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
                
                # try:
                #     payment_intent = stripe.PaymentIntent.create(
                #         amount=int(creating_job.price * 0.25),
                #         currency='usd',
                #         customer=current_customer.stripe_customer_id,
                #         payment_method=current_customer.stripe_payment_method_id,
                #         off_session=True,
                #         confirm=True,
                #     )

                #     Transaction.objects.create(
                #         stripe_payment_intent_id=payment_intent['id'],
                #         job=creating_job,
                #         amount=creating_job.price
                #     )

                    # creating_job.status = Job.PROCESSING_STATUS
                    # creating_job.save()

                #     # Send push notifications to all couriers
                #     couriers = Courier.objects.all()
                #     registration_tokens = [
                #         i.fcm_token for i in couriers if i.fcm_token]

                #     message = messaging.MulticastMessage(
                #         notification=messaging.Notification(
                #             title=creating_job.name,
                #             body=creating_job.description
                #         ),
                #         webpush=messaging.WebpushConfig(
                #             notification=messaging.WebpushNotification(
                #                 icon=creating_job.photo.url,
                #             ),
                #             fcm_options=messaging.WebpushFCMOptions(
                #                 link=settings.NGROK_URL +
                #                 reverse('courier:available_jobs')
                #             )
                #         ),
                #         tokens=registration_tokens
                #     )
                #     response = messaging.send_multicast(message)
                #     print('{0} messages were sent successfully'.format(
                #         response.success_count))

                    # return redirect(reverse('customer:home'))

                # except stripe.error.CardError as e:
                    # err = e.error
                    # Error code will be authentication_required if authentication is needed
                    # print("Code is: %s" % err.code)
                    # payment_intent_id = err.payment_intent['id']
                    # payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

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
