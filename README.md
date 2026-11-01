# سامانه جامع مدیریت و رزرواسیون اجاره خودرو (Car Rental System)
> **پروژه پایانی درس طراحی سیستم‌های تحت وب - دانشگاهی**  
> **توسعه‌دهندگان (Pair Programming):**  
> - **سروش حامدی** (`SoroushHamedi-Net`) - <soroush.hamedi.cs@gmail.com>  
> - **نورا نورس فرد** (`Noora-NF`) - <norasfardnoora@gmail.com>  

---

## ۱. معرفی و شرح پروژه
این پروژه یک سامانه جامع و مدرن تحت وب جهت مدیریت ناوگان، رزرواسیون آنلاین، اعتبارسنجی تداخل زمانی و صدور دیجیتال قراردادهای اجاره خودرو است که با بهره‌گیری از فریم‌ورک قدرتمند **Django 5** و پایگاه داده رابطه‌ای **PostgreSQL** پیاده‌سازی شده است.

### نقش‌های کاربری سیستم:
1. **مدیر سامانه (Manager):**
   - مدیریت ناوگان و برندهای خودرو (ثبت، ویرایش، تعیین مشخصات فنی و آپشن‌ها).
   - کنترل بلادرنگ وضعیت خودروها (`AVAILABLE` / `MAINTENANCE` / `RENTED`).
   - مشاهده کارتابل رزرواسیون‌ها و تأیید یا رد قراردادها به همراه درج توضیحات کارشناسی.
   - داشبورد مدیریتی جامع و آمارهای عملکردی.
2. **مشتری / کاربر عادی (Customer):**
   - ثبت‌نام، احراز هویت دو مرحله‌ای (ایمیل و پیامک OTP).
   - مشاهده لیست ناوگان خودرو با صفحه‌بندی (Pagination) و فیلتر پیشرفته بر اساس برند، مدل، ظرفیت و اسلایدر محدوده قیمت (Price Range).
   - مشاهده جزئیات خودرو و مکان تحویل بر روی نقشه تعاملی (Leaflet.js + OpenStreetMap).
   - ثبت درخواست رزرو با اعتبارسنجی بلادرنگ عدم تداخل تقویمی.
   - داشبورد پیگیری وضعیت سفارشات و امکان لغو درخواست‌های پیش از موعد.

---

## ۲. پشته فناوری (Technology Stack)
- **Backend:** Python 3.14 + Django 5.1
- **Database:** PostgreSQL 18 + `psycopg2-binary`
- **Frontend:** HTML5, CSS3, JavaScript (Fetch API / AJAX), Bootstrap 5 RTL, Vazirmatn Font
- **Maps:** Leaflet.js & OpenStreetMap
- **Environment Management:** Python venv, `python-decouple` (.env)
- **Version Control:** Git & GitHub (Co-authored Commits)

---

## ۳. فرآیندهای اصلی کسب‌وکار و دیاگرام‌ها (Process Diagrams)

کلیه فرآیندهای کسب‌وکار به صورت تفصیلی در سند [docs/PROCESS_DIAGRAMS.md](docs/PROCESS_DIAGRAMS.md) مستند گردیده است. کلیه نمودارها به صورت محلی در ویندوز با فونت استاندارد فارسی رندر شده‌اند و نسخه تعاملی وکتور نیز در دسترس است.

### فرآیند ۱: ثبت درخواست اجاره خودرو و بررسی هوشمند تداخل زمانی و موجودی
![فرآیند ۱](docs/diagrams/process_1_rental_request.png)

<details>
<summary><b>🔍 مشاهده نسخه تعاملی نمودار (Mermaid)</b></summary>

```mermaid
flowchart TD
    subgraph Customer ["👤 مشتری (Customer)"]
        A1["انتخاب خودرو و ورود به صفحه جزئیات"] --> A2["تعیین بازه تاریخی (start_date, end_date)"]
        A2 --> A3["کلیک روی دکمه ثبت درخواست اجاره"]
        A8["مشاهده پیام خطای تاریخ / فرم"]
        A9["مشاهده پیام خطای تداخل زمانی"]
        A10["مشاهده پیش‌فاکتور و کد پیگیری قرارداد (وضعیت PENDING)"]
    end

    subgraph System ["⚙️ موتور اعتبارسنجی سیستم (System)"]
        B1{"آیا تاریخ‌ها معتبر هستند؟<br/>(start >= today & end > start)"}
        B2{"آیا خودرو در وضعیت AVAILABLE است؟"}
        B3{"آیا تداخل زمانی با قراردادهای دیگر دارد؟<br/>(Date Overlap Query)"}
        B4["محاسبه روزها و هزینه کل (days * daily_price)"]
        B5["ایجاد شناسه یکتای قرارداد (contract_code)"]
        B6["ذخیره رکورد RentalContract با وضعیت PENDING"]
        B7["ثبت لاگ اعلان برای مشتری و مدیر (NotificationLog)"]
    end

    subgraph Database ["🗄️ پایگاه‌داده (PostgreSQL)"]
        DB1[("جدول fleet_car")]
        DB2[("جدول rentals_rentalcontract")]
        DB3[("جدول core_notificationlog")]
    end

    A3 --> B1
    B1 -- "خیر (خطای تاریخ)" --> A8
    B1 -- "بله" --> B2
    B2 -- "خیر (خودرو در تعمیرگاه)" --> A8
    B2 -- "بله" --> DB1
    DB1 -. بررسی وضعیت .-> B3
    B3 -- "بله (تداخل دارد)" --> A9
    B3 -- "خیر (آزاد است)" --> B4
    B4 --> B5
    B5 --> B6
    B6 --> DB2
    B6 --> DB3
    DB3 --> A10
```

