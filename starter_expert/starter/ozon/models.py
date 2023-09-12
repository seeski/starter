from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class OzonNmidToBeReported(models.Model):

    nmid = models.IntegerField(null=False, unique=True)
    name = models.CharField(max_length=255)
    #seo_collector_keywords = models.ForeignKey('Seo_collector_report', null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class DateCreateReports(models.Model):
    date = models.DateTimeField(auto_now_add=True)

    @property
    def view_date(self):
        return self.date.strftime('%d.%m.%Y')

# хранит данные об отчетах
# поле nmid хранит данные о том, какой id товара нужно проиндексировать
# поле date хранит дату создания отчета
# поле ready показывает, созданы ли и укомплектованы ли данные по отчету в модели IndexerReportsData
# поле user показывает какой пользователь подгрузил определнный nmid на создание отчета
# для каждого пользователя доступны только созданные им отчеты
class OzonIndexerReport(models.Model):

    nmid = models.IntegerField(null=False)
    date = models.DateTimeField(auto_now_add=True)
    ready = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    date_create_reports = models.ForeignKey(
        DateCreateReports,
        on_delete=models.CASCADE,
        null=False
    )

    class Meta:
        verbose_name_plural = "Индексатор, Отчеты"
        verbose_name = 'Отчет по индексатору'


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

class OzonIndexerReportData(models.Model):

    priority_cat = models.CharField(
        max_length=255, 
        blank=True, 
        null=True
    )
    keywords = models.CharField(
        max_length=255, 
        verbose_name="Поисковой запрос"
    )
    frequency = models.IntegerField(
        verbose_name="Насколько популярен запрос"
    )
    req_depth = models.IntegerField(
        verbose_name="Количество товара"
    )
    existence = models.BooleanField(
        verbose_name="Есть в топовой выдаче"
    )
    place = models.IntegerField(
        null=True, 
        default=None
    )
    spot_req_depth = models.CharField(
        null=True, 
        default=None, 
        max_length=255
    )
    report = models.ForeignKey(
        OzonIndexerReport, 
        null=False, 
        on_delete=models.CASCADE,
        related_name="report",
    )

    def __str__(self):
        return self.keywords

    class Meta:
        verbose_name_plural = 'Данные по отчетам'
        verbose_name = 'Данные по отчету'