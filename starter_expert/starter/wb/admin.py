from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Request)
admin.site.register(NmidToBeReported)
admin.site.register(IndexerReport)
admin.site.register(IndexerReportData)