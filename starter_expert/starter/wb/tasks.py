import datetime
from celery import shared_task
from . import utils
from django.contrib.auth.models import User
from asgiref.sync import async_to_sync
from . import models
from datetime import date, timezone


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
    name, brand = await dataCollector.get_brand_and_name(detail_url)
    return [name, brand, nmid_url]


@shared_task
def create_nmid_to_report_task(nmid):
    name, brand, nmid_url = async_to_sync(create_nmid_to_report)(nmid)

    try:
        models.NmidToBeReported.objects.create(
            nmid=nmid,
            name=name,
            brand=brand,
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
    today = date.today()
    for nmid in nmids:

        report = models.IndexerReport.objects.all().filter(nmid=nmid.nmid, date=today).first()
        if not report:
            print('new report')
            new_report = models.IndexerReport.objects.create(
                nmid=nmid.nmid
            )
            print(f'create_indexer_reports_task {new_report.nmid}')
            create_indexer_report.delay(new_report.id, new_report.nmid)



@shared_task
def create_phrase(phrase):
    seo_collector = utils.SeoCollector(phrase=phrase)
    seo_collector.run()

@shared_task
def set_product_standard(nmid, phrase):
    try:
        product_obj = models.NmidToBeReported.objects.all().filter(nmid=nmid).first()
        seo_phrase_obj = models.SeoCollectorPhrase.objects.all().filter(id=phrase).first()
        product_obj.phrase = seo_phrase_obj
        product_obj.save()
    except Exception as e:
        print(f'error at set_product_standard_task: {type(e).__name__} -- {e}')


@shared_task
def create_quick_report_task(nmid):
    today = date.today()
    product_info = async_to_sync(create_nmid_to_report)(nmid)
    report = models.IndexerReport.objects.create(
        nmid=nmid,
        quick_indexation=True,
        product_name=product_info[0]
    )
    utils.create_quick_indexation_report(report.id, report.nmid)

# @shared_task
# def clean_quick_indexation_task():
#     now = datetime.datetime.now()
#     one_day_delta = datetime.timedelta(days=1)
#
#     print(now, one_day_delta)
#
#     reports = models.IndexerReport.objects.all().filter(quick_indexation=True)
#     for report in reports:
#         try:
#
#             report.date_of_readiness = now
#             report.save()
#         except Exception as e:
#             print(f'{type(e).__name__} :: {e}')

# @shared_task
# def delete_useless_quick_indexation_report():
#     today = date.today()

