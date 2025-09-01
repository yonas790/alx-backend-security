from celery import shared_task
from django.utils.timezone import now, timedelta
from ip_tracking.models import RequestLog, SuspiciousIP

SENSITIVE_PATHS = ["/admin", "/login"]
REQUEST_THRESHOLD = 100  # requests per hour


@shared_task
def detect_suspicious_ips():
    """
    Flags IPs that either:
      1) Made more than REQUEST_THRESHOLD requests in the last hour
      2) Accessed sensitive paths (/admin, /login)
    """
    one_hour_ago = now() - timedelta(hours=1)
    logs = RequestLog.objects.filter(timestamp__gte=one_hour_ago)

    # Track request counts per IP
    ip_counts = {}
    for log in logs:
        ip_counts[log.ip_address] = ip_counts.get(log.ip_address, 0) + 1

        # Sensitive paths
        if log.path in SENSITIVE_PATHS:
            SuspiciousIP.objects.get_or_create(
                ip_address=log.ip_address,
                reason=f"Accessed sensitive path: {log.path}"
            )

    # Check request threshold
    for ip, count in ip_counts.items():
        if count > REQUEST_THRESHOLD:
            SuspiciousIP.objects.get_or_create(
                ip_address=ip,
                reason=f"Exceeded {REQUEST_THRESHOLD} requests in the last hour"
            )
