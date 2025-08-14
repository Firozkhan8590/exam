from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from .models import URL

def home(request):
    short_url = None
    if request.method == "POST":
        long_url = request.POST.get("long_url")
        if long_url:
            url_obj = URL(long_url=long_url)
            url_obj.save()
            short_url = request.build_absolute_uri('/') + url_obj.short_code
    urls = URL.objects.all().order_by('-clicks') 
    return render(request, "home.html", {"short_url": short_url, "urls": urls})

def redirect_url(request, code):
    url_obj = get_object_or_404(URL, short_code=code)
   
    # Increment click counter
    url_obj.clicks += 1
    url_obj.save()
    return redirect(url_obj.long_url)


def delete_url(request, id):
    url_obj = get_object_or_404(URL, id=id)
    url_obj.delete()
    return redirect('home')


# Create your views here.