</details>

---

### فرآیند ۲: بررسی، تأیید یا رد درخواست اجاره توسط مدیر، صدور قرارداد و ارسال اعلان
![فرآیند ۲](docs/diagrams/process_2_manager_review.png)

<details>
<summary><b>🔍 مشاهده نسخه تعاملی نمودار (Mermaid)</b></summary>

```mermaid
flowchart TD
    subgraph Manager ["👨‍💼 مدیر سامانه (Manager)"]
        M1["مشاهده کارتابل درخواست‌های معلق (PENDING)"] --> M2["انتخاب درخواست و بررسی اطلاعات و مدارک مشتری"]
        M2 --> M3{"تصمیم مدیر چیست؟"}
        M4["ثبت رد درخواست + درج دلیل در manager_note"]
        M5["ثبت تأیید درخواست + درج توضیحات تحویل"]
    end

    subgraph System ["⚙️ سیستم مرکزی (Django Core)"]
        S1["شروع تراکنش اتمیک دیتابیس (Atomic Transaction)"]
        S2{"بررسی مجدد تداخل همزمان (Race Condition Check)"}
        S3["تغییر وضعیت به REJECTED و آزادسازی تقویم خودرو"]
        S4["تغییر وضعیت به APPROVED و قفل قطعی بازه زمانی"]
        S5["تنظیم وضعیت خودرو به RENTED در تقویم ناوگان"]
        S6["تولید و ثبت اعلان ایمیلی و پیامکی رسمی"]
        S7["ارسال نوتیفیکیشن نتیجه به داشبورد و گوشی مشتری"]
    end

    subgraph Customer ["👤 مشتری (Customer)"]
        C1["دریافت پیامک/ایمیل رد درخواست به همراه دلیل مدیر"]
        C2["دریافت پیامک/ایمیل تأیید قرارداد + دستورالعمل تحویل خودرو"]
        C3["مشاهده وضعیت APPROVED در داشبورد کاربری"]
    end

    M3 -- "رد درخواست" --> M4
    M4 --> S3
    S3 --> S6
    S6 --> C1

    M3 -- "تأیید درخواست" --> M5
    M5 --> S1
    S1 --> S2
    S2 -- "خطای تداخل همزمان" --> M1
    S2 -- "بدون تداخل" --> S4
    S4 --> S5
    S5 --> S6
    S6 --> C2
    C2 --> C3
```

</details>

---

### فرآیند ۳: لغو درخواست اجاره توسط مشتری و آزادسازی منابع سیستم
![فرآیند ۳](docs/diagrams/process_3_cancellation.png)

<details>
<summary><b>🔍 مشاهده نسخه تعاملی نمودار (Mermaid)</b></summary>

```mermaid
flowchart TD
    subgraph Customer ["👤 مشتری (Customer)"]
        U1["ورود به داشبورد و بخش «سفارش‌های من»"] --> U2["انتخاب قرارداد و کلیک روی دکمه «لغو درخواست»"]
        U2 --> U3["تأیید پیام هشدار انصراف و درج دلیل اختیاری"]
        U6["نمایش خطای عدم امکان لغو (موعد گذشته یا وضعیت غیرمجاز)"]
        U7["مشاهده وضعیت CANCELLED و دریافت پیام موفقیت"]
    end

    subgraph System ["⚙️ سیستم مرکزی (Django Core)"]
        V1{"آیا قرارداد در وضعیت PENDING یا APPROVED است؟"}
        V2{"آیا تاریخ جاری قبل از تاریخ شروع (start_date) است؟"}
        V3["آغاز عملیات آزادسازی منابع"]
        V4["به‌روزرسانی فیلد status به CANCELLED"]
        V5["آزاد نمودن بازه زمانی تقویم خودرو در پایگاه‌داده"]
        V6["ثبت تراکنش در جدول NotificationLog"]
        V7["تولید پیامک اطلاع‌رسانی لغو"]
    end

    subgraph Manager ["👨‍💼 مدیر ناوگان (Manager)"]
        M_NOTIF["دریافت هشدار لغو سفارش و آماده‌سازی خودرو برای متقاضیان جدید"]
    end

    U3 --> V1
    V1 -- "خیر" --> U6
    V1 -- "بله" --> V2
    V2 -- "خیر (موعد تحویل فرا رسیده)" --> U6
    V2 -- "بله (مجاز به لغو)" --> V3
    V3 --> V4
    V4 --> V5
    V5 --> V6
    V6 --> V7
    V7 --> U7
    V7 --> M_NOTIF
```

