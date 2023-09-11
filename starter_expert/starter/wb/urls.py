from django.urls import path
from . import views

urlpatterns = [
    path('indexer/', views.IndexerView.as_view(), name='wb_indexer'),
    path('indexer/<int:nmid>', views.nmid_view, name='wb_product_reports_data'),
    path('supplies/', views.SuppliesView.as_view(), name='wb_supplies'),
    path('supplies/<int:cabinet>', views.supplies_detail, name='wb_supplies_detail'),
    path('seo-phrases', views.SeoPhrasesView.as_view(), name='wb_seo_phrases'),
    path('seo-phrases/<int:phrase>', views.SeoPhrasesDetailView.as_view(), name='wb_seo_phrases_detail'),
    path('seo-phrases/<int:phrase>/add-product', views.SeoPhraseAddProduct.as_view(), name='wb_seo_add_product'),
]