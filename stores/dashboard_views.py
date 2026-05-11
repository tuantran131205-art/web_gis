from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import Store, PhoneProduct, Order, OrderItem


def _parse_coord(value, default=0.0):
    raw = (value or '').strip()
    if raw == '':
        return default
    try:
        return float(raw.replace(',', '.'))
    except (TypeError, ValueError):
        raise ValueError('Tọa độ không hợp lệ.')


def dashboard_required(view_func):
    """Only staff/superuser can access dashboard."""
    return staff_member_required(view_func, login_url='/login/')


# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------
@dashboard_required
def dashboard_home(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    total_products = PhoneProduct.objects.count()
    total_stores = Store.objects.count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()

    revenue_total = Order.objects.filter(
        status__in=['confirmed', 'shipping', 'delivered']
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    revenue_month = Order.objects.filter(
        status__in=['confirmed', 'shipping', 'delivered'],
        created_at__date__gte=month_start,
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:8]

    status_counts = {
        'pending': Order.objects.filter(status='pending').count(),
        'confirmed': Order.objects.filter(status='confirmed').count(),
        'shipping': Order.objects.filter(status='shipping').count(),
        'delivered': Order.objects.filter(status='delivered').count(),
        'cancelled': Order.objects.filter(status='cancelled').count(),
    }

    low_stock = PhoneProduct.objects.filter(stock_status='low_stock').count()
    out_of_stock = PhoneProduct.objects.filter(stock_status='out_of_stock').count()

    # --- Chart: last 7 days revenue & orders ---
    labels, daily_revenue, daily_orders = [], [], []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        labels.append(day.strftime('%d/%m'))
        rev = Order.objects.filter(
            created_at__date=day,
            status__in=['confirmed', 'shipping', 'delivered']
        ).aggregate(t=Sum('total_amount'))['t'] or 0
        cnt = Order.objects.filter(created_at__date=day).count()
        daily_revenue.append(float(rev))
        daily_orders.append(cnt)

    # Top 5 products sold
    top_products = list(
        OrderItem.objects
        .values('product_name')
        .annotate(total_qty=Sum('quantity'))
        .order_by('-total_qty')[:5]
    )

    return render(request, 'stores/dashboard/home.html', {
        'total_products': total_products,
        'total_stores': total_stores,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'revenue_total': revenue_total,
        'revenue_month': revenue_month,
        'recent_orders': recent_orders,
        'status_counts': status_counts,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'chart_labels': labels,
        'chart_revenue': daily_revenue,
        'chart_orders': daily_orders,
        'top_products': top_products,
    })


# ---------------------------------------------------------------------------
# Stores CRUD
# ---------------------------------------------------------------------------
@dashboard_required
def store_list(request):
    q = request.GET.get('q', '')
    stores = Store.objects.annotate(product_count=Count('phones'))
    if q:
        stores = stores.filter(Q(name__icontains=q) | Q(address__icontains=q))
    return render(request, 'stores/dashboard/store_list.html', {
        'stores': stores, 'q': q,
    })


@dashboard_required
def store_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        latitude = request.POST.get('latitude', '').strip()
        longitude = request.POST.get('longitude', '').strip()
        address = request.POST.get('address', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        zalo_number = request.POST.get('zalo_number', '').strip()
        description = request.POST.get('description', '').strip()

        if not name:
            messages.error(request, 'Vui lòng nhập tên cửa hàng.')
        else:
            try:
                Store.objects.create(
                    name=name,
                    latitude=_parse_coord(latitude, default=0.0),
                    longitude=_parse_coord(longitude, default=0.0),
                    address=address,
                    phone_number=phone_number,
                    zalo_number=zalo_number,
                    description=description,
                )
                messages.success(request, f'Đã tạo cửa hàng "{name}".')
                return redirect('dashboard_store_list')
            except ValueError:
                messages.error(request, 'Tọa độ không hợp lệ.')
    return render(request, 'stores/dashboard/store_form.html', {'action': 'Thêm mới', 'store': None})


@dashboard_required
def store_edit(request, pk):
    store = get_object_or_404(Store, pk=pk)
    if request.method == 'POST':
        store.name = request.POST.get('name', '').strip()
        store.address = request.POST.get('address', '').strip()
        store.phone_number = request.POST.get('phone_number', '').strip()
        store.zalo_number = request.POST.get('zalo_number', '').strip()
        store.description = request.POST.get('description', '').strip()
        try:
            # Cho phép để trống: giữ nguyên tọa độ hiện tại nếu user không muốn cập nhật.
            store.latitude = _parse_coord(request.POST.get('latitude'), default=store.latitude)
            store.longitude = _parse_coord(request.POST.get('longitude'), default=store.longitude)
            store.save()
            messages.success(request, f'Đã cập nhật "{store.name}".')
            return redirect('dashboard_store_list')
        except ValueError as exc:
            messages.error(request, str(exc))
    return render(request, 'stores/dashboard/store_form.html', {'action': 'Chỉnh sửa', 'store': store})


@dashboard_required
def store_delete(request, pk):
    store = get_object_or_404(Store, pk=pk)
    if request.method == 'POST':
        name = store.name
        store.delete()
        messages.success(request, f'Đã xóa cửa hàng "{name}".')
        return redirect('dashboard_store_list')
    return render(request, 'stores/dashboard/confirm_delete.html', {
        'object': store, 'object_name': store.name, 'back_url': 'dashboard_store_list',
    })


# ---------------------------------------------------------------------------
# Products CRUD
# ---------------------------------------------------------------------------
@dashboard_required
def product_list(request):
    q = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    store_filter = request.GET.get('store', '')

    products = PhoneProduct.objects.select_related('store').all()
    if q:
        products = products.filter(Q(phone_name__icontains=q) | Q(store__name__icontains=q))
    if status_filter:
        products = products.filter(stock_status=status_filter)
    if store_filter:
        products = products.filter(store_id=store_filter)

    stores = Store.objects.all()
    return render(request, 'stores/dashboard/product_list.html', {
        'products': products, 'stores': stores,
        'q': q, 'status_filter': status_filter, 'store_filter': store_filter,
    })


@dashboard_required
def product_create(request):
    stores = Store.objects.all()
    if request.method == 'POST':
        phone_name = request.POST.get('phone_name', '').strip()
        store_id = request.POST.get('store_id')
        price = request.POST.get('price', '').strip()
        stock_status = request.POST.get('stock_status', 'in_stock')
        image_url = request.POST.get('image_url', '').strip()
        description = request.POST.get('description', '').strip()
        specs = request.POST.get('specs', '').strip()

        if not phone_name or not store_id or not price:
            messages.error(request, 'Vui lòng nhập đầy đủ thông tin bắt buộc.')
        else:
            try:
                store = get_object_or_404(Store, pk=store_id)
                PhoneProduct.objects.create(
                    phone_name=phone_name,
                    store=store,
                    price=int(price),
                    stock_status=stock_status,
                    image_url=image_url or None,
                    description=description,
                    specs=specs,
                )
                messages.success(request, f'Đã thêm sản phẩm "{phone_name}".')
                return redirect('dashboard_product_list')
            except (ValueError, TypeError):
                messages.error(request, 'Giá không hợp lệ.')
    return render(request, 'stores/dashboard/product_form.html', {
        'action': 'Thêm mới', 'product': None, 'stores': stores,
        'stock_choices': PhoneProduct.STOCK_CHOICES,
    })


@dashboard_required
def product_edit(request, pk):
    product = get_object_or_404(PhoneProduct.objects.select_related('store'), pk=pk)
    stores = Store.objects.all()
    if request.method == 'POST':
        product.phone_name = request.POST.get('phone_name', '').strip()
        product.stock_status = request.POST.get('stock_status', product.stock_status)
        product.image_url = request.POST.get('image_url', '').strip() or None
        product.description = request.POST.get('description', '').strip()
        product.specs = request.POST.get('specs', '').strip()
        store_id = request.POST.get('store_id')
        try:
            product.price = int(request.POST.get('price', product.price))
            if store_id:
                product.store = get_object_or_404(Store, pk=store_id)
            product.save()
            messages.success(request, f'Đã cập nhật "{product.phone_name}".')
            return redirect('dashboard_product_list')
        except (ValueError, TypeError):
            messages.error(request, 'Giá không hợp lệ.')
    return render(request, 'stores/dashboard/product_form.html', {
        'action': 'Chỉnh sửa', 'product': product, 'stores': stores,
        'stock_choices': PhoneProduct.STOCK_CHOICES,
    })


@dashboard_required
def product_delete(request, pk):
    product = get_object_or_404(PhoneProduct, pk=pk)
    if request.method == 'POST':
        name = product.phone_name
        product.delete()
        messages.success(request, f'Đã xóa sản phẩm "{name}".')
        return redirect('dashboard_product_list')
    return render(request, 'stores/dashboard/confirm_delete.html', {
        'object': product, 'object_name': product.phone_name, 'back_url': 'dashboard_product_list',
    })


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------
@dashboard_required
def order_list(request):
    q = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    orders = Order.objects.select_related('user').prefetch_related('items').all()
    if q:
        orders = orders.filter(Q(full_name__icontains=q) | Q(phone__icontains=q))
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'stores/dashboard/order_list.html', {
        'orders': orders, 'q': q, 'status_filter': status_filter,
        'status_choices': Order.STATUS_CHOICES,
    })


@dashboard_required
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related('items__product'), pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Đã cập nhật trạng thái đơn #{order.id}.')
            return redirect('dashboard_order_detail', pk=pk)
    return render(request, 'stores/dashboard/order_detail.html', {
        'order': order, 'status_choices': Order.STATUS_CHOICES,
    })


@dashboard_required
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.delete()
        messages.success(request, f'Đã xóa đơn hàng #{pk}.')
        return redirect('dashboard_order_list')
    return render(request, 'stores/dashboard/confirm_delete.html', {
        'object': order, 'object_name': f'Đơn hàng #{order.id} - {order.full_name}',
        'back_url': 'dashboard_order_list',
    })
