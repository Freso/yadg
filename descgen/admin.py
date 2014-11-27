from django.contrib import admin
from .models import Template, Subscription, DependencyClosure, Settings
from .forms import TemplateAdminForm, SettingsAdminForm


class TemplateAdmin(admin.ModelAdmin):
    form = TemplateAdminForm
    list_display = ('name', 'owner', 'is_public', 'is_default', 'is_utility', 'depends_on', 'dependencies_set', 'cached_dependencies_set')


class SettingsAdmin(admin.ModelAdmin):
    form = SettingsAdminForm

admin.site.register(Template, TemplateAdmin)
admin.site.register(Subscription)
admin.site.register(DependencyClosure)
admin.site.register(Settings, SettingsAdmin)