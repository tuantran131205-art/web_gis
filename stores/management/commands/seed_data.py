"""
Management command: python manage.py seed_data
Seeds the database with sample stores, products, and a demo user.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from stores.models import Store, PhoneProduct
import decimal


STORES = [
    {
        'name': 'PhoneStore Quận 1',
        'latitude': 10.7769,
        'longitude': 106.7009,
        'description': 'Cửa hàng chính tại trung tâm TP.HCM',
        'phone_number': '0901234567',
        'zalo_number': '0901234567',
        'address': '123 Nguyễn Huệ, Quận 1, TP.HCM',
    },
    {
        'name': 'PhoneStore Thủ Đức',
        'latitude': 10.8498,
        'longitude': 106.7717,
        'description': 'Chi nhánh khu vực Thủ Đức - Bình Dương',
        'phone_number': '0912345678',
        'zalo_number': '0912345678',
        'address': '456 Võ Văn Ngân, Thủ Đức, TP.HCM',
    },
    {
        'name': 'PhoneStore Bình Thạnh',
        'latitude': 10.8031,
        'longitude': 106.7141,
        'description': 'Chi nhánh Bình Thạnh - Gò Vấp',
        'phone_number': '0923456789',
        'zalo_number': '0923456789',
        'address': '789 Bạch Đằng, Bình Thạnh, TP.HCM',
    },
]

PRODUCTS = [
    # iPhone
    {
        'phone_name': 'iPhone 16 Pro Max 256GB',
        'price': decimal.Decimal('34990000'),
        'stock_status': 'in_stock',
        'image_url': 'https://cdn.tgdd.vn/Products/Images/42/329149/iphone-16-pro-max-titan-tu-nhien-1.jpg',
        'description': 'iPhone 16 Pro Max với chip A18 Pro, camera 48MP, màn hình 6.9 inch Super Retina XDR.',
        'specs': 'Màn hình: 6.9 inch OLED\nChip: A18 Pro\nRAM: 8GB\nBộ nhớ: 256GB\nCamera: 48MP + 12MP + 12MP\nPin: 4685 mAh\nHệ điều hành: iOS 18',
        'store_index': 0,
    },
    {
        'phone_name': 'iPhone 15 128GB',
        'price': decimal.Decimal('19990000'),
        'stock_status': 'in_stock',
        'image_url': 'https://cdn.tgdd.vn/Products/Images/42/299033/iphone-15-den-1.jpg',
        'description': 'iPhone 15 với Dynamic Island, chip A16 Bionic, cổng USB-C.',
        'specs': 'Màn hình: 6.1 inch OLED\nChip: A16 Bionic\nRAM: 6GB\nBộ nhớ: 128GB\nCamera: 48MP + 12MP\nPin: 3877 mAh\nHệ điều hành: iOS 17',
        'store_index': 0,
    },
    {
        'phone_name': 'iPhone 14 Plus 128GB',
        'price': decimal.Decimal('15990000'),
        'stock_status': 'low_stock',
        'image_url': 'https://cdn.tgdd.vn/Products/Images/42/247508/iphone-14-plus-tim-thumb-600x600.jpg',
        'description': 'iPhone 14 Plus màn hình lớn 6.7 inch, pin siêu bền.',
        'specs': 'Màn hình: 6.7 inch OLED\nChip: A15 Bionic\nRAM: 6GB\nBộ nhớ: 128GB\nCamera: 12MP + 12MP\nPin: 4325 mAh',
        'store_index': 1,
    },
    # Samsung
    {
        'phone_name': 'Samsung Galaxy S25 Ultra 256GB',
        'price': decimal.Decimal('31990000'),
        'stock_status': 'in_stock',
        'image_url': 'https://cdn.tgdd.vn/Products/Images/42/328770/samsung-galaxy-s25-ultra-titanium-silverblue-thumb-600x600.jpg',
        'description': 'Galaxy S25 Ultra với S Pen, chip Snapdragon 8 Elite, camera 200MP.',
        'specs': 'Màn hình: 6.9 inch LTPO AMOLED\nChip: Snapdragon 8 Elite\nRAM: 12GB\nBộ nhớ: 256GB\nCamera: 200MP + 50MP + 10MP + 10MP\nPin: 5000 mAh\nHệ điều hành: Android 15, One UI 7',
        'store_index': 0,
    },
    {
        'phone_name': 'Samsung Galaxy A55 5G 256GB',
        'price': decimal.Decimal('8990000'),
        'stock_status': 'in_stock',
        'image_url': 'https://cdn.tgdd.vn/Products/Images/42/320891/samsung-galaxy-a55-5g-xanh-thumb-600x600.jpg',
        'description': 'Galaxy A55 5G với màn hình Super AMOLED, camera 50MP, vỏ nhôm cao cấp.',
        'specs': 'Màn hình: 6.6 inch Super AMOLED\nChip: Exynos 1480\nRAM: 8GB\nBộ nhớ: 256GB\nCamera: 50MP + 12MP + 5MP\nPin: 5000 mAh',
        'store_index': 1,
    },
    {
        'phone_name': 'Samsung Galaxy Z Fold 6 512GB',
        'price': decimal.Decimal('41990000'),
        'stock_status': 'out_of_stock',
        'image_url': 'https://cdn.tgdd.vn/Products/Images/42/327074/samsung-z-fold6-xanh-thumb-600x600.jpg',
        'description': 'Điện thoại màn hình gập Galaxy Z Fold 6, chip Snapdragon 8 Gen 3.',
        'specs': 'Màn hình chính: 7.6 inch\nMàn hình phụ: 6.3 inch\nChip: Snapdragon 8 Gen 3\nRAM: 12GB\nBộ nhớ: 512GB\nPin: 4400 mAh',
        'store_index': 2,
    },
    # Xiaomi
    {
        'phone_name': 'Xiaomi 14 Ultra 512GB',
        'price': decimal.Decimal('27990000'),
        'stock_status': 'in_stock',
        'image_url': 'https://cdn.tgdd.vn/Products/Images/42/316993/xiaomi-14-ultra-den-thumb-600x600.jpg',
        'description': 'Xiaomi 14 Ultra camera Leica, Snapdragon 8 Gen 3, sạc nhanh 90W.',
        'specs': 'Màn hình: 6.73 inch LTPO AMOLED\nChip: Snapdragon 8 Gen 3\nRAM: 16GB\nBộ nhớ: 512GB\nCamera: 50MP x4 (Leica)\nPin: 5000 mAh',
        'store_index': 0,
    },
    {
        'phone_name': 'Redmi Note 13 Pro+ 256GB',
        'price': decimal.Decimal('7490000'),
        'stock_status': 'in_stock',
        'image_url': 'https://cdn.tgdd.vn/Products/Images/42/315898/redmi-note-13-pro-plus-trang-bong-thumb-600x600.jpg',
        'description': 'Redmi Note 13 Pro+ với camera 200MP, sạc nhanh 120W, màn hình cong.',
        'specs': 'Màn hình: 6.67 inch AMOLED cong\nChip: Dimensity 7200 Ultra\nRAM: 8GB\nBộ nhớ: 256GB\nCamera: 200MP + 8MP + 2MP\nPin: 5000 mAh',
        'store_index': 1,
    },
    # OPPO
    {
        'phone_name': 'OPPO Find X8 Pro 256GB',
        'price': decimal.Decimal('29990000'),
        'stock_status': 'in_stock',
        'image_url': 'https://cdn.tgdd.vn/Products/Images/42/327048/oppo-find-x8-pro-thumb-600x600.jpg',
        'description': 'OPPO Find X8 Pro camera Hasselblad, Dimensity 9400, sạc không dây 50W.',
        'specs': 'Màn hình: 6.82 inch LTPO AMOLED\nChip: Dimensity 9400\nRAM: 12GB\nBộ nhớ: 256GB\nCamera: 50MP + 50MP + 50MP (Hasselblad)\nPin: 5910 mAh',
        'store_index': 2,
    },
    {
        'phone_name': 'OPPO Reno 12 Pro 512GB',
        'price': decimal.Decimal('10990000'),
        'stock_status': 'in_stock',
        'image_url': 'https://cdn.tgdd.vn/Products/Images/42/324000/oppo-reno-12-pro-xanh-thumb-600x600.jpg',
        'description': 'OPPO Reno 12 Pro với thiết kế mỏng đẹp, camera AI, sạc nhanh 80W.',
        'specs': 'Màn hình: 6.7 inch AMOLED\nChip: Dimensity 7300 Energy\nRAM: 12GB\nBộ nhớ: 512GB\nCamera: 50MP + 8MP + 2MP\nPin: 5000 mAh',
        'store_index': 0,
    },
    # Vivo
    {
        'phone_name': 'Vivo X200 Pro 512GB',
        'price': decimal.Decimal('28990000'),
        'stock_status': 'in_stock',
        'image_url': 'https://cdn.tgdd.vn/Products/Images/42/329010/vivo-x200-pro-xanh-la-thumb-600x600.jpg',
        'description': 'Vivo X200 Pro camera Zeiss, Dimensity 9400, pin 6000 mAh.',
        'specs': 'Màn hình: 6.78 inch LTPO AMOLED\nChip: Dimensity 9400\nRAM: 16GB\nBộ nhớ: 512GB\nCamera: 50MP + 200MP + 50MP (Zeiss)\nPin: 6000 mAh',
        'store_index': 1,
    },
    # Realme
    {
        'phone_name': 'Realme GT 7 Pro 512GB',
        'price': decimal.Decimal('16990000'),
        'stock_status': 'low_stock',
        'image_url': 'https://cdn.tgdd.vn/Products/Images/42/328986/realme-gt-7-pro-xanh-la-thumb-600x600.jpg',
        'description': 'Realme GT 7 Pro với Snapdragon 8 Elite, pin 6500 mAh, sạc 120W.',
        'specs': 'Màn hình: 6.78 inch OLED\nChip: Snapdragon 8 Elite\nRAM: 12GB\nBộ nhớ: 512GB\nCamera: 50MP + 8MP + 50MP\nPin: 6500 mAh',
        'store_index': 2,
    },
]


class Command(BaseCommand):
    help = 'Seed database with sample stores and products'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding database...')

        # Create superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@phonestore.vn', 'admin123')
            self.stdout.write(self.style.SUCCESS('✅ Superuser created: admin / admin123'))
        else:
            self.stdout.write('⚠️  Superuser "admin" already exists, skipping.')

        # Create demo user
        if not User.objects.filter(username='demo').exists():
            User.objects.create_user('demo', 'demo@phonestore.vn', 'demo1234')
            self.stdout.write(self.style.SUCCESS('✅ Demo user created: demo / demo1234'))

        # Create stores
        store_objs = []
        for s in STORES:
            store, created = Store.objects.get_or_create(
                name=s['name'],
                defaults=s,
            )
            store_objs.append(store)
            status = '✅ Created' if created else '⚠️  Exists'
            self.stdout.write(f'{status}: Store "{store.name}"')

        # Create products
        count = 0
        for p in PRODUCTS:
            store = store_objs[p.pop('store_index')]
            product, created = PhoneProduct.objects.get_or_create(
                phone_name=p['phone_name'],
                store=store,
                defaults={**p, 'store': store},
            )
            if created:
                count += 1
            status = '✅ Created' if created else '⚠️  Exists'
            self.stdout.write(f'{status}: {product.phone_name}')

        self.stdout.write(self.style.SUCCESS(
            f'\n🎉 Done! Created {len(store_objs)} stores, {count} products.'
        ))
        self.stdout.write('📌 Admin: http://127.0.0.1:8000/admin/  (admin / admin123)')
