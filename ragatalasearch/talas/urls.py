from django.urls import path
from . import views 

app_name= 'talas'
urlpatterns=[
    path('name/',views.TalaNameListView.as_view(),name='tala_namelist'),
    path('name/<int:pk>/',views.TalaDetailView.as_view(),name='tala_detail'),
    path('aksharas/', views.TalaAkListView.as_view(), name='tala_list'),
    path('aksharas/<int:pk>/',views.TalaDetailView.as_view(),name='tala_ak_detail'),
    path('table/', views.TalaTableView.as_view(), name="tala_table"),
]