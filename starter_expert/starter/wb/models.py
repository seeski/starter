from django.db import models
from django.contrib.auth.models import User


# просто хранит все nmid для создания отчетов
class NmidToBeReported(models.Model):

    nmid = models.IntegerField(null=False, unique=True)
    name = models.CharField(max_length=255)
    url = models.URLField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        verbose_name_plural = "Товары"


# хранит данные об отчетах
# поле nmid хранит данные о том, какой id товара нужно проиндексировать
# поле date хранит дату создания отчета
# поле ready показывает, созданы ли и укомплектованы ли данные по отчету в модели IndexerReportsData
# поле user показывает какой пользователь подгрузил определнный nmid на создание отчета
# для каждого пользователя доступны только созданные им отчеты
class IndexerReport(models.Model):

    nmid = models.IntegerField(null=False)
    date = models.DateTimeField(auto_now_add=True)
    ready = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        verbose_name_plural = "Индексатор, Отчеты"


#  хранит собранные данные по каждому отчету
#  nmid - хранит в себе id товара, который был проиндексирован. Возможно поле в последующем удалиться за ненадобностью
#  priority_cat - хранит данные о приоритетной категории по определенному запросу
# keywords - хранится строка с поисковым запросом, по которому было совпадение
# frequency - лежит число запросов за x времени из файлика requests.csv (насколько популярен запрос)
# rep_depth - хранится дата о кол-ве выданных результатов по определенному запросу
# existence - есть ли товар в поисковой выдаче по данному запросу
# place - место в поисковой выдаче в пределах 1000 запросов (за пределами 1000 место не определяется)
#  spot_req_depth - процент топа поисковой выдачи (если место товара в пределах первой 1000)
# ad_spots - кол-во рекламных мест
# ad_place - место в рекламной выдаче
# report_id - внешний ключ связывающий отчет с записью в
class IndexerReportData(models.Model):

    priority_cat = models.CharField(max_length=255)
    keywords = models.CharField(max_length=255)
    frequency = models.IntegerField()
    req_depth = models.IntegerField()
    existence = models.BooleanField()
    place = models.IntegerField(null=True, default=None)
    spot_req_depth = models.CharField(null=True, default=None, max_length=255)
    ad_spots = models.IntegerField(null=True, default=None)
    ad_place = models.IntegerField(null=True, default=None)
    report = models.ForeignKey(IndexerReport, null=False, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Данные по отчетам'


class Request(models.Model):

    keywords = models.CharField(max_length=255)
    normalized_keywords = models.CharField(max_length=255)
    frequency = models.IntegerField()

    class Meta:
        verbose_name_plural = 'Топ запросы'
        verbose_name = 'Топ запрос'