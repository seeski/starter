from django.urls import path
from . import views

urlpatterns = [
    path('indexer/', views.IndexerView.as_view(), name='indexer'),
    path('indexer/<int:nmid>', views.nmid_view, name='product_reports_data')
]