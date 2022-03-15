from django.contrib import admin

# Register your models here.
from public_housing.models import Account, Watchlist


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'description')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}
