from django.shortcuts import render, redirect, HttpResponse


def support_services(request):
    return render(request, 'support_services/services.html')