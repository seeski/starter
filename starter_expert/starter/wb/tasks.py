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


# таска нормализует запрос и записывает данные по нему в бд
@shared_task
def load_and_normalize_request(request_data: dict):
    keywords = request_data.get('keywords')
    frequency = request_data.get('frequency')
    normalized_keywords = utils.normalize_text(keywords)
    models.Request.objects.create(
        keywords=keywords, frequency=frequency, normalized_keywords=normalized_keywords
    )

# запускает обновление топ миллиона запросов

@shared_task
def update_requests_task():
    models.Request.objects.all().delete()
    async_to_sync(update_requests)()



# таска для создание записи о определенном nmid
# таска потому что обращаемся к апи вб
# если nmid в подгружаемом файле будет много, то клиент будет долго ждать ответа
async def create_nmid_to_report(nmid):
    nmid_url = f'https://www.wildberries.ru/catalog/{nmid}/detail.aspx'
    urlOperator = utils.URLOperator()
    dataCollector = utils.DataCollector()

    detail_url = urlOperator.create_nmid_detail_url(nmid)
    name = await dataCollector.get_brand_and_name(detail_url)
    return [name, nmid_url]


@shared_task
def create_nmid_to_report_task(nmid):
    name, nmid_url = async_to_sync(create_nmid_to_report)(nmid)

    try:
        models.NmidToBeReported.objects.create(
            nmid=nmid,
            name=name,
            url=nmid_url,
        )

    except Exception as e:
        print(e)

@shared_task
def create_indexer_report(report_id, nmid):
    utils.createReportData(report_id, nmid)

@shared_task
def create_indexer_reports_task():
    nmids = models.NmidToBeReported.objects.all()

    for nmid in nmids:
        report = models.IndexerReport.objects.create(
            nmid=nmid.nmid
        )
        create_indexer_report.delay(report.id, report.nmid)


@shared_task
def create_phrase(phrase):
    seo_collector = utils.SeoCollector(phrase=phrase)
    print(phrase)
    seo_collector.run()

@shared_task
def set_product_standard(nmid, phrase):
    try:
        product_obj = models.NmidToBeReported.objects.all().filter(nmid=nmid)[0]
        seo_phrase_obj = models.SeoCollectorPhrase.objects.all().filter(phrase=phrase)[0]
        product_obj.phrase = seo_phrase_obj
        product_obj.save()
    except Exception as e:
        print(f'error at set_product_standard_task: {type(e).__name__} -- {e}')