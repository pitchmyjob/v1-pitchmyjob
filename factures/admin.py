from django.contrib import admin
from .models import Facture, PaymentLink

class FactureAdmin(admin.ModelAdmin):
	list_display = ('email', 'first_name', 'last_name', 'designation', 'prix_ttc', 'paid')


class PaymentLinkAdmin(admin.ModelAdmin):
	list_display = ('designation', 'prix_ht', 'paid')
	readonly_fields=('link',)

	class Media:
		js = ('/static/js/admin/payment_link.js',)

admin.site.register(Facture, FactureAdmin)
admin.site.register(PaymentLink, PaymentLinkAdmin)