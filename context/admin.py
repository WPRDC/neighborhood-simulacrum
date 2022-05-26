from django.contrib import admin

from context.models import Tag, ContextItem


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'id')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ContextItem)
class ContextAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'level', 'id')
    search_fields = ('name', 'text',)
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ('tags',)
