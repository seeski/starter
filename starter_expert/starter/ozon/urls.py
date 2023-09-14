from django.urls import path, re_path
from django.shortcuts import redirect
from .views import IndexerView, DetailView, CreateNmidToBeReported

urlpatterns = [
	path('indexer/', IndexerView.as_view(), name="ozon_indexer"),
	path('indexer/<int:nmid>/', DetailView.as_view(), name="detail_report_info"),
	path('add-nmid/', CreateNmidToBeReported.as_view(), name="add_nmid"),
	re_path(".*", lambda x: redirect("ozon_indexer")),
]
