from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Store, PhoneProduct, Cart, CartItem, Order, OrderItem
from .utils import haversine, estimate_time


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _parse_float_param(raw):
    """Parse tọa độ từ GET/POST; chấp nhận dấu phẩy là dấu thập phân (locale vi)."""
    if raw is None or raw == '':
        return None
    try:
        return float(str(raw).strip().replace(',', '.'))
    except (TypeError, ValueError):
        return None


BRAND_MAP = [
    (['iphone', 'apple', 'mac'], 'apple', '🍎'),
    (['samsung', 'galaxy'], 'samsung', '🌀'),
    (['xiaomi', 'redmi'], 'xiaomi', '⚡'),
    (['oppo'], 'oppo', '🟢'),
    (['vivo'], 'vivo', '💜'),
    (['realme'], 'realme', '🔴'),
    (['nokia'], 'nokia', '🔵'),
    (['google', 'pixel'], 'google', '🔷'),
    (['huawei'], 'huawei', '🌹'),
]


def get_brand_info(phone_name):
    name = phone_name.lower()
    for keywords, brand, emoji in BRAND_MAP:
        if any(kw in name for kw in keywords):
            return brand, emoji
    return 'other', '📱'


def enrich_phones(qs):
    result = []
    for phone in qs:
        brand, emoji = get_brand_info(phone.phone_name)
        result.append({
            'phone': phone,
            'brand': brand,
            'emoji': emoji,
            'disabled': phone.stock_status == 'out_of_stock',
        })
    return result


def get_cart_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        return cart.get_count() if cart else 0
    return 0


# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------
def home(request):
    phones_raw = PhoneProduct.objects.select_related('store').all()
    phones = enrich_phones(phones_raw)
    cart_count = get_cart_count(request)
    return render(request, 'stores/home.html', {
        'phones': phones,
        'cart_count': cart_count,
    })


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------
def search(request):
    query = request.GET.get('q', '').strip()
    phones_raw = []
    if query:
        phones_raw = PhoneProduct.objects.select_related('store').filter(
            Q(phone_name__icontains=query) |
            Q(description__icontains=query) |
            Q(store__name__icontains=query)
        )
    phones = enrich_phones(phones_raw)
    cart_count = get_cart_count(request)
    return render(request, 'stores/search_results.html', {
        'phones': phones,
        'query': query,
        'cart_count': cart_count,
    })


# ---------------------------------------------------------------------------
# Product Detail
# ---------------------------------------------------------------------------
def product_detail(request, pk):
    product = get_object_or_404(PhoneProduct.objects.select_related('store'), pk=pk)
    brand, emoji = get_brand_info(product.phone_name)
    # Ưu tiên sản phẩm cùng cửa hàng; nếu không đủ thì bổ sung theo cùng thương hiệu.
    same_store_qs = PhoneProduct.objects.select_related('store').filter(store=product.store).exclude(pk=pk)
    related_raw = list(same_store_qs[:4])
    if len(related_raw) < 4:
        same_brand_qs = (
            PhoneProduct.objects.select_related('store')
            .filter(phone_name__icontains=brand)
            .exclude(pk=pk)
            .exclude(pk__in=[p.pk for p in related_raw])
        )
        related_raw.extend(list(same_brand_qs[: (4 - len(related_raw))]))
    related = enrich_phones(related_raw)
    cart_count = get_cart_count(request)
    return render(request, 'stores/product_detail.html', {
        'product': product,
        'brand': brand,
        'emoji': emoji,
        'related': related,
        'disabled': product.stock_status == 'out_of_stock',
        'cart_count': cart_count,
    })


# ---------------------------------------------------------------------------
# Cart
# ---------------------------------------------------------------------------
@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').all()
    cart_count = cart.get_count()
    return render(request, 'stores/cart.html', {
        'cart': cart,
        'items': items,
        'cart_count': cart_count,
    })


@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(PhoneProduct, pk=pk)
    if product.stock_status == 'out_of_stock':
        messages.error(request, 'Sản phẩm này đã hết hàng.')
        return redirect('product_detail', pk=pk)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
        item.save()
        messages.success(request, f'Đã cập nhật số lượng "{product.phone_name}" trong giỏ hàng!')
    else:
        messages.success(request, f'Đã thêm "{product.phone_name}" vào giỏ hàng!')

    next_url = request.POST.get('next') or request.GET.get('next') or '/'
    return redirect(next_url)


@login_required
def remove_from_cart(request, pk):
    cart = get_object_or_404(Cart, user=request.user)
    item = get_object_or_404(CartItem, cart=cart, pk=pk)
    item.delete()
    messages.success(request, 'Đã xóa sản phẩm khỏi giỏ hàng.')
    return redirect('cart')