</details>

---

### فرآیند ۴: بازگشت خودرو، بازرسی فنی و مدیریت چرخه وضعیت تعمیرگاه
![فرآیند ۴](docs/diagrams/process_4_vehicle_return.png)

<details>
<summary><b>🔍 مشاهده نسخه تعاملی نمودار (Mermaid)</b></summary>

```mermaid
flowchart TD
    subgraph Customer ["👤 مشتری (Customer)"]
        R1["تحویل فیزیکی خودرو و کلید به شعبه"]
        R6["دریافت فاکتور تسویه‌حساب نهایی و پیامک پایان قرارداد"]
    end

    subgraph Manager ["👨‍💼 مدیر / کارشناس ناوگان (Manager)"]
        M_REV1["ثبت کیلومتر پیموده شده و زمان دقیق ورود"]
        M_CHECK{"آیا خودرو آسیب دیده یا نیاز به سرویس دوره‌ای دارد؟"}
        M_MAINT["تنظیم وضعیت خودرو به MAINTENANCE و ارجاع به تعمیرگاه"]
        M_MAINT_DONE["پایان سرویس تعمیرگاه و بازگردانی وضعیت به AVAILABLE"]
        M_OK["تأیید سلامت خودرو و تنظیم وضعیت به AVAILABLE"]
        M_FIN["بستن قرارداد و ثبت وضعیت COMPLETED"]
    end

    subgraph System ["⚙️ سیستم مرکزی (Django Core)"]
        SYS_LATE{"آیا موعد تحویل دارای تأخیر زمانی است؟"}
        SYS_CALC_FINE["محاسبه جریمه دیرکرد و به‌روزرسانی فاکتور"]
        SYS_CLOSE["به‌روزرسانی وضعیت RentalContract به COMPLETED"]
        SYS_LOG["ثبت لاگ پایان قرارداد و ارسال اعلان به مشتری"]
    end

    subgraph Database ["🗄️ پایگاه‌داده (PostgreSQL)"]
        DB_CAR[("جدول fleet_car")]
        DB_RENTAL[("جدول rentals_rentalcontract")]
    end

    R1 --> M_REV1
    M_REV1 --> SYS_LATE
    SYS_LATE -- "بله (دارای دیرکرد)" --> SYS_CALC_FINE
    SYS_CALC_FINE --> M_CHECK
    SYS_LATE -- "خیر (سروقت)" --> M_CHECK

    M_CHECK -- "بله (نیاز به تعمیر)" --> M_MAINT
    M_MAINT --> DB_CAR
    M_MAINT -. پس از تعمیرات .-> M_MAINT_DONE
    M_MAINT_DONE --> DB_CAR

    M_CHECK -- "خیر (سالم است)" --> M_OK
    M_OK --> DB_CAR

    M_CHECK --> M_FIN
    M_FIN --> SYS_CLOSE
    SYS_CLOSE --> DB_RENTAL
    SYS_CLOSE --> SYS_LOG
    SYS_LOG --> R6
```

</details>

---

## ۴. ساختار معماری پروژه (Modular Apps)
پروژه از ۴ ماژول ساختاریافته تشکیل شده است:
- `accounts`: مدل سفارشی کاربر (`CustomUser`)، سطوح دسترسی (`Manager` / `Customer`)، احراز هویت پیامکی/ایمیلی.
- `fleet`: مدل برند (`CarBrand`)، مدل خودرو (`Car`)، مدیریت موقعیت جغرافیایی تحویل، وضعیت تعمیرگاه و فیلترها.
- `rentals`: مدل قرارداد (`RentalContract`)، اعتبارسنجی تاریخ‌ها و تداخل زمانی، گردش کار تایید/رد و لغو.
- `core`: صفحات اصلی، سیستم لاگینگ جامع، جدول اعلان‌ها (`NotificationLog`) و سرویس‌های سیستمی.

---

## ۵. راهنمای راه‌اندازی سریع (Getting Started)

```bash
# ۱. فعال‌سازی محیط مجازی
.\venv\Scripts\activate

# ۲. نصب وابستگی‌ها
pip install -r requirements.txt

# ۳. تنظیم متغیرهای محیطی
# فایل .env را بر مبنای .env.example ایجاد کنید

# ۴. اعمال مایگریشن‌های دیتابیس PostgreSQL
python manage.py migrate

# ۵. اجرای سرور توسعه
python manage.py runserver
```

---

## ۶. بکاپ‌های پایگاه داده (Database Backups)
نسخه‌های پشتیبان مرحله به مرحله پایگاه‌داده در پوشه [backups/](backups/) نگهداری می‌شوند:
- `backups/phase1_db_backup.json` & `backups/phase1_postgres.sql`
