from django.contrib import admin
from .models import Template, Subscription, DependencyClosure
from .forms import TemplateForm

class TemplateAdmin(admin.ModelAdmin):
    form = TemplateForm
    list_display = ('__unicode__','is_public','is_default','depends_on', 'dependencies_set', 'cached_dependencies_set')

admin.site.register(Template, TemplateAdmin)
admin.site.register(Subscription)
admin.site.register(DependencyClosure)