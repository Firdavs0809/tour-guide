from django.contrib import admin
from .models import TourPackage, Language, Company, City, Destination, Activity, Feature, Hotel, Country, TempCompany, \
    Category, Options, Booking

admin.site.register(TourPackage)
admin.site.register(Language)
admin.site.register(Company)
admin.site.register(Destination)
admin.site.register(Activity)
admin.site.register(Feature)
admin.site.register(Hotel)
admin.site.register(TempCompany)
admin.site.register(Category)
admin.site.register(Options)
admin.site.register(Booking)


class CountryModelAdmin(admin.ModelAdmin):
    search_fields = ['name']


class CityModelAdmin(admin.ModelAdmin):
    search_fields = ['name']


admin.site.register(Country, CountryModelAdmin)
admin.site.register(City, CityModelAdmin)
