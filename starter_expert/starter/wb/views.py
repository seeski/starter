from django.shortcuts import render
from . import utils
from . import tasks
from django.views.generic import ListView, View
from .models import NmidToBeReported, IndexerReport, IndexerReportData, Cabinet
from .forms import Upload_nmids_form
from asgiref.sync import async_to_sync
from django.db.models import Avg, Q
import asyncio

# Create your views here.

class IndexerView(ListView):

    template_name = 'wb/indexer.html'
    paginate_by = 100
    model = NmidToBeReported
    context_object_name = 'nmids'

    def post(self, request):
        user = request.user
        user_id = user.id
        form = Upload_nmids_form(request.POST, request.FILES)
        if form.is_valid():
            file_operator = utils.FileOperator()
            nmids = file_operator.iterate_nmids(request.FILES['file'].file)
            for nmid in nmids:
                tasks.create_nmid_to_report_task.delay(nmid, user_id)

        return render(request, self.template_name)



def nmid_view(request, nmid):
    context = {}
    requests_list = list(data['keywords'] for data in IndexerReportData.objects.all().filter(product_id=nmid).values('keywords').distinct())
    requests = dict([(i,[]) for i in requests_list])
    reports = IndexerReport.objects.all().filter(nmid=nmid, ready=True)
    context_operator = utils.NmidContextOperator(requests, reports)
    context['reports'] = reports
    context['requests'] = context_operator.requests
    return render(request, 'wb/nmid.html', context)


def supplies(request, cabinet):
    data_collector = utils.DataCollector()
    context = {}
    context['cabinets'] = {}
    cabinets = Cabinet.objects.all().filter(id=cabinet)
    for cabinet in cabinets:
        supplies = asyncio.run(data_collector.get_supplies(cabinet.token, cabinet.name))
        context['cabinets'][cabinet.name] = supplies
    return render(request, 'wb/supplies.html', context=context)