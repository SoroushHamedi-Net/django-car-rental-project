from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import CustomUser
from fleet.models import CarBrand, Car
from rentals.models import RentalContract


class Command(BaseCommand):
    help = 'تزریق داده‌های اولیه و تستی ناوگان، کاربران و قراردادها به پایگاه‌داده'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('شروع بارگذاری داده‌های اولیه سامانه اجاره خودرو...'))

        # ۱. ساخت کاربران مدیر (Managers)
        manager1, created = CustomUser.objects.get_or_create(
            username='manager1',
            defaults={
                'email': 'soroush@carrental.ir',
                'first_name': 'سروش',
                'last_name': 'حامدی',
                'role': 'MANAGER',
                'phone_number': '09121111111',
                'national_code': '0011223344',
                'is_staff': True,
                'is_superuser': True,
                'is_email_verified': True,
                'is_phone_verified': True,
            }
        )
        if created:
            manager1.set_password('AdminPassword123!')
            manager1.save()
            self.stdout.write(self.style.SUCCESS('کاربر مدیر ۱ (manager1) با موفقیت ساخته شد.'))

        manager2, created = CustomUser.objects.get_or_create(
            username='manager2',
            defaults={
                'email': 'noora@carrental.ir',
                'first_name': 'نورا',
                'last_name': 'نوراسفرد',
                'role': 'MANAGER',
                'phone_number': '09122222222',
                'national_code': '0022334455',
                'is_staff': True,
                'is_email_verified': True,
                'is_phone_verified': True,
            }
        )
        if created:
            manager2.set_password('AdminPassword123!')
            manager2.save()
            self.stdout.write(self.style.SUCCESS('کاربر مدیر ۲ (manager2) با موفقیت ساخته شد.'))

        # ۲. ساخت کاربران مشتری (Customers)
        customers_data = [
            ('customer1', 'ali@example.com', 'علی', 'محمدی', '09123333333', '0033445566'),
            ('customer2', 'sara@example.com', 'سارا', 'کریمی', '09124444444', '0044556677'),
            ('customer3', 'reza@example.com', 'رضا', 'صادقی', '09125555555', '0055667788'),
            ('customer4', 'maryam@example.com', 'مریم', 'احمدی', '09126666666', '0066778899'),
        ]

        customers = []
        for username, email, first_name, last_name, phone, national in customers_data:
            user, created = CustomUser.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': 'CUSTOMER',
                    'phone_number': phone,
                    'national_code': national,
                    'is_email_verified': True,
                }
            )
            if created:
                user.set_password('CustomerPass123!')
                user.save()
            customers.append(user)

        self.stdout.write(self.style.SUCCESS(f'{len(customers)} کاربر مشتری آماده شد.'))

        # ۳. ساخت ۵ برند مطرح خودرو
        brands_data = [
            ('مرسدس بنز', 'آلمان'),
            ('تویوتا', 'ژاپن'),
            ('هیوندای', 'کره جنوبی'),
            ('کیا', 'کره جنوبی'),
            ('پژو', 'فرانسه'),
        ]
        brands = {}
        for name, country in brands_data:
            brand, _ = CarBrand.objects.get_or_create(name=name, defaults={'country': country})
            brands[name] = brand

        self.stdout.write(self.style.SUCCESS(f'{len(brands)} برند خودرو ثبت شد.'))

        # ۴. ساخت ۱۰ خودروی واقعی در ناوگان با وضعیت‌ها و قیمت‌های متنوع
        cars_data = [
            (brands['مرسدس بنز'], 'C200', 2020, 9500000, 5, 'AVAILABLE', 'تهران، سعادت‌آباد، خیابان سرو غربی', 35.7765, 51.3688, 'کیت AMG، رادار نقطه کور، صندلی چرم طبیعی، سیستم صوتی برمستر، بیمه بدنه کامل'),
            (brands['مرسدس بنز'], 'E250', 2021, 14000000, 5, 'RENTED', 'تهران، نیاوران، سه راه یاسر', 35.8152, 51.4678, 'سقف پانوراما، اتوپارک، دوربین ۳۶۰ درجه، کروز کنترل هوشمند، پکیج اختصاصی VIP'),
            (brands['تویوتا'], 'Camry', 2018, 4800000, 5, 'AVAILABLE', 'تهران، میدان ونک، خیابان گاندی', 35.7575, 51.4116, 'هیبرید، مصرف سوخت فوق‌العاده کم، سواری نرم و راحت، سیستم صوتی JBL'),
            (brands['تویوتا'], 'RAV4', 2019, 6500000, 5, 'AVAILABLE', 'تهران، شهرک غرب، بلوار دادمان', 35.7612, 51.3789, 'دو دیفرانسیل AWD، گرمکن صندلی‌ها، سیستم کنترل کشش در سراشیبی، مانیتور لمسی بزرگ'),
            (brands['هیوندای'], 'Sonata LF', 2017, 3900000, 5, 'AVAILABLE', 'تهران، صادقیه، بلوار فردوس شرق', 35.7208, 51.3142, 'فول کامل، درایو مود، ترمز دستی برقی، اتوهلد، پرده عقب برقی'),
            (brands['هیوندای'], 'Santa Fe', 2018, 5800000, 7, 'MAINTENANCE', 'تهران، میدان آزادی، تعمیرگاه مرکزی سامانه', 35.6997, 51.3541, '۷ نفره خانوادگی، دو دیفرانسیل، صندوق برقی، چک فنی دوره‌ای و سرویس لنت و تعویض روغن'),
            (brands['کیا'], 'Sportage', 2017, 4500000, 5, 'AVAILABLE', 'تهران، میدان آرژانتین، خیابان وزرا', 35.7390, 51.4160, 'سقف شیشه‌ای پانوراما، تهویه دوگانه اتوماتیک، شیب‌سنج، رینگ ۱۸ اینچی اسپرت'),
            (brands['کیا'], 'Cerato', 2016, 2600000, 5, 'RENTED', 'تهران، پاسداران، گلستان پنجم', 35.7711, 51.4645, 'موتور ۲۰۰۰ سی‌سی، پدال شیفتر پشت فرمان، کی‌لس استارت، بیمه شخص ثالث و بدنه کامل'),
            (brands['پژو'], '206 SD', 1399, 950000, 4, 'AVAILABLE', 'تهران، میدان هفت تیر، خیابان مفتح شمالی', 35.7225, 51.4284, 'صندوق‌دار V8، بسیار تمیز و کم‌مصرف، مناسب سفرهای شهری و اقتصادی، کولر و بخاری عالی'),
            (brands['پژو'], '207i MC', 1401, 1350000, 4, 'AVAILABLE', 'تهران، پیروزی، خیابان نبرد شمالی', 35.6881, 51.4795, 'سقف قرمز دو رنگ، مانیتور مالتی مدیا، کروز کنترل، فرمان برقی، رینگ آلومینیومی'),
        ]

        cars = []
        for brand, model_name, year, price, capacity, status, address, lat, lng, features in cars_data:
            car, _ = Car.objects.get_or_create(
                brand=brand,
                model_name=model_name,
                year=year,
                defaults={
                    'daily_price': price,
                    'capacity': capacity,
                    'status': status,
                    'pickup_address': address,
                    'latitude': lat,
                    'longitude': lng,
                    'features': features,
                    'created_by': manager1,
                }
            )
            cars.append(car)

        self.stdout.write(self.style.SUCCESS(f'{len(cars)} خودرو در ناوگان آماده‌سازی گردید.'))

        # ۵. ساخت ۶ قرارداد نمونه با وضعیت‌های متنوع
        today = timezone.localdate()
        contracts_data = [
            (customers[0], cars[1], today - timedelta(days=2), today + timedelta(days=3), 'APPROVED', 'قرارداد تایید و کلید و مدارک در نیاوران تحویل مشتری گردید.'),
            (customers[1], cars[7], today - timedelta(days=1), today + timedelta(days=4), 'APPROVED', 'مدارک و ودیعه نقدی دریافت شد، خودرو در اجاره می‌باشد.'),
            (customers[0], cars[2], today + timedelta(days=5), today + timedelta(days=8), 'PENDING', ''),
            (customers[2], cars[4], today + timedelta(days=2), today + timedelta(days=6), 'PENDING', ''),
            (customers[1], cars[9], today - timedelta(days=10), today - timedelta(days=6), 'COMPLETED', 'خودرو بدون هیچ‌گونه خسارت تحویل گرفته و ودیعه مسترد شد.'),
            (customers[3], cars[0], today - timedelta(days=5), today - timedelta(days=3), 'REJECTED', 'عدم انطباق مدارک بارگذاری شده با هویت متقاضی.'),
        ]

        created_contracts_count = 0
        for customer, car, start_date, end_date, status, note in contracts_data:
            # جلوگیری از تکرار ایجاد قرارداد مشابه
            exists = RentalContract.objects.filter(customer=customer, car=car, start_date=start_date).exists()
            if not exists:
                contract = RentalContract(
                    customer=customer,
                    car=car,
                    start_date=start_date,
                    end_date=end_date,
                    daily_rate_snapshot=car.daily_price,
                    status=status,
                    manager_note=note,
                    reviewed_by=manager1 if status in ['APPROVED', 'REJECTED', 'COMPLETED'] else None
                )
                contract.save()
                created_contracts_count += 1

        self.stdout.write(self.style.SUCCESS(f'{created_contracts_count} قرارداد نمونه با موفقیت در سیستم ثبت گردید.'))
        self.stdout.write(self.style.SUCCESS('بارگذاری داده‌های اولیه با موفقیت کامل انجام شد!'))
