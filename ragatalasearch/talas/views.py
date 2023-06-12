from django.shortcuts import render
from django.views import View
from django.views.generic import DetailView
from .models import Tala
from django.http import HttpResponse

class TalaNameListView(View):
    template_name = 'talas/tala_namelist.html'
    def get(self,request):
        strval = request.GET.get("search",False)
        if strval:
            tala_list = Tala.objects.all().filter(name__contains=strval)
        else:
            tala_list=None
        ctx = {'tala_list':tala_list,'search':strval}   
        return render(request,self.template_name,ctx) 

class TalaAkListView(View):
    template_name='talas/tala_list.html'
    def get(self,request):
        strval = request.GET.get("search",False)
        if strval :
            tala_list = Tala.objects.all().filter(aksharas=strval)
        else:
            tala_list = None
        ctx = {'tala_list':tala_list,'search':strval}  
        return render(request, self.template_name, ctx)      

class TalaDetailView(DetailView):
    model = Tala
    template_name = 'talas/tala_detail.html'
    def get(self,request,pk):
        x = Tala.objects.all().get(id = pk)
        ctx = {'tala':x}
        return render(request, self.template_name, ctx)   

class TalaTableView(View):
    template_name= 'talas/tala_table.html'
    def get(self,request):
        strval = request.GET.get("search", False)
        if strval:
            tala_table = Tala.objects.all().filter(category__name= strval.rstrip())     
        else:
            tala_table = None
        ctx = {'tala_table':tala_table, 'search':strval}
        return render(request, self.template_name, ctx)             

