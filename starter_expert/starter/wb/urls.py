from django.urls import path
from . import views

urlpatterns = [
    path('indexer/', views.IndexerView.as_view(), name='wb_indexer'),
    path('indexer/<int:nmid>', views.nmid_view, name='wb_product_reports_data'),
    path('supplies', views.supplies, name='wb_supplies')
]