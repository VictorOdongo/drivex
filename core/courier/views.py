from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages

from core.courier import forms
from core.models import *

from django.http import HttpResponse
from drivex.utils import render_to_pdf
from django.db.models import Sum
from core.models import Job
from django.views.generic import View


@login_required(login_url="/sign-in/?next=/courier/")
def home(request):
    return redirect(reverse('courier:available_jobs'))


@login_required(login_url="/sign-in/?next=/courier/")
def available_jobs_page(request):
    return render(request, 'courier/available_jobs.html', {
        "GOOGLE_API_KEY": settings.GOOGLE_API_KEY
    })


@login_required(login_url="/sign-in/?next=/courier/")
def available_job_page(request, id):
    job = Job.objects.filter(id=id, status=Job.PROCESSING_STATUS).last()

    if not job:
        return redirect(reverse('courier:available_jobs'))

    if request.method == 'POST':
        job.courier = request.user.courier
        job.status = Job.PICKING_STATUS
        job.save()

        return redirect(reverse('courier:current_job'))

    return render(request, 'courier/available_job.html', {
        "job": job
    })


@login_required(login_url="/sign-in/?next=/courier/")
def current_job_page(request):
    job = Job.objects.filter(
        courier=request.user.courier,
        status__in=[
            Job.PICKING_STATUS,
            Job.DELIVERING_STATUS
        ]
    ).last()

    return render(request, 'courier/current_job.html', {
        "job": job,
        "GOOGLE_API_KEY": settings.GOOGLE_API_KEY
    })


@login_required(login_url="/sign-in/?next=/courier/")
def current_job_take_photo_page(request, id):
    job = Job.objects.filter(
        id=id,
        courier=request.user.courier,
        status__in=[
            Job.PICKING_STATUS,
            Job.DELIVERING_STATUS
        ]
    ).last()

    if not job:
        return redirect(reverse('courier:current_job'))

    return render(request, 'courier/current_job_take_photo.html', {
        "job": job
    })


@login_required(login_url="/sign-in/?next=/courier/")
def job_complete_page(request):
    return render(request, 'courier/job_complete.html')


@login_required(login_url="/sign-in/?next=/courier/")
def archived_jobs_page(request):
    jobs = Job.objects.filter(
        courier=request.user.courier,
        status=Job.COMPLETED_STATUS
    )

    return render(request, 'courier/archived_jobs.html', {
        "jobs": jobs
    })


@login_required(login_url="/sign-in/?next=/courier/")
def profile_page(request):
    jobs = Job.objects.filter(
        courier=request.user.courier,
        status=Job.COMPLETED_STATUS
    )

    total_earnings = round(sum(job.price for job in jobs) * 0.8, 2)
    total_jobs = len(jobs)
    total_km = sum(job.distance for job in jobs)

    return render(request, 'courier/profile.html', {
        "total_earnings": total_earnings,
        "total_jobs": total_jobs,
        "total_km": total_km
    })

class DownloadPDF2(View):
	def get(self, request, *args, **kwargs):
            # jobs = Job.objects.all()
            
            # Get the current customer
            courier = request.user.courier
            
             # Access the associated user model
            user = courier.user
            
            # Capture the current customer's full name from the associated user model
            full_name = user.get_full_name()  # Retrieve the customer's full name
            
            # Filter the jobs for the current courier with status "completed"
            jobs = Job.objects.filter(courier=courier, status='completed')
            
            # Calculate the total job price using the Sum aggregation function
            total_price = jobs.aggregate(total_price=Sum('price'))['total_price']
            
            # Generate a unique report number using UUID
            report_number = str(uuid.uuid4())[:8]  # Generate a random UUID and truncate to 8 characters
        
        
                             
            data = {
                "company": "DriveXpress",
                "contact": "+2541107800",
                "website": "www.drivex.com",
                "email": "info@drive.com",
                "jobs": jobs,
                "job_price": total_price,  # Add the total job price to the data dictionary
                "courier_name": full_name,  # Add the customer's full name to the data dictionary
                "report_number": report_number,  # Add the invoice number to the data dictionary

            }
            
            pdf = render_to_pdf('courier/pdf_template.html', data)
            
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



@login_required(login_url="/sign-in/?next=/courier/")
def payout_method_page(request):
    payout_form = forms.PayoutForm(instance=request.user.courier)

    if request.method == 'POST':
        payout_form = forms.PayoutForm(
            request.POST, instance=request.user.courier)
        if payout_form.is_valid():
            payout_form.save()

            messages.success(request, "Payout address is updated.")
            return redirect(reverse('courier:profile'))

    return render(request, 'courier/payout_method.html', {
        'payout_form': payout_form
    })
