import datetime
from .models import RequestLog

class IPLoggingMiddleware:
    """
    Middleware that logs the IP address, timestamp, and path of each incoming request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get client IP
        ip_address = self.get_client_ip(request)

        # Log to DB
        RequestLog.objects.create(
            ip_address=ip_address,
            timestamp=datetime.datetime.now(),
            path=request.path
        )

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """Extract client IP address considering proxy headers."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
