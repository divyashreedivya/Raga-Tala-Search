from django.contrib import admin
from ragas.models import Raga, Melakarta, RagaEdge

@admin.register(Melakarta)
class MelakarataAdmin(admin.ModelAdmin):
    list_display = ['name', 'num']
    search_fields = ['name']

@admin.register(Raga)
class RagaAdmin(admin.ModelAdmin):
    list_display = ['name', 'mela', 'mela_true']
    list_filter = ['mela_true', 'mela']
    search_fields = ['name']

@admin.register(RagaEdge)
class RagaEdgeAdmin(admin.ModelAdmin):
    list_display = ['source_raga', 'target_raga', 'similarity_score', 'shared_notes']
    list_filter = ['similarity_score']
    search_fields = ['source_raga__name', 'target_raga__name']
    ordering = ['-similarity_score']
