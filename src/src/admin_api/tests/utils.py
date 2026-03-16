from django.contrib import admin
from django_admin_adapter.adapter import AdminAPIAdapter


def get_view(view_name, **kwargs):
    adapter = AdminAPIAdapter(admin.site, **kwargs)
    # we use the get_urls method of the adapter
    # in order to get the view with
    # the proper adapter instance injected
    for url in adapter.get_urls():
        if hasattr(url, "name") and url.name == view_name:
            return url.callback
    assert False, f"View with expected name '{view_name}' was not found"
