from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from ragas.models import Raga, Melakarta
from django.views.generic import DetailView

class SearchRaga(View):
    def get(self,request):
        return render(request, 'ragas/raga_search.html')

class RagaListView(View):
    template_name = 'ragas/raga_list.html'

    def get(self,request):
        strval = request.GET.get("search", False)
        raga_exact = None
        if strval:
            raga_list = Raga.objects.all().filter(name__contains = strval).select_related()
        else:
            #raga_list = Raga.objects.all()[:5]
            raga_list = None
            
        ctx ={'raga_list':raga_list , 'search':strval}
        return render(request, self.template_name, ctx)

class RagaArListView(View):
    template_name = 'ragas/raga_ar_list.html'

    def get(self, request):
        strval = request.GET.get("search", False)
        if strval:
            raga_list = Raga.objects.all().filter(arohanam__contains = strval.rstrip()).select_related()
        else:
            raga_list = None
        ctx = {'raga_list':raga_list, 'search':strval}       
        return render(request, self.template_name, ctx)       

class RagaAvListView(View):
    template_name = 'ragas/raga_av_list.html'

    def get(self, request):
        strval = request.GET.get("search", False)
        if strval:
            raga_list = Raga.objects.all().filter(avarohanam__contains = strval.rstrip()).select_related()
        else:
            raga_list = None
        ctx = {'raga_list':raga_list, 'search':strval}       
        return render(request, self.template_name, ctx)   

class RagaTableView(View):
    template_name='ragas/raga_table.html'
    def get(self, request):
        mela_list = Raga.objects.all().filter(mela_true=True) 
        return render(request, self.template_name, {'mela_list':mela_list})       


class RagaDetailView(DetailView):
    model =Raga
    template_name = 'ragas/raga_detail.html'
    def get(self, request, pk):
        x = Raga.objects.all().get(id= pk)
        ctx = {'raga': x}
        return render(request, self.template_name, ctx)

class RagaMelaDetailView(DetailView):
    model = Raga
    template_name = 'ragas/raga_mela_detail.html'
    def get(self, request, pk):
        x = Raga.objects.all().get(id=pk)
        y = Raga.objects.all().filter(mela_id = x.mela_id)[1:]
        ctx = {'raga':x,'janyas':y} 
        return render(request, self.template_name, ctx)       
