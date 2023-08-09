from celery import shared_task
from . import utils
from django.contrib.auth.models import User
from asgiref.sync import async_to_sync
from . import models
import time


# каждые выходные обновляет файл с миллионом запросов
# также сразу приводит каждый запрос в начальную форму
async def update_requests():
    data_collector = utils.DataCollector()
    requests_data = await data_collector.getRequestsData()
    for request_data in requests_data:

        load_and_normalize_request.delay(request_data=request_data)



@shared_task
def load_and_normalize_request(request_data: dict):
    keywords = request_data.get('keywords')
    frequency = request_data.get('frequency')
    normalized_keywords = utils.normalize_text(keywords)
    models.Request.objects.create(
        keywords=keywords, frequency=frequency, normalized_keywords=normalized_keywords
    )

@shared_task
def update_requests_task():
    models.Request.objects.all().delete()
    async_to_sync(update_requests)()