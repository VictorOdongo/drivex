from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from core.models import *


@csrf_exempt
@login_required(login_url="/courier/sign-in/")
def available_jobs_api(request):
    jobs = list(Job.objects.filter(status=Job.PROCESSING_STATUS).values())

    return JsonResponse({
        "success": True,
        "jobs": jobs
    })


@csrf_exempt
@login_required(login_url="/courier/sign-in/")
def current_job_update_api(request, id):
    job = Job.objects.filter(
        id=id,
        courier=request.user.courier,
        status__in=[
            Job.PICKING_STATUS,
            Job.DELIVERING_STATUS
        ]
    ).last()

    if job.status == Job.PICKING_STATUS:
        job.pickup_photo = request.FILES['pickup_photo']
        job.pickedup_at = timezone.now()
        job.status = Job.DELIVERING_STATUS
        job.save()

    elif job.status == Job.DELIVERING_STATUS:
        job.delivery_photo = request.FILES['delivery_photo']
        job.delivered_at = timezone.now()
        job.status = Job.COMPLETED_STATUS
        job.save()

    return JsonResponse({
        "success": True
    })


@csrf_exempt
@login_required(login_url="/courier/sign-in/")
def fcm_token_update_api(request):
    request.user.courier.fcm_token = request.GET.get('fcm_token')
    request.user.courier.save()

    return JsonResponse({
        "success": True
    })
