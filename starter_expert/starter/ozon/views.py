from django.shortcuts import render, redirect
from django.views.generic import ListView
from .models import OzonNmidToBeReported, OzonIndexerReport, OzonIndexerReportData, DateCreateReports, User
from . import tasks
from .forms import Upload_nmids_form
from .utils import FileOperator
from .ozon_parser import OzonIndexerManager
import asyncio

from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.search import (
    SearchRank,
    SearchVector,
    SearchQuery
)
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.views import View


class IndexerLoginRequiredMixin(LoginRequiredMixin):
    redirect_field_name = "/account/cabinet/"


class IndexerView(IndexerLoginRequiredMixin, ListView):
    template_name = 'ozon/indexer.html'

    paginate_by = 100
    model = OzonNmidToBeReported

    def get(self, request, *args, **kwargs):
        self.search = self.request.GET.get('search')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if self.search is None:
            return self.model.objects.filter(user=self.request.user)
        else:
            query = SearchQuery(self.search)
            vector = SearchVector("name")
            return self.model.objects.filter(user=self.request.user).annotate(
                rank = SearchRank(query, vector)
            ).order_by("-rank")

    def post(self, request):
        user = request.user
        form = Upload_nmids_form(request.POST, request.FILES)
        if form.is_valid():
            file_operator = FileOperator()
            nmids = file_operator.iterate_nmids(request.FILES['file'].file)
            for nmid in nmids:
                tasks.create_nmid_to_report_task.delay(nmid, user.pk)

        return redirect("ozon_indexer")


"""
class LoginUser(LoginView):
    form_class = AuthenticationForm
    template_name = 'ozon/login.html'

    def get_success_url(self):
        return reverse_lazy('ozon_indexer')


class LogoutUser(LogoutView):
    pass


"""
class CreateNmidToBeReported(IndexerLoginRequiredMixin, FormView):
    pass


class DetailView(IndexerLoginRequiredMixin, TemplateView):

    template_name = "ozon/detail.html"

    def dispatch(self, request, nmid, *args, **kwargs):
        self.nmid = nmid 
        return super().dispatch(request, nmid, *args, **kwargs)
    
    def get_context_data(self):
        context = super().get_context_data()
        data = OzonIndexerReportData\
            .objects\
            .select_related("report")\
            .select_related("report__date_create_reports")\
            .filter(
                report__nmid = self.nmid
            )

        table = {}
        keywords_set = set([])
        date_set = set([])
        for i in data:
            keywords = i.keywords
            date = i.report.date_create_reports.date
            try:
                table[keywords]
            except KeyError:
                table[keywords] = {}

            table[keywords][date] = i
            keywords_set.add(keywords)
            date_set.add(date)

        keywords_list = list(sorted(keywords_set))
        date_list = list(sorted(date_set))
        result_table = []
        for keywords in keywords_list:
            report_data = []
            for date in date_list:
                try:
                    table[keywords][date]
                except KeyError:
                    table[keywords][date] = None
                report_data.append(table[keywords][date])

            result_table.append([keywords, *report_data])

        context['table'] = result_table
        context['keywords_list'] = keywords_list
        context['date_list'] = date_list
        return context


