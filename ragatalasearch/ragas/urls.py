from django.urls import path
from . import views

app_name = 'ragas'
urlpatterns=[
    path('',views.SearchRaga.as_view(), name= "search"),
    path('raga/',views.RagaListView.as_view(), name = 'name'),
    path('raga/<int:pk>/',views.RagaDetailView.as_view(), name ='raga_detail'),
    path('arohana/', views.RagaArListView.as_view(), name='arohana'),
    path('arohana/<int:pk>/', views.RagaDetailView.as_view(), name='raga_ar_detail'),
    path('avarohana/', views.RagaAvListView.as_view(), name='avarohana'),
    path('avarohana/<int:pk>/', views.RagaDetailView.as_view(), name='raga_av_detail'),
    path('table',views.RagaTableView.as_view(), name='raga_table'),
    path('table/<int:pk>/', views.RagaMelaDetailView.as_view(),name='raga_mela_detail'),
]