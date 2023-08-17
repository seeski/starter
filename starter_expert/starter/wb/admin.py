from django.contrib import admin
from .models import *
# Register your models here.

class RequestAdmin(admin.ModelAdmin):
    list_display = ('keywords', 'frequency', 'normalized_keywords')

class NmidAdmin(admin.ModelAdmin):
    list_display = ('nmid', 'name', 'url', 'user')

class IndexerReportAdmin(admin.ModelAdmin):
    list_display = ('nmid', 'date', 'ready', 'user')

class IndexerReportDataAdmin(admin.ModelAdmin):
    list_display = ('keywords', 'priority_cat', 'frequency', 'req_depth', 'existence', 'place',
                    'spot_req_depth', 'ad_spots', 'ad_place', 'report', 'product_id')

class CabinetAdmin(admin.ModelAdmin):
    list_display = ('name', 'token')

admin.site.register(Request, RequestAdmin)
admin.site.register(NmidToBeReported, NmidAdmin)
admin.site.register(IndexerReport, IndexerReportAdmin)
admin.site.register(IndexerReportData, IndexerReportDataAdmin)
admin.site.register(Cabinet, CabinetAdmin)