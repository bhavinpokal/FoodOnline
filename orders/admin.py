from django.contrib import admin

from orders.models import Payment, Order, OrderFood


class OrderFoodInline(admin.TabularInline):
    model = OrderFood
    readonly_fields = ('order', 'payment', 'user',
                       'fooditem', 'quantity', 'price', 'amount')
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'name', 'phone', 'email',
                    'total', 'payment_method', 'status', 'is_ordered']
    inlines = [OrderFoodInline]


admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderFood)
