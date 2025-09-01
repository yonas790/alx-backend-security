from django.shortcuts import render
from django.http import JsonResponse
from ratelimit.decorators import ratelimit

# Anonymous users 5 req/min
@ratelimit(key='ip', rate='5/m', method='POST', block=True)
# Authenticated users 10 req/min
@ratelimit(key='user_or_ip', rate='10/m', method='POST', block=True)
def login_view(request):
    if request.method == "POST":
        return JsonResponse({"message": "Login attempt processed"})
    return JsonResponse({"error": "Invalid request"}, status=400)

def user_or_ip(request):
    return request.user.pk if request.user.is_authenticated else request.META.get("REMOTE_ADDR")

