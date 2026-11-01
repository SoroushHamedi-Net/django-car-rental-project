import os
import sys
import subprocess
import time
from pathlib import Path
from PIL import Image, ImageChops

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DIAGRAMS = {
    "process_1": {
        "targets": ["process_1_rental_request.png"],
        "code": """flowchart TD
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
"""
    },
    "process_2": {
        "targets": ["process_2_manager_review.png"],
        "code": """flowchart TD
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
"""
    },
    "process_3": {
        "targets": ["process_3_cancellation.png", "process_3_customer_cancellation.png"],
        "code": """flowchart TD
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
"""
    },
    "process_4": {
        "targets": ["process_4_vehicle_return.png", "process_4_vehicle_return_maintenance.png"],
        "code": """flowchart TD
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
"""
    }
}

def find_browser():
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None

def crop_diagram(image_path, pad=30):
    try:
        im = Image.open(image_path)
        bg = Image.new(im.mode, im.size, (255, 255, 255))
        diff = ImageChops.difference(im, bg)
        bbox = diff.getbbox()
        if bbox:
            crop_box = (
                max(0, bbox[0] - pad),
                max(0, bbox[1] - pad),
                min(im.width, bbox[2] + pad),
                min(im.height, bbox[3] + pad)
            )
            cropped = im.crop(crop_box)
            cropped.save(image_path, "PNG", optimize=True)
            return True
    except Exception as e:
        print(f"  Warning during cropping {image_path}: {e}")
    return False

def export_diagrams_locally():
    browser = find_browser()
    if not browser:
        print("ERROR: Neither Microsoft Edge nor Google Chrome was found on this system.")
        sys.exit(1)
        
    print(f"Using headless browser: {browser}")
    
    base_dir = Path(__file__).resolve().parent.parent
    scripts_dir = base_dir / "scripts"
    out_dir = base_dir / "docs" / "diagrams"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Path to local mermaid.min.js
    local_mermaid = scripts_dir / "mermaid.min.js"
    mermaid_src = local_mermaid.as_uri() if local_mermaid.exists() else "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"

    for key, data in DIAGRAMS.items():
        targets = data["targets"]
        code = data["code"]
        primary_target = targets[0]
        primary_path = out_dir / primary_target
        temp_html_path = scripts_dir / f"temp_{key}.html"
        
        print(f"\n[+] Rendering {key} -> {primary_target}...")
        
        html_content = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
* {{
    font-family: 'Vazirmatn', Tahoma, 'Segoe UI', Arial, sans-serif !important;
}}
html, body {{
    background-color: #ffffff !important;
    margin: 0;
    padding: 30px;
    direction: rtl;
    display: inline-block;
}}
.mermaid {{
    font-family: 'Vazirmatn', Tahoma, 'Segoe UI', Arial, sans-serif;
    font-size: 15px;
    direction: rtl;
    text-align: center;
}}
.mermaid svg {{
    max-width: none !important;
    height: auto !important;
    font-family: 'Vazirmatn', Tahoma, 'Segoe UI', Arial, sans-serif !important;
}}
.nodeLabel, .edgeLabel, .cluster-label, span.nodeLabel {{
    font-family: 'Vazirmatn', Tahoma, 'Segoe UI', Arial, sans-serif !important;
    font-weight: 500 !important;
}}
</style>
<script src="{mermaid_src}"></script>
<script>
mermaid.initialize({{
    startOnLoad: true,
    theme: 'default',
    fontFamily: 'Vazirmatn, Tahoma, "Segoe UI", Arial, sans-serif',
    themeVariables: {{
        fontFamily: 'Vazirmatn, Tahoma, "Segoe UI", Arial, sans-serif',
        fontSize: '15px',
        primaryColor: '#e8f0fe',
        primaryTextColor: '#1a73e8',
        lineColor: '#5f6368'
    }},
    flowchart: {{
        htmlLabels: true,
        curve: 'basis'
    }}
}});
</script>
</head>
<body>
<div class="mermaid">
{code}
</div>
</body>
</html>
"""
        temp_html_path.write_text(html_content, encoding="utf-8")
        
        # Screenshot with Edge/Chrome
        html_url = temp_html_path.resolve().as_uri()
        screenshot_target = str(primary_path.resolve())
        
        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--force-device-scale-factor=2",
            "--virtual-time-budget=6000",
            "--window-size=2400,1800",
            f"--screenshot={screenshot_target}",
            html_url
        ]
        
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Verify file existence
        if primary_path.exists() and primary_path.stat().st_size > 2000:
            crop_diagram(str(primary_path), pad=30)
            file_size = primary_path.stat().st_size
            print(f"  [OK] Rendered and cropped {primary_target} ({file_size} bytes)")
            
            # Copy to alias targets if any
            for alias in targets[1:]:
                alias_path = out_dir / alias
                alias_path.write_bytes(primary_path.read_bytes())
                print(f"  [OK] Saved alias {alias}")
        else:
            print(f"  [FAIL] Failed to generate {primary_target}")
            
        # Clean up temporary HTML
        if temp_html_path.exists():
            temp_html_path.unlink()

    print("\n[✓] All diagrams successfully exported locally with native Persian fonts!")

if __name__ == "__main__":
    export_diagrams_locally()
