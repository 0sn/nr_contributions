from django.conf import settings
from django.contrib.sites.models import Site
from prowlpy.prowlpy import Prowl

# c.f. http://www.taylanpince.com/blog/posts/django-push-notifications-and-prowl/

import django.dispatch


def contribution_notification(sender, contribution, **kwargs):
    prowl_api = Prowl(settings.PROWL_API_KEY)
    site = Site.objects.get_current()
    
    if prowl_api.verify_key():
        try:
            prowl_api.post(
                application=site,
                event="New Contribution",
                description=str(contribution)
            )
        except Exception:
            pass

nr_contrib_added = django.dispatch.Signal(providing_args=["contribution"])

nr_contrib_added.connect(contribution_notification)
