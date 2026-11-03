import os
import sys
import re
import subprocess
from pathlib import Path
from PIL import Image, ImageChops

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DIAGRAMS = {
    "process_1": {
        "title": "فرآیند ۱: ثبت درخواست اجاره خودرو و بررسی هوشمند تداخل زمانی و موجودی",
        "targets_png": ["process_1_rental_request.png"],
        "target_svg": "process_1_rental_request.svg",
        "code": """flowchart LR
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
"""
    },
    "process_2": {
        "title": "فرآیند ۲: بررسی، تأیید یا رد درخواست اجاره توسط مدیر، صدور قرارداد و ارسال اعلان",
        "targets_png": ["process_2_manager_review.png"],
        "target_svg": "process_2_manager_review.svg",
        "code": """flowchart LR
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
"""
    },
    "process_3": {
        "title": "فرآیند ۳: لغو درخواست اجاره توسط مشتری و آزادسازی منابع سیستم",
        "targets_png": ["process_3_cancellation.png", "process_3_customer_cancellation.png"],
        "target_svg": "process_3_cancellation.svg",
        "code": """flowchart LR
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
"""
    },
    "process_4": {
        "title": "فرآیند ۴: بازگشت خودرو، بازرسی فنی و مدیریت چرخه وضعیت تعمیرگاه",
        "targets_png": ["process_4_vehicle_return.png", "process_4_vehicle_return_maintenance.png"],
        "target_svg": "process_4_vehicle_return.svg",
        "code": """flowchart LR
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

def crop_diagram(image_path, pad=35):
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
            return cropped.size
    except Exception as e:
        print(f"  Warning during cropping {image_path}: {e}")
    return None

def export_all_diagrams():
    browser = find_browser()
    if not browser:
        print("ERROR: Neither Microsoft Edge nor Google Chrome was found on this system.")
        sys.exit(1)
        
    print(f"Using headless browser: {browser}")
    
    base_dir = Path(__file__).resolve().parent.parent
    scripts_dir = base_dir / "scripts"
    out_dir = base_dir / "docs" / "diagrams"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    for key, data in DIAGRAMS.items():
        targets_png = data["targets_png"]
        target_svg = data["target_svg"]
        code = data["code"]
        title = data["title"]
        primary_png = out_dir / targets_png[0]
        svg_path = out_dir / target_svg
        temp_html_path = scripts_dir / f"render_{key}.html"
        
        print(f"\n[+] Rendering {key}: {title}...")
        
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
    width: auto;
}}
.mermaid {{
    display: inline-block;
    font-family: 'Vazirmatn', Tahoma, 'Segoe UI', Arial, sans-serif;
    font-size: 22px;
    direction: rtl;
    text-align: center;
    width: max-content !important;
}}
.mermaid svg {{
    max-width: none !important;
    font-family: 'Vazirmatn', Tahoma, 'Segoe UI', Arial, sans-serif !important;
}}
.nodeLabel, .edgeLabel, .cluster-label, span.nodeLabel {{
    font-family: 'Vazirmatn', Tahoma, 'Segoe UI', Arial, sans-serif !important;
    font-size: 20px !important;
    font-weight: 600 !important;
}}
.cluster-label span {{
    font-size: 22px !important;
    font-weight: 700 !important;
}}
</style>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
mermaid.initialize({{
    startOnLoad: true,
    theme: 'base',
    themeVariables: {{
        fontFamily: 'Vazirmatn, Tahoma, "Segoe UI", Arial, sans-serif',
        fontSize: '22px',
        primaryColor: '#ffffff',
        primaryTextColor: '#0f172a',
        primaryBorderColor: '#1e40af',
        lineColor: '#334155',
        secondaryColor: '#fef3c7',
        tertiaryColor: '#f8fafc'
    }},
    flowchart: {{
        htmlLabels: true,
        curve: 'basis'
    }}
}});

window.addEventListener('load', async () => {{
    if (document.fonts) {{
        await document.fonts.ready;
    }}
    setTimeout(() => {{
        const svg = document.querySelector('.mermaid svg');
        if (svg) {{
            const vb = svg.viewBox.baseVal;
            if (vb && vb.width > 0) {{
                svg.style.width = vb.width + 'px';
                svg.style.height = vb.height + 'px';
                svg.style.maxWidth = 'none';
            }}
        }}
    }}, 400);
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
        html_url = temp_html_path.resolve().as_uri()

        # Step 1: Extract SVG vector using --dump-dom
        dom_proc = subprocess.run(
            [browser, "--headless=new", "--disable-gpu", "--virtual-time-budget=5000", "--dump-dom", html_url],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        match = re.search(r'(<svg[^>]*class=["\']mermaid["\'][^>]*>.*?</svg>|<svg[^>]*id=["\']mermaid-[^>]*>.*?</svg>|<svg[^>]*>.*?</svg>)', dom_proc.stdout, re.DOTALL)
        if match:
            svg_content = match.group(1)
            svg_path.write_text(svg_content, encoding="utf-8")
            print(f"  [OK] Saved vector SVG: {target_svg} ({len(svg_content)} bytes)")
        else:
            print(f"  [WARN] Could not extract raw SVG for {key}")

        # Step 2: Render 3X Retina Screenshot
        cmd_png = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--force-device-scale-factor=3",
            "--virtual-time-budget=6000",
            "--window-size=4500,2500",
            f"--screenshot={str(primary_png.resolve())}",
            html_url
        ]
        subprocess.run(cmd_png, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Step 3: Crop and duplicate to aliases
        if primary_png.exists() and primary_png.stat().st_size > 5000:
            final_size = crop_diagram(str(primary_png), pad=35)
            file_size = primary_png.stat().st_size
            print(f"  [OK] Rendered 3x Retina PNG: {primary_png.name} (dimensions={final_size}, {file_size} bytes)")
            
            for alias in targets_png[1:]:
                alias_path = out_dir / alias
                alias_path.write_bytes(primary_png.read_bytes())
                print(f"  [OK] Saved alias: {alias}")
        else:
            print(f"  [FAIL] Failed to generate {primary_png.name}")
            
        # Clean up temporary HTML
        if temp_html_path.exists():
            temp_html_path.unlink()

    print("\n[✓] All 4 Ultra-HD process diagrams rendered at 3x Retina resolution!")

if __name__ == "__main__":
    export_all_diagrams()
