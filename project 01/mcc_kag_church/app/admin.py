from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import ContactMessage, FirstTimeVisitor

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'status_badge', 'created_at', 'actions_column')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20
    
    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'phone', 'subject', 'message')
        }),
        ('Status', {
            'fields': ('status', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_resolved', 'mark_as_in_progress', 'delete_selected']
    
    def status_badge(self, obj):
        color_map = {
            'new': 'blue',
            'in_progress': 'orange',
            'resolved': 'green'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 10px;">{}</span>',
            color_map.get(obj.status, 'gray'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def actions_column(self, obj):
        return format_html(
            '<a href="{}" class="button">Edit</a> '
            '<a href="{}" class="button" style="background-color: #ba2121">Delete</a>',
            reverse('admin:app_contactmessage_change', args=[obj.id]),
            reverse('admin:app_contactmessage_delete', args=[obj.id])
        )
    actions_column.short_description = 'Actions'
    
    def mark_as_resolved(self, request, queryset):
        queryset.update(status='resolved')
    mark_as_resolved.short_description = "Mark selected as resolved"
    
    def mark_as_in_progress(self, request, queryset):
        queryset.update(status='in_progress')
    mark_as_in_progress.short_description = "Mark selected as in progress"

class FirstTimeVisitorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'visit_date', 'created_at', 'actions_column')
    list_filter = ('visit_date', 'created_at')
    search_fields = ('name', 'email', 'phone', 'address', 'how_heard')
    readonly_fields = ('created_at',)
    list_per_page = 20
    
    fieldsets = (
        ('Visitor Info', {
            'fields': ('name', 'email', 'phone', 'address', 'how_heard')
        }),
        ('Visit Details', {
            'fields': ('visit_date', 'questions')
        }),
        ('System Info', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['export_as_csv', 'delete_selected']
    
    def actions_column(self, obj):
        return format_html(
            '<a href="{}" class="button">Edit</a> '
            '<a href="{}" class="button" style="background-color: #ba2121">Delete</a>',
            reverse('admin:app_firsttimevisitor_change', args=[obj.id]),
            reverse('admin:app_firsttimevisitor_delete', args=[obj.id])
        )
    actions_column.short_description = 'Actions'
    
    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        from io import StringIO
        
        f = StringIO()
        writer = csv.writer(f)
        writer.writerow(['Name', 'Email', 'Phone', 'Address', 'Visit Date', 'How Heard', 'Questions', 'Created At'])
        
        for obj in queryset:
            writer.writerow([
                obj.name,
                obj.email,
                obj.phone,
                obj.address,
                obj.visit_date.strftime('%Y-%m-%d'),
                obj.how_heard,
                obj.questions,
                obj.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        f.seek(0)
        response = HttpResponse(f, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=visitors_export.csv'
        return response
    export_as_csv.short_description = "Export selected as CSV"

admin.site.register(ContactMessage, ContactMessageAdmin)
admin.site.register(FirstTimeVisitor, FirstTimeVisitorAdmin)