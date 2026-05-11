from django.contrib import admin
from .models import Store, PhoneProduct, Cart, CartItem, Order, OrderItem


# ---------------------------------------------------------------------------
# Store
# ---------------------------------------------------------------------------
@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'address', 'latitude', 'longitude')
    search_fields = ('name', 'phone_number', 'address')
    list_per_page = 20


# ---------------------------------------------------------------------------
# PhoneProduct
# ---------------------------------------------------------------------------
@admin.register(PhoneProduct)
class PhoneProductAdmin(admin.ModelAdmin):
    list_display = ('phone_name', 'store', 'price', 'stock_status', 'created_at')
    list_filter = ('stock_status', 'store')
    search_fields = ('phone_name', 'description')
    list_editable = ('stock_status',)
    list_per_page = 25
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('store', 'phone_name', 'price', 'stock_status')
        }),
        ('Hình ảnh', {
            'fields': ('image_url', 'image')
        }),
        ('Mô tả & Thông số', {
            'fields': ('description', 'specs'),
            'classes': ('collapse',),
        }),
    )


# ---------------------------------------------------------------------------
# Cart
# ---------------------------------------------------------------------------
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('get_subtotal',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_count', 'get_total', 'created_at')
    inlines = [CartItemInline]
    readonly_fields = ('get_total', 'get_count')


# ---------------------------------------------------------------------------
# Order
# ---------------------------------------------------------------------------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('get_subtotal',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone', 'status', 'payment_method', 'total_amount', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('full_name', 'phone', 'address')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at', 'total_amount')
    inlines = [OrderItemInline]
    list_per_page = 25
    actions = ['mark_confirmed', 'mark_shipping', 'mark_delivered', 'mark_cancelled']

    @admin.action(description='✅ Xác nhận đơn hàng')
    def mark_confirmed(self, request, queryset):
        queryset.update(status='confirmed')

    @admin.action(description='🚚 Đang giao hàng')
    def mark_shipping(self, request, queryset):
        queryset.update(status='shipping')

    @admin.action(description='📦 Đã giao hàng')
    def mark_delivered(self, request, queryset):
        queryset.update(status='delivered')

    @admin.action(description='❌ Hủy đơn hàng')
    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
