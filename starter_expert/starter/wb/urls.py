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
    path('seo-phrases/<int:phrase>/download', views.download_seo_report, name='wb_download_seo_phrase'),
    path('quick-indexation', views.QuickIndexationView.as_view(), name='wb_quick_indexation'),
    path('quick-indexation/<int:report>', views.QuickIndexationDetailView.as_view(), name='wb_quick_indexation_detail'),
    path('quick-indexation/<int:report>/download', views.download_quick_indexation_report, name='wb_download_report'),
]