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

کلیه فرآیندهای کسب‌وکار به صورت تفصیلی در سند [docs/PROCESS_DIAGRAMS.md](docs/PROCESS_DIAGRAMS.md) مستند گردیده است. تمامی نمودارها در رزولوشن فوق‌العاده **۳X Retina Ultra-HD** و چینش افقی متوازن رندر شده‌اند.

> 🖥️ **صفحه ارائه تعاملی دیاگرام‌ها:** جهت نمایش در کلاس با قابلیت زوم بی‌نهایت و جابجایی برداری، صفحه [docs/diagrams/present_diagrams.html](docs/diagrams/present_diagrams.html) را در مرورگر باز کنید.

---

### فرآیند ۱: ثبت درخواست اجاره خودرو و بررسی هوشمند تداخل زمانی و موجودی
![فرآیند ۱](docs/diagrams/process_1_rental_request.png)
*(وکتور با کیفیت نامحدود: [process_1_rental_request.svg](docs/diagrams/process_1_rental_request.svg))*

```mermaid
flowchart LR
    subgraph Customer ["👤 مشتری (Customer)"]
        direction TB
        A1["انتخاب خودرو و<br/>مشاهده جزئیات فنی"] --> A2["تعیین بازه زمانی اجاره<br/>(start_date تا end_date)"]
        A2 --> A3["ارسال فرم و ثبت نهایی<br/>درخواست اولیه"]
        A_ERR["نمایش خطای تاریخ /<br/>تداخل بازه زمانی"]
        A_OK["مشاهده پیش‌فاکتور و<br/>کد پیگیری (PENDING)"]
    end

    subgraph System ["⚙️ موتور اعتبارسنجی (Core)"]
        direction TB
        B1{"صحت تاریخ‌ها؟<br/>(امروز <= شروع < پایان)"}
        B2{"وضعیت خودرو؟<br/>(AVAILABLE)"}
        B3{"تداخل با رزروهای دیگر؟<br/>(Date Overlap Query)"}
        B4["محاسبه مبلغ کل اجاره<br/>(days × daily_price)"]
        B5["تولید کد یکتا و ایجاد<br/>RentalContract (PENDING)"]
        B6["ثبت لاگ و ارسال اعلان<br/>(NotificationLog)"]
    end

    subgraph Database ["🗄️ پایگاه‌داده (PostgreSQL)"]
        direction TB
        DB_CAR[("جدول ناوگان<br/>fleet_car")]
        DB_RENTAL[("جدول قراردادها<br/>rentals_rentalcontract")]
        DB_LOG[("جدول اعلان‌ها<br/>core_notificationlog")]
    end

    A3 --> B1
    B1 -- "نامعتبر" --> A_ERR
    B1 -- "معتبر" --> B2
    B2 -- "در تعمیرگاه" --> A_ERR
    B2 -- "آماده" --> DB_CAR
    DB_CAR -. استعلام تقویم .-> B3
    B3 -- "تداخل دارد" --> A_ERR
    B3 -- "آزاد" --> B4 --> B5
    B5 --> DB_RENTAL
    B5 --> B6 --> DB_LOG
    B6 --> A_OK

    classDef default fill:#ffffff,stroke:#1e40af,stroke-width:2.5px,color:#0f172a;
    classDef decision fill:#fef3c7,stroke:#d97706,stroke-width:2.5px,color:#78350f;
    classDef error fill:#fee2e2,stroke:#dc2626,stroke-width:2.5px,color:#991b1b;
    classDef success fill:#dcfce7,stroke:#16a34a,stroke-width:2.5px,color:#14532d;
    classDef db fill:#f0fdf4,stroke:#059669,stroke-width:2px,color:#064e3b;
    class B1,B2,B3 decision;
    class A_ERR error;
    class A_OK success;
    class DB_CAR,DB_RENTAL,DB_LOG db;
```

---

### فرآیند ۲: بررسی، تأیید یا رد درخواست اجاره توسط مدیر، صدور قرارداد و ارسال اعلان
![فرآیند ۲](docs/diagrams/process_2_manager_review.png)
*(وکتور با کیفیت نامحدود: [process_2_manager_review.svg](docs/diagrams/process_2_manager_review.svg))*

