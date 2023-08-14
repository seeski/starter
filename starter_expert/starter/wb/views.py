from django.shortcuts import render
from . import utils
from . import tasks
from django.views.generic import ListView, View
from .models import NmidToBeReported, IndexerReport, IndexerReportData
from .forms import Upload_nmids_form

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



# class IndexerNmidView(ListView):
#     template_name = 'wb/indexer_reports.html'
#     paginate_by = 100
#     model = IndexerReportData
#     context_object_name = 'nmid_reports'
#
#     def get_context_data(self, *, object_list=None, **kwargs):
