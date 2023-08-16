from django.shortcuts import render
from . import utils
from . import tasks
from django.views.generic import ListView, View
from .models import NmidToBeReported, IndexerReport, IndexerReportData
from .forms import Upload_nmids_form
from django.db.models import Avg, Q

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
    reports = IndexerReport.objects.all().filter(nmid=nmid)
    context_operator = utils.NmidContextOperator(requests, reports)
    context['reports'] = reports
    # for request in context_operator.requests:
    #     print(f'{context_operator.requests[request]}\n\n\n\n')
    context['requests'] = context_operator.requests

    return render(request, 'wb/nmid.html', context)