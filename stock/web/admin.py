from django.contrib import admin
from django.apps import apps

# Register your models here.
post_models = apps.get_app_config('web').get_models()

for model in post_models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass