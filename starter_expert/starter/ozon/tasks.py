import asyncio

from django.core.paginator import Paginator
from celery import shared_task
from .utils import ozon_parser, create_nmid_to_report
from .models import OzonNmidToBeReported, DateCreateReports
from django.contrib.auth.models import User


@shared_task
def create_indexer_report_task(*nmids_and_users_id):
    asyncio.run(ozon_parser(*nmids_and_users_id))


@shared_task
def create_indexer_reports_task():
    pages = Paginator(list(OzonNmidToBeReported.objects.all()), 1)
    date_create_reports = DateCreateReports.objects.create()
    for page in pages:
        nmids_and_users_id = []
        for nmid_obj in page.object_list:
            nmids_and_users_id.append((nmid_obj.nmid, nmid_obj.user.pk))

        create_indexer_report_task.delay(date_create_reports.pk, *nmids_and_users_id)


@shared_task
def create_nmid_to_report_task(nmid, user_id):
    asyncio.run(create_nmid_to_report(nmid, user_id))