```mermaid
flowchart LR
    subgraph Manager ["👨‍💼 مدیر سامانه (Manager)"]
        direction TB
        M1["مشاهده کارتابل درخواست‌های<br/>معلق (وضعیت PENDING)"] --> M2["بررسی مدارک و پیشینه<br/>مشتری متقاضی"]
        M2 --> M_DEC{"تصمیم مدیر؟"}
        M_REJ["ثبت رد درخواست +<br/>درج دلیل در manager_note"]
        M_APP["ثبت تأیید درخواست +<br/>دستورالعمل تحویل"]
    end

    subgraph System ["⚙️ سیستم مرکزی (Django Core)"]
        direction TB
        S_ATOMIC["آغاز تراکنش اتمیک<br/>(transaction.atomic)"]
        S_CHECK{"بررسی تداخل همزمان؟<br/>(Race Condition Check)"}
        S_SET_REJ["تغییر وضعیت به REJECTED<br/>و آزادسازی تقویم خودرو"]
        S_SET_APP["تغییر وضعیت به APPROVED<br/>و قفل قطعی بازه زمانی"]
        S_CAR_STATUS["تنظیم وضعیت خودرو به RENTED<br/>در تقویم ناوگان"]
        S_NOTIF["تولید و ثبت اعلان رسمی<br/>(ایمیل و پیامک OTP/اطلاع‌رسانی)"]
    end

    subgraph Customer ["👤 مشتری (Customer)"]
        direction TB
        C_REJ["دریافت پیامک رد درخواست<br/>به همراه دلیل مدیر"]
        C_APP["دریافت پیامک تأیید رزرو +<br/>دستورالعمل تحویل خودرو"]
        C_DASH["مشاهده قرارداد فعال و<br/>پیش‌فاکتور در داشبورد"]
    end

    M_DEC -- "رد درخواست" --> M_REJ --> S_SET_REJ --> S_NOTIF --> C_REJ
    M_DEC -- "تأیید درخواست" --> M_APP --> S_ATOMIC --> S_CHECK
    S_CHECK -- "تداخل همزمان" --> M1
    S_CHECK -- "بدون تداخل" --> S_SET_APP --> S_CAR_STATUS --> S_NOTIF --> C_APP --> C_DASH

    classDef default fill:#ffffff,stroke:#1e40af,stroke-width:2.5px,color:#0f172a;
    classDef decision fill:#fef3c7,stroke:#d97706,stroke-width:2.5px,color:#78350f;
    classDef error fill:#fee2e2,stroke:#dc2626,stroke-width:2.5px,color:#991b1b;
    classDef success fill:#dcfce7,stroke:#16a34a,stroke-width:2.5px,color:#14532d;
    class M_DEC,S_CHECK decision;
    class M_REJ,C_REJ error;
    class S_SET_APP,C_APP,C_DASH success;
```

---

### فرآیند ۳: لغو درخواست اجاره توسط مشتری و آزادسازی منابع سیستم
![فرآیند ۳](docs/diagrams/process_3_cancellation.png)
*(وکتور با کیفیت نامحدود: [process_3_cancellation.svg](docs/diagrams/process_3_cancellation.svg))*

```mermaid
flowchart LR
    subgraph Customer ["👤 مشتری (Customer)"]
        direction TB
        U1["ورود به داشبورد و<br/>بخش سفارش‌های من"] --> U2["انتخاب قرارداد و<br/>کلیک روی لغو درخواست"]
        U2 --> U3["تأیید هشدار انصراف و<br/>درج دلیل اختیاری"]
        U_ERR["نمایش خطای عدم امکان لغو<br/>(موعد گذشته یا وضعیت غیرمجاز)"]
        U_OK["مشاهده وضعیت CANCELLED و<br/>دریافت پیامک تأیید لغو"]
    end

    subgraph System ["⚙️ موتور اعتبارسنجی لغو (Core)"]
        direction TB
        V1{"وضعیت مجاز است؟<br/>(PENDING یا APPROVED)"}
        V2{"موعد تحویل فرا نرسیده؟<br/>(تاریخ جاری < start_date)"}
        V3["آغاز عملیات آزادسازی منابع"]
        V4["به‌روزرسانی فیلد وضعیت<br/>به CANCELLED"]
        V5["آزاد نمودن بازه تقویم خودرو<br/>در پایگاه‌داده"]
        V6["ثبت تراکنش در جدول لاگ و<br/>ارسال پیامک اطلاع‌رسانی"]
    end

    subgraph Manager ["👨‍💼 مدیر ناوگان (Manager)"]
        direction TB
        M_NOTIF["دریافت هشدار لغو در کارتابل و<br/>آماده‌سازی خودرو برای متقاضیان جدید"]
    end

    U3 --> V1
    V1 -- "خیر" --> U_ERR
    V1 -- "بله" --> V2
    V2 -- "خیر (موعد رسیده)" --> U_ERR
    V2 -- "بله (مجاز)" --> V3 --> V4 --> V5
    V5 --> U_OK
    V5 --> M_NOTIF

    classDef default fill:#ffffff,stroke:#1e40af,stroke-width:2.5px,color:#0f172a;
    classDef decision fill:#fef3c7,stroke:#d97706,stroke-width:2.5px,color:#78350f;
    classDef error fill:#fee2e2,stroke:#dc2626,stroke-width:2.5px,color:#991b1b;
    classDef success fill:#dcfce7,stroke:#16a34a,stroke-width:2.5px,color:#14532d;
    class V1,V2 decision;
    class U_ERR error;
    class U_OK success;
```

