from django.shortcuts import render, redirect
from . import utils
from . import tasks
from django.views.generic import ListView, View
from .models import *
from .forms import *
from asgiref.sync import async_to_sync
from django.db.models import Avg, Q
import asyncio
from django.http import FileResponse

# Create your views here.

class IndexerView(ListView):

    template_name = 'wb/indexer.html'
    paginate_by = 100
    model = NmidToBeReported
    context_object_name = 'nmids'
    object_list = []

    def post(self, request):
        file_form = Upload_excel_file(request.POST, request.FILES)
        add_nmid_value = utils.check_int(request.POST.get('add_nmid'))
        search_value = utils.check_int(request.POST.get('search'))
        if file_form.is_valid():
            file_operator = utils.FileOperator()
            nmids = file_operator.iterate_excel_file(request.FILES['file'].file)
            for nmid in nmids:
                tasks.create_nmid_to_report_task.delay(nmid)

        if add_nmid_value:
            tasks.create_nmid_to_report_task.delay(int(add_nmid_value))
        if search_value:
            product_obj = self.model.objects.all().filter(nmid=search_value).filter()
            if product_obj:
                return redirect('wb_product_reports_data', nmid=search_value)

        return render(request, self.template_name, self.get_context_data())


    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nmids'] = self.model.objects.all()
        return context





class SeoPhrasesView(ListView):
    template_name = 'wb/seo_collector.html'
    paginate_by = 100
    model = SeoCollectorPhrase
    object_list = []

    context_object_name = 'phrases'

    def post(self, request):
        file_form = Upload_excel_file(request.POST, request.FILES)
        phrase = request.POST.get('add_phrase')
        if file_form.is_valid():
            file_operator = utils.FileOperator()
            phrases = file_operator.iterate_excel_file(request.FILES['file'].file)
            for phrase in phrases:
                tasks.create_phrase.delay(phrase)

        if phrase:
            tasks.create_phrase.delay(phrase)

        return render(request, self.template_name, self.get_context_data())


    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['phrases'] = self.model.objects.all()
        return context


class SeoPhrasesDetailView(ListView):

    model = SeoCollectorPhraseData
    template_name = 'wb/seo_phrases_detail.html'
    context_object_name = 'queries'
    object_list = []

    def post(self, request, phrase):
        standards = request.POST.getlist('standards')
        context = self.get_context_data()
        for query in context['queries']:
            if str(query.id) in standards:
                query.standard = True
                query.save()
            else:
                query.standard = False
                query.save()
        return render(request, self.template_name, self.get_context_data())

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['queries'] = self.model.objects.all().filter(phrase=self.kwargs.get('phrase')).order_by('-standard', 'priority_cat', 'query')
        context['phrases'] = SeoCollectorPhrase.objects.all().filter(id=self.kwargs.get('phrase'))
        return context


class SeoPhraseAddProduct(ListView):
    model = NmidToBeReported
    template_name = 'wb/seo_phrase_add_product.html'
    object_list = []

    def post(self, request, phrase):
        form = Upload_excel_file(request.POST, request.FILES)
        add_nmid = utils.check_int(request.POST.get('add_nmid'))

        if form.is_valid():
            file_operator = utils.FileOperator()
            nmids = file_operator.iterate_excel_file(request.FILES['file'].file)
            for nmid in nmids:
                tasks.set_product_standard.delay(nmid, int(phrase))

        if add_nmid:
            tasks.set_product_standard.delay(add_nmid, int(phrase))



        return render(request, self.template_name, self.get_context_data())

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        phrase = SeoCollectorPhrase.objects.all().filter(id=self.kwargs.get('phrase')).first()
        context['nmids'] = self.model.objects.all().filter(phrase=phrase)
        context['phrases'] = [phrase]
        return context



class SuppliesView(ListView):
    template_name = 'wb/supplies.html'
    model = Cabinet
    context_object_name = 'cabinets'



def nmid_view(request, nmid):
    nmid_obj = NmidToBeReported.objects.all().get(nmid=nmid)
    context = {}
    requests_list = list(data['keywords'] for data in IndexerReportData.objects.all().filter(product_id=nmid).values('keywords').distinct())
    requests = dict([(i,[]) for i in requests_list])
    reports = IndexerReport.objects.all().filter(nmid=nmid, ready=True)
    context_operator = utils.NmidContextOperator(requests, reports)
    context['reports'] = reports
    context['requests'] = context_operator.requests
    context['product'] = nmid_obj

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


def download_seo_report(request, phrase):
    file_operator = utils.FileOperator()
    buffer = file_operator.create_seo_report_buffer(phrase_id=phrase)
    phrase_obj = SeoCollectorPhrase.objects.all().get(id=phrase)

    return FileResponse(buffer, as_attachment=True, filename=f'фразы "{phrase_obj.phrase}".xlsx')