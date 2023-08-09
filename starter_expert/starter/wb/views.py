from django.shortcuts import render
from django.views.generic import ListView
from .models import NmidToBeReported, IndexerReport, IndexerReportData

# Create your views here.

class IndexerView(ListView):

    template_name = 'wb/indexer.html'
    paginate_by = 50
    queryset = IndexerReport.objects.all()
    context_object_name = 'reports'