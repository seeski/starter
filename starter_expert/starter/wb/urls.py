from django.urls import path
from . import views

urlpatterns = [
    path('indexer/', views.IndexerView.as_view(), name='indexer'),
    # path('indexer/<int:product_id>', views.IndexerNmidView.as_view(), name='product_reports_data')
]