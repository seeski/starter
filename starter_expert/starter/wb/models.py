from django.db import models
from django.contrib.auth.models import User


# просто хранит все nmid для создания отчетов
class NmidToBeReported(models.Model):

    nmid = models.IntegerField(null=False, unique=True)
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, default='')
    url = models.URLField()
    phrase = models.ForeignKey('SeoCollectorPhrase', blank=True, null=True, on_delete=models.SET_NULL, default=None)
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


# хранит данные об отчетах
# поле nmid хранит данные о том, какой id товара нужно проиндексировать
# поле date хранит дату создания отчета
# поле ready показывает, созданы ли и укомплектованы ли данные по отчету в модели IndexerReportsData
# поле user показывает какой пользователь подгрузил определнный nmid на создание отчета
# для каждого пользователя доступны только созданные им отчеты
class IndexerReport(models.Model):

    nmid = models.IntegerField(null=False)
    date = models.DateField(auto_now_add=True)
    name = models.CharField(max_length=255, default='')
    quick_indexation = models.BooleanField(default=False)
    ready = models.BooleanField(default=False)
    date_of_readiness = models.DateTimeField(null=True, default=None)

    class Meta:
        verbose_name_plural = "Индексатор, Отчеты"
        verbose_name = 'Отчет по индексатору'


# class QuickIndexerReportName(models.Model):
#
#     name = models.CharField(max_length=255)
#     report = models.ForeignKey(IndexerReport, null=False, on_delete=models.CASCADE)


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

    priority_cat = models.CharField(max_length=255, blank=True, null=True)
    keywords = models.CharField(max_length=255)
    frequency = models.IntegerField(null=True)
    req_depth = models.IntegerField()
    existence = models.BooleanField()
    place = models.IntegerField(null=True, default=None)
    spot_req_depth = models.CharField(null=True, default=None, max_length=255)
    ad_spots = models.IntegerField(null=True, default=None)
    ad_place = models.IntegerField(null=True, default=None)
    report = models.ForeignKey(IndexerReport, null=False, on_delete=models.CASCADE)
    quick_indexation = models.BooleanField(default=False)
    product_id = models.IntegerField()
    date = models.DateField(auto_now_add=True, null=True)

    class Meta:
        verbose_name_plural = 'Данные по отчетам Индексация'
        verbose_name = 'Данные по отчету Индексация'


class Request(models.Model):

    keywords = models.CharField(max_length=255)
    normalized_keywords = models.CharField(max_length=255)
    frequency = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Топ запросы'
        verbose_name = 'Топ запрос'

class Cabinet(models.Model):

    name = models.CharField(max_length=255)
    token = models.TextField()
    useless_field = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Кабинет'
        verbose_name_plural = 'Кабинеты'


class SeoCollectorPhrase(models.Model):

    phrase = models.CharField(max_length=255, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    req_depth = models.IntegerField()
    priority_cat = models.CharField(max_length=255, default='')
    ready = models.BooleanField(default=False)

    def __str__(self):
        return self.phrase

    class Meta:
        verbose_name = 'Фраза'
        verbose_name_plural = 'Фразы'


class SeoCollectorPhraseData(models.Model):

    query = models.CharField(max_length=255)
    priority_cat = models.CharField(max_length=255)
    standard = models.BooleanField(default=False)
    frequency = models.IntegerField(null=True, default=None)
    depth = models.IntegerField(null=True, default=None)
    phrase = models.ForeignKey(SeoCollectorPhrase, null=False, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Данные по отчету Сео'
        verbose_name_plural = 'Данные по отчетам Сео'


class Phrase(models.Model):

    phrase = models.CharField(max_length=255, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    req_depth = models.IntegerField()
    frequency = models.IntegerField(null=True, default=None)   
    priority_cat = models.CharField(max_length=255, default='')
    top_category = models.CharField(max_length=255, default='')
    second_top_category = models.CharField(max_length=255, default='')
    third_top_category = models.CharField(max_length=255, default='')
    updated_at = models.DateTimeField(auto_now=True)
    ready = models.BooleanField(default=False)

    def __str__(self):
        return self.phrase

    class Meta:
        verbose_name = 'Статистика топовой фразы'
        verbose_name_plural = 'Статистика топовых фраз'
