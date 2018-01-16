from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from main import models
from django.core import urlresolvers
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from nested_inline.admin import NestedModelAdmin, NestedTabularInline
from django import forms


class BuildingFileInline(admin.TabularInline):
    model = models.BuildingFile
    extra=1

class BuildingPhotoAdmin(admin.ModelAdmin):
    fields = ["building","image",]
    list_display = ("building","image","image_thm")

    def building_link(self, obj):
        if obj.building is None:
            return _('No associated building')
        url = urlresolvers.reverse(
            'admin:main_building_change', args=(obj.building.id,))
        return format_html(u'<a href={}>{}</a>', mark_safe(url), obj.building)
    building_link.short_description = _('link to the building')
    readonly_fields = ('building_link',"image_thm",)


class BuildingPhotoInline(admin.TabularInline):
    model = models.BuildingPhoto
    extra = 1
    readonly_fields = ('image_thm',)

    def image_thm(self,obj):
        if obj.image_thumbnail:
            return format_html(
                u'<a href="{}" target="blank" /><img src="{}" /></a>',
                obj.image.url, obj.image_thumbnail.url)
        else:
            return ''


class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name', 'property_count')
    inlines = [BuildingPhotoInline]


class PropertyFileInline(admin.TabularInline):
    model = models.PropertyFile
    extra = 1
    def get_extra (self, request, obj=None, **kwargs):
        """Dynamically sets the number of extra forms. 0 if the related object
        already exists or the extra configuration otherwise."""
        if obj:
            # Don't add any extra forms if the related object already exists.
            return 0
        return self.extra
class ProperyPayableInline(admin.TabularInline):
    model = models.PropertyPayable
    extra = 1


class UtilityFileInline(admin.TabularInline):
    model = models.Utility
    extra = 3
    def get_extra (self, request, obj=None, **kwargs):
        """Dynamically sets the number of extra forms. 0 if the related object
        already exists or the extra configuration otherwise."""
        if obj:
            # Don't add any extra forms if the related object already exists.
            return 0
        return self.extra

class PropertyPhotoInline(admin.TabularInline):
    model = models.PropertyPhoto
    readonly_fields = ("image_thm",)
    extra = 0
#    fk_name = 'room'
    def image_thm(self,obj):
        if obj.image_thumbnail:
            return format_html(
                u'<a href="{}" target="blank" /><img src="{}" /></a>',
                obj.image.url, obj.image_thumbnail.url)
        else:
            return ''


class RoomInline(NestedTabularInline):
    model = models.Room
 #   inlines = [RoomPhotoInline]
#    fk_name = 'property'
    extra = 2
    def get_extra (self, request, obj=None, **kwargs):
        """Dynamically sets the number of extra forms. 0 if the related object
        already exists or the extra configuration otherwise."""
        if obj:
            # Don't add any extra forms if the related object already exists.
            return 0
        return self.extra
class InventoryInline(admin.TabularInline):
    model = models.Inventory
    extra =1


class PropertyAdmin(NestedModelAdmin):
    model = models.Property
    list_display = ('name', 'address', 'building', 'plan_thm')
    inlines = [PropertyPhotoInline,RoomInline,InventoryInline,UtilityFileInline,ProperyPayableInline,PropertyFileInline]

    def building_link(self, obj):
        if obj.building is None:
            return _('No associated building')
        url = urlresolvers.reverse(
            'admin:main_building_change', args=(obj.building.id,))
        return format_html(u'<a href={}>{}</a>', mark_safe(url), obj.building)
    building_link.short_description = _('link to the building')
    readonly_fields = ('building_link',)
    class Media:
        css = {
            'all': (
                'main/css/admin.css',
            )
        }


class RentRevisionInline(admin.TabularInline):
    model = models.RentRevision
    extra = 1


class TenantFileInline(admin.TabularInline):
    model = models.TenantFile
    extra = 1


class PaymentInline(admin.TabularInline):
    model = models.Payment


class RefundInline(admin.TabularInline):
    model = models.Refund

class FeeInline(admin.TabularInline):
    model = models.Fee
    extra = 1


class DiscountInline(admin.TabularInline):
    model = models.Discount
    extra = 1


class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'balance')
    inlines = [
        RentRevisionInline,
        FeeInline,
        DiscountInline,
        TenantFileInline,
        PaymentInline,
        RefundInline,
    ]
    readonly_fields = ('property_link', 'balance',)

    def property_link(self, obj):
        url = urlresolvers.reverse(
            'admin:main_property_change', args=(obj.property.id,))
        return format_html(u'<a href={}>{}</a>', mark_safe(url), obj.property)
    property_link.short_description = _('link to the property')


# This is a hack to have 2 displays for the tenants
class TenantReminders(models.Tenant):
    class Meta:
        proxy = True
        verbose_name = _("tenant reminder list")
        verbose_name_plural = _("tenants reminder lists")



class ReminderInline(admin.TabularInline):
    fields = ['date', 'read', 'text']
    model = models.Reminder
    extra = 1


class TenantRemindersAdmin(admin.ModelAdmin):
    fields = ('name', 'property')
    readonly_fields = ('name', 'property')
    inlines = [
        ReminderInline,
    ]



admin.site.register(models.Building, BuildingAdmin)
admin.site.register(models.BuildingPhoto, BuildingPhotoAdmin)
admin.site.register(models.Property, PropertyAdmin)
admin.site.register(models.Tenant, TenantAdmin)
admin.site.register(TenantReminders, TenantRemindersAdmin)
