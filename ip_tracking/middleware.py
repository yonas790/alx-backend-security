import datetime
from django.core.cache import cache
from django.utils.timezone import now
from ipgeolocation import IpGeolocationAPI
from .models import RequestLog


class IPTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.geo_api = IpGeolocationAPI("YOUR_API_KEY")  # Replace with your key

    def __call__(self, request):
        ip = self.get_client_ip(request)
        path = request.path
        timestamp = now()

        # Cache lookup for 24h
        cache_key = f"geo_{ip}"
        geo_data = cache.get(cache_key)

        if not geo_data:
            try:
                response = self.geo_api.get_geolocation(ip_address=ip)
                country = response.get("country_name", "")
                city = response.get("city", "")
                geo_data = {"country": country, "city": city}
                cache.set(cache_key, geo_data, 86400)  # 24 hours
            except Exception:
                geo_data = {"country": "", "city": ""}

        # Save log
        RequestLog.objects.create(
            ip_address=ip,
            path=path,
            timestamp=timestamp,
            country=geo_data["country"],
            city=geo_data["city"],
        )

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
