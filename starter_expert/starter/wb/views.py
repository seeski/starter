from django.shortcuts import render
from . import utils
from . import tasks
from django.views.generic import ListView, View
from .models import *
from .forms import Upload_excel_file
from asgiref.sync import async_to_sync
from django.db.models import Avg, Q
import asyncio

# Create your views here.

class IndexerView(ListView):

    template_name = 'wb/indexer.html'
    paginate_by = 100
    model = NmidToBeReported
    context_object_name = 'nmids'
    object_list = []

    def post(self, request):
        form = Upload_excel_file(request.POST, request.FILES)
        if form.is_valid():
            file_operator = utils.FileOperator()
            nmids = file_operator.iterate_excel_file(request.FILES['file'].file)
            for nmid in nmids:
                tasks.create_nmid_to_report_task.delay(nmid)

        return render(request, self.template_name)




class SeoPhrasesView(ListView):
    template_name = 'wb/seo_collector.html'
    paginate_by = 100
    model = SeoCollectorPhrase
    context_object_name = 'phrases'

    def post(self, request):
        form = Upload_excel_file(request.POST, request.FILES)
        if form.is_valid():
            SeoCollectorPhrase.objects.all().delete()
            file_operator = utils.FileOperator()
            phrases = file_operator.iterate_excel_file(request.FILES['file'].file)
            for phrase in phrases:
                tasks.create_phrase.delay(phrase)

        return render(request, self.template_name)



class SeoPhrasesDetailView(ListView):

    model = SeoCollectorPhraseData
    template_name = 'wb/seo_phrases_detail.html'
    context_object_name = 'queries'
    object_list = []

    def post(self, request, phrase):
        standards = request.POST.getlist('standards')
        context = self.get_context_data()
        print(context)
        print(standards)
        for query in context['queries']:
            if str(query.id) in standards:
                print('true')
                query.standard = True
                query.save()
            else:
                print('false')
                query.standard = False
                query.save()
        return render(request, self.template_name, self.get_context_data())

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['queries'] = self.model.objects.all().filter(phrase=self.kwargs.get('phrase')).order_by('-standard')
        context['phrases'] = SeoCollectorPhrase.objects.all().filter(id=self.kwargs.get('phrase'))
        return context


class SeoPhraseAddProduct(ListView):
    model = NmidToBeReported
    template_name = 'wb/indexer.html'

    def post(self, request, phrase):
        form = Upload_excel_file(request.POST, request.FILES)
        if form.is_valid():
            file_operator = utils.FileOperator()
            nmids = file_operator.iterate_excel_file(request.FILES['file'].file)
            for nmid in nmids:
                print(nmid, type(nmid))
                tasks.set_product_standard.delay(nmid)

        return render(request, self.template_name, self.get_context_data())

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        phrase = SeoCollectorPhrase.objects.all().filter(id=self.kwargs.get('phrase'))[0]
        print(phrase)
        context['nmids'] = self.model.objects.all().filter(phrase=phrase)
        return context



class SuppliesView(ListView):
    template_name = 'wb/supplies.html'
    model = Cabinet
    context_object_name = 'cabinets'



def nmid_view(request, nmid):
    context = {}
    requests_list = list(data['keywords'] for data in IndexerReportData.objects.all().filter(product_id=nmid).values('keywords').distinct())
    requests = dict([(i,[]) for i in requests_list])
    reports = IndexerReport.objects.all().filter(nmid=nmid, ready=True)
    context_operator = utils.NmidContextOperator(requests, reports)
    context['reports'] = reports
    context['requests'] = context_operator.requests
    return render(request, 'wb/nmid.html', context)

def supplies_detail(request, cabinet):
    data_collector = utils.DataCollector()
    context = {}
    context['cabinets'] = {}
    cabinets = Cabinet.objects.all().filter(id=cabinet)
    for cabinet in cabinets:
        supplies = asyncio.run(data_collector.get_supplies(cabinet.token, cabinet.name))
        context['cabinets'][cabinet.name] = supplies
    return render(request, 'wb/supplies_detail.html', context=context)