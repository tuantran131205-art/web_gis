from django.db import models
from django.contrib.auth.models import User


# ---------------------------------------------------------------------------
# Store
# ---------------------------------------------------------------------------
class Store(models.Model):
    name = models.CharField(max_length=100, verbose_name='Tên cửa hàng')
    latitude = models.FloatField(verbose_name='Vĩ độ')
    longitude = models.FloatField(verbose_name='Kinh độ')
    description = models.TextField(blank=True, default='', verbose_name='Giới thiệu cửa hàng')
    phone_number = models.CharField(max_length=20, blank=True, default='', verbose_name='Số điện thoại')
    zalo_number = models.CharField(max_length=20, blank=True, default='', verbose_name='Số Zalo')
    address = models.CharField(max_length=255, blank=True, default='', verbose_name='Địa chỉ')

    class Meta:
        verbose_name = 'Cửa hàng'
        verbose_name_plural = 'Cửa hàng'

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# Product
# ---------------------------------------------------------------------------
class PhoneProduct(models.Model):
    STOCK_CHOICES = [
        ('in_stock', 'Còn hàng'),
        ('low_stock', 'Sắp hết hàng'),
        ('out_of_stock', 'Hết hàng'),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='phones', verbose_name='Cửa hàng')
    phone_name = models.CharField(max_length=200, verbose_name='Tên điện thoại')
    price = models.DecimalField(max_digits=15, decimal_places=0, verbose_name='Giá (VNĐ)')
    image_url = models.URLField(blank=True, null=True, verbose_name='Ảnh URL')
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='Ảnh upload')
    stock_status = models.CharField(max_length=20, choices=STOCK_CHOICES, default='in_stock', verbose_name='Tình trạng')
    description = models.TextField(blank=True, default='', verbose_name='Mô tả sản phẩm')
    specs = models.TextField(blank=True, default='', verbose_name='Thông số kỹ thuật')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Sản phẩm'
        verbose_name_plural = 'Sản phẩm'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.phone_name} - {self.store.name}"

    def get_stock_label(self):
        return dict(self.STOCK_CHOICES).get(self.stock_status, self.stock_status)

    def get_image(self):
        if self.image:
            return self.image.url
        return self.image_url or 'https://placehold.co/400x400?text=No+Image'


# ---------------------------------------------------------------------------
# Cart
# ---------------------------------------------------------------------------
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', verbose_name='Người dùng')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Giỏ hàng'
        verbose_name_plural = 'Giỏ hàng'

    def __str__(self):
        return f"Giỏ hàng của {self.user.username}"

    def get_total(self):
        return sum(item.get_subtotal() for item in self.items.all())

    def get_count(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(PhoneProduct, on_delete=models.CASCADE, verbose_name='Sản phẩm')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Số lượng')

    class Meta:
        verbose_name = 'Sản phẩm trong giỏ'
        verbose_name_plural = 'Sản phẩm trong giỏ'
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.phone_name}"

    def get_subtotal(self):
        return self.product.price * self.quantity


# ---------------------------------------------------------------------------
# Order
# ---------------------------------------------------------------------------
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('shipping', 'Đang giao'),
        ('delivered', 'Đã giao'),
        ('cancelled', 'Đã hủy'),
    ]

    PAYMENT_CHOICES = [
        ('cod', 'Thanh toán khi nhận hàng (COD)'),
        ('bank', 'Chuyển khoản ngân hàng'),
        ('momo', 'Ví MoMo'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Người đặt')
    full_name = models.CharField(max_length=100, verbose_name='Họ và tên')
    phone = models.CharField(max_length=20, verbose_name='Số điện thoại')
    address = models.TextField(verbose_name='Địa chỉ giao hàng')
    note = models.TextField(blank=True, default='', verbose_name='Ghi chú')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod', verbose_name='Phương thức thanh toán')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Trạng thái')
    total_amount = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name='Tổng tiền')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Đơn hàng'
        verbose_name_plural = 'Đơn hàng'
        ordering = ['-created_at']

    def __str__(self):
        return f"Đơn #{self.id} - {self.full_name}"

    def get_status_color(self):
        colors = {
            'pending': 'warning',
            'confirmed': 'info',
            'shipping': 'primary',
            'delivered': 'success',
            'cancelled': 'danger',
        }
        return colors.get(self.status, 'secondary')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Đơn hàng')
    product = models.ForeignKey(PhoneProduct, on_delete=models.SET_NULL, null=True, verbose_name='Sản phẩm')
    product_name = models.CharField(max_length=200, verbose_name='Tên sản phẩm')
    price = models.DecimalField(max_digits=15, decimal_places=0, verbose_name='Giá')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Số lượng')

    class Meta:
        verbose_name = 'Sản phẩm trong đơn'
        verbose_name_plural = 'Sản phẩm trong đơn'

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"

    def get_subtotal(self):
        return self.price * self.quantity