---

### فرآیند ۴: بازگشت خودرو، بازرسی فنی و مدیریت چرخه وضعیت تعمیرگاه
![فرآیند ۴](docs/diagrams/process_4_vehicle_return.png)
*(وکتور با کیفیت نامحدود: [process_4_vehicle_return.svg](docs/diagrams/process_4_vehicle_return.svg))*

```mermaid
flowchart LR
    subgraph Customer ["👤 مشتری (Customer)"]
        direction TB
        R1["تحویل فیزیکی خودرو و<br/>سوئیچ به ایستگاه"]
        R_END["دریافت فاکتور تسویه نهایی<br/>و پیامک اتمام قرارداد"]
    end

    subgraph Manager ["👨‍💼 کارشناس فنی / مدیر (Manager)"]
        direction TB
        M_REC["ثبت کیلومتر پیموده شده،<br/>باک سوخت و زمان دقیق ورود"]
        M_INSPECT{"نتیجه بازرسی فنی و بدنه؟"}
        M_MAINT["تنظیم وضعیت خودرو به MAINTENANCE<br/>و ارجاع به تعمیرگاه"]
        M_MAINT_DONE["پایان سرویس و بازگردانی<br/>وضعیت به AVAILABLE"]
        M_OK["تأیید سلامت کامل خودرو و<br/>تنظیم وضعیت به AVAILABLE"]
        M_FIN["بستن قرارداد و تغییر وضعیت<br/>به COMPLETED"]
    end

    subgraph System ["⚙️ سیستم مرکزی (Core)"]
        direction TB
        SYS_DELAY{"آیا دارای تأخیر زمانی است؟<br/>(تحویل > end_date)"}
        SYS_FINE["محاسبه جریمه دیرکرد روزانه<br/>و به‌روزرسانی فاکتور نهایی"]
        SYS_CLOSE["به‌روزرسانی قرارداد به COMPLETED<br/>در جدول دیتابیس"]
        SYS_LOG["ثبت لاگ پایان قرارداد و<br/>ارسال اعلان پیامکی به مشتری"]
    end

    R1 --> M_REC --> SYS_DELAY
    SYS_DELAY -- "بله (دارای دیرکرد)" --> SYS_FINE --> M_INSPECT
    SYS_DELAY -- "خیر (سروقت)" --> M_INSPECT
    M_INSPECT -- "نیاز به تعمیر" --> M_TO_MAINT
    M_TO_MAINT -. پس از تعمیرات .-> M_MAINT_DONE --> M_FIN
    M_INSPECT -- "سالم" --> M_OK --> M_FIN
    M_FIN --> SYS_CLOSE --> SYS_LOG --> R_END

    classDef default fill:#ffffff,stroke:#1e40af,stroke-width:2.5px,color:#0f172a;
    classDef decision fill:#fef3c7,stroke:#d97706,stroke-width:2.5px,color:#78350f;
    classDef error fill:#fee2e2,stroke:#dc2626,stroke-width:2.5px,color:#991b1b;
    classDef success fill:#dcfce7,stroke:#16a34a,stroke-width:2.5px,color:#14532d;
    class SYS_DELAY,M_INSPECT decision;
    class M_TO_MAINT error;
    class M_MAINT_DONE,M_OK,M_FIN,R_END success;
```

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
