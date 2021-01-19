from django.shortcuts import  HttpResponse,HttpResponseRedirect,Http404,render

def homepage(request):
    return render(request,'index.html',status=200)

def resultsPage(request):
    return render(request,'results.html',status=200)