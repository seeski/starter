from django.contrib import admin
from .models import OzonNmidToBeReported, OzonIndexerReport, OzonIndexerReportData

admin.site.register(OzonNmidToBeReported)
admin.site.register(OzonIndexerReport)
admin.site.register(OzonIndexerReportData)
# Register your models here.
