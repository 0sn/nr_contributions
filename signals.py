from django.conf import settings
from django.contrib.sites.models import Site

from prowlpy.prowlpy import Prowl

# c.f. http://www.taylanpince.com/blog/posts/django-push-notifications-and-prowl/

def contribution_notification(sender, instance, **kwargs):
    prowl_api = Prowl(settings.PROWL_API_KEY)
    site = Site.objects.get_current()
    
    if prowl_api.verify_key():
        try:
            prowl_api.post(
                application="nameremoved.com",
                event="New Contribution",
                description=str(instance)
            )
        except Exception:
            pass