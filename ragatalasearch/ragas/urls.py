from django.urls import path
from . import views

app_name = 'ragas'
print("Loading ragas.urls")
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
    
    # Raga Similarity Graph URLs
    path('graph/', views.RagaSimilarityGraphView.as_view(), name='similarity_graph'),
    path('find-similar/', views.FindSimilarRagasView.as_view(), name='find_similar_ragas'),
    path('api/graph/data/', views.graph_data_api, name='graph_data_api'),
    path('api/graph/build/', views.build_graph_api, name='build_graph_api'),
    path('api/graph/neighbors/<int:raga_id>/', views.raga_neighbors_api, name='raga_neighbors_api'),
    
    # Semantic Similarity URLs
    path('api/similarity/search/', views.semantic_similarity_search, name='semantic_similarity_search'),
    path('api/embeddings/generate/', views.generate_raga_embeddings, name='generate_embeddings'),
    path('api/embeddings/status/', views.embedding_status, name='embedding_status'),
    
]