@login_required
def update_cart(request, pk):
    if request.method == 'POST':
        cart = get_object_or_404(Cart, user=request.user)
        item = get_object_or_404(CartItem, cart=cart, pk=pk)
        qty = int(request.POST.get('quantity', 1))
        if qty < 1:
            item.delete()
            messages.info(request, 'Đã xóa sản phẩm khỏi giỏ hàng.')
        else:
            item.quantity = qty
            item.save()
            messages.success(request, 'Đã cập nhật số lượng.')
    return redirect('cart')


# ---------------------------------------------------------------------------
# Checkout & Order
# ---------------------------------------------------------------------------
@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.warning(request, 'Giỏ hàng của bạn đang trống.')
        return redirect('cart')

    items = cart.items.select_related('product').all()
    cart_count = cart.get_count()

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        note = request.POST.get('note', '').strip()
        payment_method = request.POST.get('payment_method', 'cod')

        if not full_name or not phone or not address:
            messages.error(request, 'Vui lòng điền đầy đủ thông tin giao hàng.')
            return render(request, 'stores/checkout.html', {
                'cart': cart, 'items': items, 'cart_count': cart_count,
                'full_name': full_name, 'phone': phone, 'address': address,
                'note': note, 'payment_method': payment_method,
            })

        total = cart.get_total()
        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address=address,
            note=note,
            payment_method=payment_method,
            total_amount=total,
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.phone_name,
                price=item.product.price,
                quantity=item.quantity,
            )

        # Clear cart
        cart.items.all().delete()

        messages.success(request, f'Đặt hàng thành công! Mã đơn hàng của bạn: #{order.id}')
        return redirect('payment_result', order_id=order.id)

    return render(request, 'stores/checkout.html', {
        'cart': cart,
        'items': items,
        'cart_count': cart_count,
        'payment_choices': Order.PAYMENT_CHOICES,
    })


@login_required
def payment_result(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    cart_count = get_cart_count(request)
    return render(request, 'stores/payment_result.html', {
        'order': order,
        'cart_count': cart_count,
    })


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    cart_count = get_cart_count(request)
    return render(request, 'stores/my_orders.html', {
        'orders': orders,
        'cart_count': cart_count,
    })


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Chào mừng {user.username}! Đăng ký thành công.')
            return redirect('home')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin.')
    else:
        form = UserCreationForm()
    return render(request, 'stores/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Chào mừng trở lại, {user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng.')
    else:
        form = AuthenticationForm()
    return render(request, 'stores/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Bạn đã đăng xuất.')
    return redirect('home')


# ---------------------------------------------------------------------------
# GIS: Find Nearest Store
# ---------------------------------------------------------------------------
def find_nearest(request):
    nearest = []
    user_lat = None
    user_lng = None

    stores_qs = Store.objects.prefetch_related('phones').all()

    if not stores_qs.exists():
        return render(request, 'stores/find.html', {
            'nearest': [], 'user_lat': None, 'user_lng': None,
            'target_store_lat': None, 'target_store_lng': None,
        })

    if request.method == 'GET' and request.GET.get('lat') and request.GET.get('lng'):
        user_lat = _parse_float_param(request.GET.get('lat'))
        user_lng = _parse_float_param(request.GET.get('lng'))
    elif request.method == 'POST':
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')
        if not lat or not lng:
            return render(request, 'stores/find.html', {
                'nearest': [], 'user_lat': None, 'user_lng': None,
                'target_store_lat': None, 'target_store_lng': None,
                'error': 'Không lấy được vị trí',
            })
        user_lat = _parse_float_param(lat)
        user_lng = _parse_float_param(lng)

    if user_lat is not None and user_lng is not None:
        stores_with_distance = []
        for store in stores_qs:
            dist = haversine(user_lat, user_lng, store.latitude, store.longitude)
            time = estimate_time(dist)
            stores_with_distance.append((store, dist, time))
        stores_with_distance.sort(key=lambda x: x[1])
        nearest = [item for item in stores_with_distance if item[1] <= 20][:10]
        if not nearest:
            nearest = stores_with_distance[:5]

    target_store_lat = None
    target_store_lng = None
    store_lat_param = request.GET.get('store_lat')
    store_lng_param = request.GET.get('store_lng')
    if store_lat_param and store_lng_param:
        target_store_lat = _parse_float_param(store_lat_param)
        target_store_lng = _parse_float_param(store_lng_param)

    if target_store_lat is None or target_store_lng is None:
        if nearest:
            target_store_lat = nearest[0][0].latitude
            target_store_lng = nearest[0][0].longitude
        else:
            first_store = stores_qs.first()
            if first_store:
                target_store_lat = first_store.latitude
                target_store_lng = first_store.longitude

    cart_count = get_cart_count(request)
    return render(request, 'stores/find.html', {
        'nearest': nearest,
        'user_lat': user_lat,
        'user_lng': user_lng,
        'target_store_lat': target_store_lat,
        'target_store_lng': target_store_lng,
        'cart_count': cart_count,
    })
