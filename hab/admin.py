from django.contrib import admin
from hab.models import *

class AssignmentTemplateAdmin(admin.ModelAdmin):
    def make_instance(self, request, queryset):
        for t in queryset.all():
            new, ass = t.instanciate()
            if new:
                ass.owner = request.user
                ass.save()
    make_instance.short_description = "Create new instances of the selected templates"
    actions = [make_instance]

admin.site.register(Verb)
admin.site.register(Assignment)
admin.site.register(AssignmentTemplate, AssignmentTemplateAdmin)
admin.site.register(AssignmentView)

