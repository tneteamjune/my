from django.shortcuts import render

# Create your views here.
from .models import MapInfo


def index(request):
    MapInfos = MapInfo.objects.all()
    context = { 'MapInfos': MapInfos }
    return render(request, 'pybo/index.html', context)