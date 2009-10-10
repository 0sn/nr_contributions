from django.contrib import admin
from django.db import models
from models import Contribution, Contributor


class ContributionAdmin(admin.ModelAdmin):
    list_display = ('submitted', 'aka', 'contribution_type', 'content','flagged', 'contributor', 'used')
    list_display_links = ('aka','contribution_type', 'content')
    list_filter = ('flagged', 'contribution_type', 'contributor')
    list_select_related = True
    ordering = ['-submitted']
    search_fields = ['content']
    radio_fields = {
        "contribution_type": admin.VERTICAL,
        "contributor": admin.VERTICAL,
    }
    
    fieldsets = (
        (None, {
            'fields': (('aka', 'flagged'), 'content'),
        }),
        ("Info", {
            'fields': (('contribution_type', 'contributor',),),
            'classes': ('collapse',),
        }),
    )
    
    def flag_contribution(self, request, queryset):
        rows_updated = queryset.update(flagged=True)
        if rows_updated == 1:
            message_bit = "1 contribution was"
        else:
            message_bit = '%s contributions were' % rows_updated
        self.message_user(request,"%s flagged." % message_bit)
    flag_contribution.short_description = "Flag selected contributions"
    
    actions = [flag_contribution]
    
    def used(self, obj):
        """
        Returns True if there are any Comics involved with this suggestion.
        """
        return obj.comic_set.all().count() > 0
    used.boolean = True

admin.site.register(Contribution,ContributionAdmin)

class ContributorAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',),}

admin.site.register(Contributor, ContributorAdmin)
