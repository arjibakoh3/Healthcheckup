
import streamlit as st
import pandas as pd
import os
from io import BytesIO

st.set_page_config(page_title="โปรแกรมตรวจสุขภาพ + Add-on", page_icon="🩺", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --bg: #ffffff;
        --text: #1a1a1a;
        --muted: #4b5563;
        --card: #f7f8fb;
        --border: #d1d5db;
        --accent: #0f172a;
        --accent-hover: #1f2937;
    }
    .stApp {
        background-color: var(--bg);
        color: var(--text);
        font-family: "Segoe UI", "Tahoma", "Arial", sans-serif;
    }
    .stApp, .stApp p, .stApp span, .stApp label, .stMarkdown, .stText, .stCaption,
    .stDataFrame, .stMetric, .stSelectbox, .stMultiSelect, .stCheckbox, .stRadio {
        color: var(--text);
    }
    .stCaption, .stMarkdown small, .stMarkdown em {
        color: var(--muted);
    }
    [data-testid="stMetricValue"] {
        color: #000000;
    }
    .stButton > button {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid var(--border);
    }
    .stButton > button:hover {
        background-color: #f3f4f6;
        border-color: var(--border);
    }
    .stDownloadButton > button {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid var(--border);
    }
    .stDownloadButton > button:hover {
        background-color: #f3f4f6;
        border-color: var(--border);
    }
    .stExpander, .stDataFrame, .stTable, .stMetric {
        border: 1px solid var(--border);
        background-color: var(--card);
        border-radius: 10px;
    }
    [data-testid="stDataFrame"], [data-testid="stTable"] {
        background-color: #ffffff;
        color: #000000;
    }
    [data-testid="stDataFrame"] [role="grid"] {
        background-color: #ffffff;
        color: #000000;
    }
    [data-testid="stDataFrame"] [role="grid"] * {
        color: #000000;
    }
    [data-testid="stDataFrame"] {
        --gdg-bg: #ffffff;
        --gdg-text-dark: #000000;
        --gdg-text-medium: #111111;
        --gdg-border-color: #d1d5db;
        --gdg-header-bg: #ffffff;
        --gdg-header-text-color: #000000;
        --gdg-selection-bg: rgba(15, 23, 42, 0.12);
        --gdg-selection-border-color: #0f172a;
        --gdg-hover-bg: #f3f4f6;
    }
    [data-testid="stTable"] table {
        background-color: #ffffff;
        color: #000000;
    }
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stMultiSelect > div > div,
    .stTextArea > div > div > textarea {
        color: var(--text);
        border-color: var(--border);
        background-color: #ffffff;
    }
    .stSelectbox [data-baseweb="select"] > div {
        background-color: #ffffff;
    }
    .stSelectbox [role="listbox"] {
        background-color: #ffffff;
        color: var(--text);
        border: 1px solid var(--border);
    }
    .inc-table {
        width: 100%;
        border-collapse: collapse;
        background-color: #ffffff;
        color: #000000;
    }
    .inc-table th, .inc-table td {
        border: 1px solid var(--border);
        padding: 8px 10px;
        text-align: left;
        color: #000000;
    }
    .civil-table th:nth-child(2), .civil-table td:nth-child(2) {
        width: 120px;
        white-space: nowrap;
    }
    .inc-table thead th {
        background-color: #ffffff;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# ข้อมูลราคา (อ้างอิง HOSxP ที่ผู้ใช้ให้มา)
# -----------------------------
BASE_PACKAGES = {
    "Basic (449)": {
        "price": 449,
        "includes": [
            ("ตรวจร่างกายโดยแพทย์", "พื้นฐาน", "ตรวจร่างกายทั่วไปโดยแพทย์"),
            ("CBC", "พื้นฐาน", "ตรวจความสมบูรณ์ของเม็ดเลือด (คัดกรองโลหิตจาง/ติดเชื้อเบื้องต้น)"),
            ("UA", "พื้นฐาน", "ตรวจปัสสาวะ (คัดกรองความผิดปกติทางเดินปัสสาวะ/ไตเบื้องต้น)"),
            ("CXR", "พื้นฐาน", "เอกซเรย์ปอด (คัดกรองความผิดปกติทรวงอก/ปอด)"),
            ("FBS", "เบาหวาน", "น้ำตาลหลังอดอาหาร (คัดกรองเบาหวานเบื้องต้น)"),
            ("Uric acid", "เมตาบอลิก", "ประเมินความเสี่ยงเกาต์/กรดยูริกสูง"),
            ("BUN", "ไต", "ประเมินการทำงานของไตเบื้องต้น"),
            ("Creatinine", "ไต", "ประเมินการทำงานของไตเบื้องต้น"),
            ("Total cholesterol", "ไขมัน", "ไขมันรวม (คัดกรองความเสี่ยงหลอดเลือด)"),
            ("Triglyceride (TG)", "ไขมัน", "ไตรกลีเซอไรด์ (สัมพันธ์กับความเสี่ยงเมตาบอลิก/ตับไขมัน)"),
        ],
    },
    "Standard (649)": {
        "price": 649,
        "includes": [
            ("ตรวจร่างกายโดยแพทย์", "พื้นฐาน", "ตรวจร่างกายทั่วไปโดยแพทย์"),
            ("CBC", "พื้นฐาน", "ตรวจความสมบูรณ์ของเม็ดเลือด (คัดกรองโลหิตจาง/ติดเชื้อเบื้องต้น)"),
            ("UA", "พื้นฐาน", "ตรวจปัสสาวะ (คัดกรองความผิดปกติทางเดินปัสสาวะ/ไตเบื้องต้น)"),
            ("CXR", "พื้นฐาน", "เอกซเรย์ปอด (คัดกรองความผิดปกติทรวงอก/ปอด)"),
            ("FBS", "เบาหวาน", "น้ำตาลหลังอดอาหาร (คัดกรองเบาหวานเบื้องต้น)"),
            ("Uric acid", "เมตาบอลิก", "ประเมินความเสี่ยงเกาต์/กรดยูริกสูง"),
            ("BUN", "ไต", "ประเมินการทำงานของไตเบื้องต้น"),
            ("Creatinine", "ไต", "ประเมินการทำงานของไตเบื้องต้น"),
            ("Total cholesterol", "ไขมัน", "ไขมันรวม (คัดกรองความเสี่ยงหลอดเลือด)"),
            ("Triglyceride (TG)", "ไขมัน", "ไตรกลีเซอไรด์ (สัมพันธ์กับความเสี่ยงเมตาบอลิก/ตับไขมัน)"),
            ("HDL-C", "ไขมัน", "ไขมันดี ช่วยประเมินความเสี่ยงหลอดเลือดได้แม่นขึ้น"),
            ("Direct LDL-C", "ไขมัน", "ไขมันเลวแบบตรวจตรง เหมาะเมื่ออยากได้ LDL ชัดเจน"),
            ("AST", "ตับ", "เอนไซม์ตับ (บาดเจ็บของเซลล์ตับ)"),
            ("ALT", "ตับ", "เอนไซม์ตับ (บาดเจ็บของเซลล์ตับ)"),
            ("ALP", "ตับ/ทางเดินน้ำดี", "เอนไซม์ตับ/ทางเดินน้ำดี (ใช้ร่วมกับตัวอื่นในการประเมิน)"),
        ],
    },
    "ข้าราชการ <35 (เบิกจ่ายตรง)": {
        "price": 580,
        "includes": [
            ("ตรวจร่างกายโดยแพทย์", "พื้นฐาน", "ตรวจร่างกายทั่วไปโดยแพทย์", 0),
            ("CXR (รหัส 31001)", "พื้นฐาน", "เอกซเรย์ปอด (คัดกรองความผิดปกติทรวงอก/ปอด)", 170),
            ("UA (รหัส 31001)", "พื้นฐาน", "ตรวจปัสสาวะ (Urine analysis)", 50),
            ("Stool exam + Occult blood (รหัส 31201/31203)", "พื้นฐาน", "ตรวจอุจจาระพร้อมตรวจเลือดแฝง", 70),
            ("CBC (รหัส 30101)", "พื้นฐาน", "ตรวจความสมบูรณ์ของเม็ดเลือด (CBC Automation)", 90),
            ("ตรวจภายใน (รหัส 55620)", "สตรี", "ตรวจภายในโดยแพทย์ (เฉพาะเพศหญิง)", 100),
            ("Pap Smear (รหัส 38302)", "สตรี", "คัดกรองมะเร็งปากมดลูก", 100),
        ],
    },
    "ข้าราชการ ≥35 (เบิกจ่ายตรง)": {
        "price": 1050,
        "includes": [
            ("ตรวจร่างกายโดยแพทย์", "พื้นฐาน", "ตรวจร่างกายทั่วไปโดยแพทย์", 0),
            ("CXR (รหัส 31001)", "พื้นฐาน", "เอกซเรย์ปอด (คัดกรองความผิดปกติทรวงอก/ปอด)", 170),
            ("UA (รหัส 31001)", "พื้นฐาน", "ตรวจปัสสาวะ (Urine analysis)", 50),
            ("Stool exam + Occult blood (รหัส 31201/31203)", "พื้นฐาน", "ตรวจอุจจาระพร้อมตรวจเลือดแฝง", 70),
            ("CBC (รหัส 30101)", "พื้นฐาน", "ตรวจความสมบูรณ์ของเม็ดเลือด (CBC Automation)", 90),
            ("ตรวจภายใน (รหัส 55620)", "สตรี", "ตรวจภายในโดยแพทย์ (เฉพาะเพศหญิง)", 100),
            ("Pap Smear (รหัส 38302)", "สตรี", "คัดกรองมะเร็งปากมดลูก", 100),
            ("Glucose (รหัส 32203)", "เคมีเลือด", "น้ำตาลในเลือด (FBS/Glucose)", 40),
            ("Cholesterol (รหัส 32501)", "ไขมัน", "ไขมันรวม", 60),
            ("Triglyceride (รหัส 32502)", "ไขมัน", "ไตรกลีเซอไรด์", 60),
            ("BUN (รหัส 32201)", "ไต", "ประเมินการทำงานของไต", 50),
            ("Creatinine (รหัส 32202)", "ไต", "ประเมินการทำงานของไต", 50),
            ("AST (รหัส 32310)", "ตับ", "เอนไซม์ตับ", 50),
            ("ALT (รหัส 32311)", "ตับ", "เอนไซม์ตับ", 50),
            ("ALP (รหัส 32309)", "ตับ/ทางเดินน้ำดี", "เอนไซม์ตับ/ทางเดินน้ำดี", 50),
            ("Uric acid (รหัส 32205)", "เมตาบอลิก", "ประเมินความเสี่ยงกรดยูริกสูง", 60),
        ],
    },
}

# Add-on master
# note: ราคาอัปเกรด LFT panel สำหรับ Standard = 170 (290 - 120)
ADDONS = [
    # ไขมัน
    dict(id="HDL", name="HDL-C", category="ไขมัน", price=100,
         purpose="ตรวจไขมันดี เพื่อประเมินความเสี่ยงหัวใจ/หลอดเลือดให้ครบขึ้น เหมาะกับผู้ที่ตรวจไขมันพื้นฐานแล้วอยากรู้ภาพรวมชัดเจน"),
    dict(id="LDL", name="Direct LDL-C", category="ไขมัน", price=150,
         purpose="ตรวจไขมันเลวแบบตรง เห็นค่าชัดเจน เหมาะกับผู้ที่กังวลความเสี่ยงหลอดเลือดหรือมีไขมันสูง"),
    dict(id="LIPID_UP", name="อัปเกรดไขมันครบ (HDL + Direct LDL)", category="ไขมัน", price=250,
         purpose="อัปเกรดให้ชุดไขมันครบทั้งดีและเลว เหมาะกับผู้ซื้อ Basic ที่ต้องการประเมินไขมันอย่างเต็มรูปแบบ",
         bundle=True, bundle_items=["HDL", "LDL"]),
    # ตับ
    dict(id="ENZ_LIVER", name="การทำงานของตับเบื้องต้น (AST + ALT + ALP)", category="ตับ", price=120,
         purpose="คัดกรองการอักเสบ/บาดเจ็บของตับเบื้องต้น เหมาะกับผู้ซื้อ Basic หรือผู้ที่ดื่มแอลกอฮอล์"),
    dict(id="GGT", name="GGT", category="ตับ/ทางเดินน้ำดี", price=130,
         purpose="ช่วยประเมินตับและทางเดินน้ำดี เหมาะกับผู้ดื่มแอลกอฮอล์บ่อย หรือสงสัยปัญหาทางเดินน้ำดี"),
    dict(id="LFT_PANEL", name="การทำงานของตับแบบละเอียด (LFT)", category="ตับ (ขยาย)", price=290, price_if_standard=170,
         purpose="ตรวจตับแบบละเอียด เพิ่มบิลิรูบินและโปรตีน/อัลบูมิน เหมาะกับผู้มีปัญหาตับเดิม/ใช้ยาหลายชนิด/อยากตรวจเชิงลึก"),
    # ไต
    dict(id="ACR", name="Urine ACR / Microalbumin", category="ไต", price=310,
         purpose="คัดกรองไตเสื่อมระยะแรก เหมาะกับผู้เป็นเบาหวาน/ความดัน หรือมีประวัติไตในครอบครัว"),
    dict(id="ELECT", name="Electrolytes (Na/K/Cl/CO2)", category="ไต/เกลือแร่", price=80,
         purpose="ตรวจสมดุลเกลือแร่ในเลือด เหมาะกับผู้สูงอายุ ผู้กินยาความดัน หรือผู้มีโรคไต"),
    # ไวรัสตับ
    dict(id="HBsAg_strip", name="HBsAg (strip)", category="ไวรัสตับ", price=130,
         purpose="คัดกรองไวรัสตับอักเสบบีเบื้องต้น เหมาะกับผู้ไม่เคยตรวจหรือไม่แน่ใจภูมิคุ้มกัน"),
    dict(id="HBsAg_quant", name="HBsAg (quantitative)", category="ไวรัสตับ", price=600,
         purpose="ตรวจเชิงปริมาณไวรัสตับอักเสบบี ใช้เมื่อแพทย์ต้องการข้อมูลเชิงลึกหรือเคยมีผลผิดปกติ"),
    dict(id="AntiHCV", name="Anti-HCV", category="ไวรัสตับ", price=300,
         purpose="คัดกรองไวรัสตับอักเสบซี เหมาะกับผู้ที่เคยมีความเสี่ยงหรือไม่เคยตรวจมาก่อน"),
    dict(id="HAV_IGM", name="HAV IgM", category="ไวรัสตับ", price=400,
         purpose="คัดกรองการติดเชื้อไวรัสตับอักเสบเอระยะเฉียบพลัน เหมาะกับผู้ที่มีอาการตาเหลือง ตัวเหลือง หรือสงสัยติดเชื้ออาหาร/น้ำไม่สะอาด"),
    # ต่อมไทรอยด์
    dict(id="THYROID_PANEL", name="ชุดตรวจไทรอยด์ (TSH + FT3 + FT4)", category="ไทรอยด์", price=490,
         purpose="ตรวจฮอร์โมนไทรอยด์ครบชุดเพื่อประเมินภาวะไทรอยด์ต่ำ/เกิน เหมาะกับผู้มีอาการใจสั่น เหนื่อยง่าย น้ำหนักเปลี่ยนผิดปกติ และรวมตรวจร่างกายโดยแพทย์"),
    # หัวใจ
    dict(id="EKG", name="EKG 12 lead", category="หัวใจ", price=200,
         purpose="คัดกรองจังหวะหัวใจผิดปกติ เหมาะกับผู้มีอาการเจ็บหน้าอก ใจสั่น หรืออายุมากขึ้น"),
    # มะเร็ง/คัดกรองเฉพาะกลุ่ม
    dict(id="PSA", name="PSA (Total)", category="ต่อมลูกหมาก", price=300,
         purpose="คัดกรองความเสี่ยงต่อมลูกหมาก เหมาะกับผู้ชายอายุ 50+ หรือมีประวัติครอบครัว"),
    dict(id="AFP", name="AFP", category="Tumor marker", price=250,
         purpose="ตรวจค่าบ่งชี้มะเร็งตับ/โรคตับบางชนิด เพื่อใช้ประกอบการประเมิน เหมาะกับผู้มีปัจจัยเสี่ยงโรคตับ"),
    dict(id="CEA", name="CEA", category="Tumor marker", price=280,
         purpose="ตรวจค่าบ่งชี้มะเร็งบางชนิด เพื่อใช้ประกอบการประเมิน (ควรพิจารณาตามคำแนะนำแพทย์)"),
    # กระดูก
    dict(id="BMD", name="ตรวจมวลกระดูก (BMD) - เงินสด", category="กระดูก", price=1000,
         purpose="ประเมินความเสี่ยงกระดูกพรุน เหมาะกับหญิงหลังหมดประจำเดือน ผู้สูงอายุ หรือมีปัจจัยเสี่ยง"),
    # เก๊าต์
    dict(id="URIC_ACID_ADDON", name="Uric acid", category="ประเมินความเสี่ยงเก๊าต์", price=60,
         purpose="ตรวจกรดยูริกในเลือด เพื่อประเมินความเสี่ยงเก๊าต์ เหมาะกับผู้มีอาการปวดข้อหรือทานอาหารพิวรีนสูงบ่อย"),
]

# -----------------------------
# Helpers
# -----------------------------
def get_base_key():
    return st.session_state.get("base_choice", list(BASE_PACKAGES.keys())[0])

def get_base_includes(base_key: str) -> list[tuple]:
    includes = list(BASE_PACKAGES[base_key]["includes"])
    if base_key.startswith("ข้าราชการ"):
        gender = st.session_state.get("civil_gender", "หญิง")
        if gender == "ชาย":
            includes = [row for row in includes if not (row[0].startswith("ตรวจภายใน") or row[0].startswith("Pap Smear"))]
    return includes

def base_included_names(base_key: str) -> set[str]:
    names = {row[0] for row in get_base_includes(base_key)}
    if base_key.startswith("ข้าราชการ ≥35"):
        names.add("Uric acid")
    return names

def get_addon_price(addon: dict, base_key: str) -> int:
    if (base_key.startswith("Standard") or base_key.startswith("ข้าราชการ ≥35")) and "price_if_standard" in addon and addon["price_if_standard"] is not None:
        return int(addon["price_if_standard"])
    return int(addon["price"])

def included_badge(text: str) -> str:
    return f"✅ รวมในแพ็กเกจแล้ว: {text}"

def money(x: int) -> str:
    return f"{x:,.0f}"

def build_pdf_report(
    base_choice: str,
    base_price: int,
    addon_total: int,
    total: int,
    exam_date: pd.Timestamp,
    base_df: pd.DataFrame,
    addon_rows: list[dict],
) -> bytes | None:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        return None

    base_rows_count = len(base_df.index)
    addon_rows_count = len(addon_rows)
    total_rows = base_rows_count + addon_rows_count
    compact_mode = total_rows >= 12

    font_candidates = [
        (os.path.join("assets", "fonts", "Sarabun-Regular.ttf"), os.path.join("assets", "fonts", "Sarabun-Bold.ttf")),
        (r"C:\Windows\Fonts\THSarabunNew.ttf", r"C:\Windows\Fonts\THSarabunNew Bold.ttf"),
        (r"C:\Windows\Fonts\THSarabunNew.ttf", r"C:\Windows\Fonts\THSarabunNew.ttf"),
        (r"C:\Windows\Fonts\Tahoma.ttf", r"C:\Windows\Fonts\Tahoma.ttf"),
    ]
    font_path = None
    bold_path = None
    for regular, bold in font_candidates:
        if os.path.exists(regular):
            font_path = regular
            bold_path = bold if os.path.exists(bold) else regular
            break
    try:
        body_size = 24 if compact_mode else 28
        title_size = 32 if compact_mode else 36
        font = ImageFont.truetype(font_path, body_size) if font_path else ImageFont.load_default()
        bold_font = ImageFont.truetype(bold_path or font_path, body_size) if font_path else ImageFont.load_default()
        title_font = ImageFont.truetype(bold_path or font_path, title_size) if font_path else ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()
        bold_font = font
        title_font = font

    page_w, page_h = 1240, 1754  # A4-ish at 150 DPI
    margin_x = 60 if compact_mode else 80
    margin_y = 60 if compact_mode else 80
    line_h = int(font.getbbox("ไทยA")[3] - font.getbbox("ไทยA")[1]) + (6 if compact_mode else 10)
    cell_pad_y = 6 if compact_mode else 8
    cell_pad_x = 6 if compact_mode else 8

    def wrap_text(text: str, draw: ImageDraw.ImageDraw, fnt: ImageFont.ImageFont, max_w: int) -> list[str]:
        if draw.textlength(text, font=fnt) <= max_w:
            return [text]
        words = text.split(" ")
        if len(words) > 1:
            lines = []
            cur = ""
            for w in words:
                trial = f"{cur} {w}".strip()
                if draw.textlength(trial, font=fnt) <= max_w:
                    cur = trial
                else:
                    if cur:
                        lines.append(cur)
                    if draw.textlength(w, font=fnt) <= max_w:
                        cur = w
                    else:
                        buf = ""
                        for ch in w:
                            trial2 = f"{buf}{ch}"
                            if draw.textlength(trial2, font=fnt) <= max_w:
                                buf = trial2
                            else:
                                if buf:
                                    lines.append(buf)
                                buf = ch
                        cur = buf
            if cur:
                lines.append(cur)
            return lines

        lines = []
        buf = ""
        for ch in text:
            trial = f"{buf}{ch}"
            if draw.textlength(trial, font=fnt) <= max_w:
                buf = trial
            else:
                if buf:
                    lines.append(buf)
                buf = ch
        if buf:
            lines.append(buf)
        return lines

    def new_page():
        img = Image.new("RGB", (page_w, page_h), color="white")
        return img, ImageDraw.Draw(img), margin_y

    def draw_table(draw, start_y, headers, rows, col_widths):
        nonlocal img
        y = start_y

        def calc_row_height(cells, is_header=False):
            max_lines = 1
            fnt = bold_font if is_header else font
            for i, cell in enumerate(cells):
                cell_lines = wrap_text(str(cell), draw, fnt, col_widths[i] - (cell_pad_x * 2))
                max_lines = max(max_lines, len(cell_lines))
            return (line_h * max_lines) + (cell_pad_y * 2)

        def render_row(cells, is_header=False):
            nonlocal y, draw
            row_lines = []
            fnt = bold_font if is_header else font
            max_lines = 1
            for i, cell in enumerate(cells):
                cell_lines = wrap_text(str(cell), draw, fnt, col_widths[i] - (cell_pad_x * 2))
                row_lines.append(cell_lines)
                max_lines = max(max_lines, len(cell_lines))
            row_h = (line_h * max_lines) + (cell_pad_y * 2)
            x = margin_x
            for i, cell_lines in enumerate(row_lines):
                draw.rectangle([x, y, x + col_widths[i], y + row_h], outline="#d1d5db")
                for idx, line in enumerate(cell_lines):
                    draw.text((x + cell_pad_x, y + cell_pad_y + (idx * line_h)), line, font=fnt, fill="black")
                x += col_widths[i]
            y += row_h

        def ensure_space(row_h):
            nonlocal img, draw, y
            if y + row_h > page_h - margin_y:
                pages.append(img)
                img, draw, y = new_page()
                return True
            return False

        header_h = calc_row_height(headers, is_header=True)
        if ensure_space(header_h):
            pass
        render_row(headers, is_header=True)
        for r in rows:
            row_h = calc_row_height(r, is_header=False)
            if ensure_space(row_h):
                header_h = calc_row_height(headers, is_header=True)
                ensure_space(header_h)
                render_row(headers, is_header=True)
            render_row(r, is_header=False)
        return y

    pages = []
    img, draw, y = new_page()

    draw.text((margin_x, y), "สรุปการตรวจสุขภาพ", font=title_font, fill="black")
    y += line_h * 2
    meta_lines = [
        f"วันที่มาตรวจ: {exam_date.strftime('%d/%m/%Y')}",
        f"Base package: {base_choice} = {money(base_price)} บาท",
        f"Add-on รวม: {money(addon_total)} บาท",
        f"รวมสุทธิ: {money(total)} บาท",
    ]
    for line in meta_lines:
        for part in wrap_text(line, draw, font, page_w - (margin_x * 2)):
            draw.text((margin_x, y), part, font=font, fill="black")
            y += line_h
    y += line_h if not compact_mode else int(line_h * 0.6)

    # Base package table
    draw.text((margin_x, y), "รายการใน Base package", font=bold_font, fill="black")
    y += line_h + (2 if compact_mode else 6)
    if base_choice.startswith("ข้าราชการ"):
        headers = ["รายการ", "หมวด", "ตรวจเพื่ออะไร", "ราคาเบิก (บาท)"]
        col_widths = [300, 140, 500, 140]
    else:
        headers = ["รายการ", "หมวด", "ตรวจเพื่ออะไร"]
        col_widths = [300, 140, 640]
    base_rows = base_df.values.tolist()

    y = draw_table(draw, y, headers, base_rows, col_widths)

    y += line_h if not compact_mode else int(line_h * 0.6)

    # Add-on table
    draw.text((margin_x, y), "รายการ Add-on ที่เลือก", font=bold_font, fill="black")
    y += line_h + (2 if compact_mode else 6)
    addon_headers = ["หมวด", "รายการ", "ตรวจเพื่ออะไร", "ราคา (บาท)"]
    addon_col_widths = [160, 320, 460, 140]
    addon_table_rows = []
    for r in addon_rows:
        addon_table_rows.append([r["หมวด"], r["รายการ"], r["ตรวจเพื่ออะไร"], money(int(r["ราคา (บาท)"]))])
    if not addon_table_rows:
        addon_table_rows = [["-", "-", "ไม่มีรายการ Add-on ที่เลือก", "-"]]

    y = draw_table(draw, y, addon_headers, addon_table_rows, addon_col_widths)

    pages.append(img)
    buf = BytesIO()
    pages[0].save(buf, format="PDF", save_all=True, append_images=pages[1:])
    return buf.getvalue()

# -----------------------------
# UI
# -----------------------------
st.title("🩺 โปรแกรมตรวจสุขภาพ + Add-on")
st.caption("เลือกแพ็กเกจพื้นฐาน แล้วติ๊ก Add-on ที่ต้องการ ระบบจะแสดงราคารวมและสรุปรายการให้ทันที")

left, right = st.columns([1.2, 1.4])

with left:
    if st.button("รีเซ็ตการเลือกทั้งหมด"):
        st.session_state.pop("selected_addons", None)
        st.session_state["base_choice"] = list(BASE_PACKAGES.keys())[0]
        st.rerun()

    base_choice = st.selectbox("เลือก Base package", list(BASE_PACKAGES.keys()), key="base_choice")
    base_price = BASE_PACKAGES[base_choice]["price"]

    if base_choice.startswith("ข้าราชการ"):
        st.radio("เพศ (สำหรับสิทธิ์ข้าราชการ)", ["หญิง", "ชาย"], key="civil_gender", horizontal=True)

    st.subheader("สิ่งที่รวมในแพ็กเกจ")
    if base_choice.startswith("ข้าราชการ"):
        inc_df = pd.DataFrame(get_base_includes(base_choice), columns=["รายการ", "หมวด", "ตรวจเพื่ออะไร", "ราคาเบิก (บาท)"])
    else:
        inc_df = pd.DataFrame(get_base_includes(base_choice), columns=["รายการ", "หมวด", "ตรวจเพื่ออะไร"])
    if base_choice.startswith("ข้าราชการ"):
        inc_html = inc_df.to_html(index=False, classes="inc-table civil-table", border=0)
    else:
        inc_html = inc_df.to_html(index=False, classes="inc-table", border=0)
    st.markdown(inc_html, unsafe_allow_html=True)

    st.subheader("เงื่อนไขราคาอัตโนมัติ")
    st.markdown(
        "- หากเลือก **Standard** แล้วติ๊ก **LFT Panel (ตับแบบขยาย)** ระบบจะคิดเป็น **ราคาอัปเกรด 170** (เพิ่ม bilirubin + protein/albumin)\n"
        "- รายการที่รวมในแพ็กเกจแล้วจะไม่ถูกคิดเงินซ้ำ"
    )
    if base_choice.startswith("ข้าราชการ"):
        st.info(
            "กรณีสิทธิ์ข้าราชการ: ลูกค้าชำระเงินสดกับโรงพยาบาล แล้วนำใบเสร็จไปเบิกกับต้นสังกัดได้เฉพาะรายการในแพ็กเกจ "
            "ส่วนรายการ Add-on จะเบิกคืนไม่ได้",
            icon="ℹ️"
        )
    st.metric("ราคา Base package", f"{money(base_price)} บาท")

with right:
    st.subheader("เลือก Add-on (แยกหมวด)")
    st.caption("เลือกตรวจเพิ่มเติมตามความเสี่ยงหรือความกังวลของแต่ละคน ดูคำอธิบายใต้ชื่อหมวดได้เลย")

    included = base_included_names(base_choice)

    # Build category mapping (excluding bundles from list display; we'll show bundles but manage overlap)
    addons_by_cat = {}
    for a in ADDONS:
        addons_by_cat.setdefault(a["category"], []).append(a)

    selected_ids = {a["id"] for a in ADDONS if st.session_state.get(f"pick_{a['id']}", False)}

    # When base changes, keep selections but we'll ignore included items/bundle rules in calculation
    category_labels = {
        "Tumor marker": "ค่าบ่งชี้มะเร็ง",
        "กระดูก": "มวลกระดูก",
        "ตับ": "การทำงานของตับ",
        "ตับ (ขยาย)": "การทำงานของตับ",
        "ตับ/ทางเดินน้ำดี": "การทำงานของตับ",
        "ไต": "การทำงานของไต",
        "ไต/เกลือแร่": "การทำงานของไต",
    }
    category_desc_display = {
        "การทำงานของตับ": "ตรวจตับและทางเดินน้ำดี ตั้งแต่พื้นฐานถึงแบบขยาย เลือกได้ตามความเสี่ยง",
        "การทำงานของไต": "ตรวจการทำงานของไตและสมดุลเกลือแร่ในเลือด",
    }
    category_desc = {
        "ไขมัน": "ตรวจไขมันในเลือด เพื่อประเมินความเสี่ยงโรคหัวใจและหลอดเลือด",
        "ตับ": "ตรวจเอนไซม์ตับ เพื่อคัดกรองการอักเสบหรือการทำงานของตับเบื้องต้น",
        "ตับ (ขยาย)": "ตรวจตับแบบละเอียด เพิ่มข้อมูลตับเชิงลึกมากขึ้น",
        "ไต": "ตรวจการทำงานของไตและคัดกรองไตเสื่อมระยะเริ่มต้น",
        "ไต/เกลือแร่": "ตรวจสมดุลเกลือแร่ในเลือด",
        "ไวรัสตับ": "ตรวจคัดกรองไวรัสตับอักเสบบี/ซี",
        "ไทรอยด์": "ตรวจการทำงานของต่อมไทรอยด์",
        "หัวใจ": "ตรวจคลื่นไฟฟ้าหัวใจเพื่อคัดกรองความผิดปกติของจังหวะหัวใจ",
        "ต่อมลูกหมาก": "ตรวจคัดกรองความเสี่ยงต่อมลูกหมากในผู้ชาย",
        "Tumor marker": "ตรวจค่าบ่งชี้มะเร็ง เพื่อใช้ประกอบการประเมิน (เหมาะกับผู้มีความเสี่ยงหรืออยากตรวจเชิงลึก)",
        "กระดูก": "ตรวจมวลกระดูก เพื่อประเมินความเสี่ยงกระดูกพรุน",
    }
    # UI per category (grouped by display label)
    category_groups = {}
    display_order = []
    for cat in sorted(addons_by_cat.keys()):
        display_cat = category_labels.get(cat, cat)
        if display_cat not in category_groups:
            category_groups[display_cat] = []
            display_order.append(display_cat)
        category_groups[display_cat].append(cat)

    expanded_cats = {"ไขมัน", "ตับ (ขยาย)", "ไต"}
    for display_cat in display_order:
        cats = category_groups[display_cat]
        is_expanded = any(cat in expanded_cats for cat in cats)
        with st.expander(display_cat, expanded=is_expanded):
            desc = category_desc_display.get(display_cat) or category_desc.get(cats[0])
            if desc:
                st.caption(desc)
            for cat in cats:
                items = addons_by_cat[cat]
                for a in items:
                    # Bundle: show as its own checkbox; if selected, we will suppress component items cost later
                    a_name = a["name"]
                    a_price = get_addon_price(a, base_choice)
                    is_bundle = bool(a.get("bundle", False))
                    # Disable if already included (exact name match) AND not a special pricing upgrade (like LFT panel)
                    is_included = (a_name in included)
                    # Special-case: LFT panel is never "included"; it has upgrade price.
                    if a["id"] == "LFT_PANEL":
                        is_included = False
                    # Standard and civil servant >=35 already include AST/ALT/ALP, so hide enzyme add-on.
                    if (base_choice.startswith("Standard") or base_choice.startswith("ข้าราชการ ≥35")) and a["id"] == "ENZ_LIVER":
                        is_included = True

                    help_txt = a["purpose"]
                    label = f"{a_name} — {money(a_price)} บาท: {help_txt}"
                    is_mutex = False
                    if base_choice.startswith("Basic") or base_choice.startswith("ข้าราชการ <35"):
                        if "ENZ_LIVER" in selected_ids and "LFT_PANEL" in selected_ids:
                            selected_ids.discard("ENZ_LIVER")
                        if a["id"] == "ENZ_LIVER" and "LFT_PANEL" in selected_ids:
                            is_mutex = True
                        if a["id"] == "LFT_PANEL" and "ENZ_LIVER" in selected_ids:
                            is_mutex = True
                    if is_included:
                        st.checkbox(included_badge(a_name), value=True, disabled=True, key=f"inc_{a['id']}")
                    else:
                        default_val = a["id"] in selected_ids
                        picked = st.checkbox(label, value=default_val, disabled=(is_mutex and not default_val), key=f"pick_{a['id']}")
                        if picked:
                            selected_ids.add(a["id"])
                            if base_choice.startswith("Basic") or base_choice.startswith("ข้าราชการ <35"):
                                if a["id"] == "ENZ_LIVER":
                                    selected_ids.discard("LFT_PANEL")
                                if a["id"] == "LFT_PANEL":
                                    selected_ids.discard("ENZ_LIVER")
                        else:
                            selected_ids.discard(a["id"])

    # Persist selection
    st.session_state["selected_addons"] = sorted(selected_ids)

st.divider()

# -----------------------------
# Price calculation with bundle logic
# -----------------------------
id_map = {a["id"]: a for a in ADDONS}

# Remove included items if any got selected somehow
selected_effective = []
for aid in selected_ids:
    a = id_map.get(aid)
    if not a:
        continue
    if a["name"] in included and aid != "LFT_PANEL":
        continue
    selected_effective.append(a)

# Handle bundle: if bundle selected, drop its component items to avoid double-charge
bundles = [a for a in selected_effective if a.get("bundle", False)]
bundle_components = set()
for b in bundles:
    for comp in b.get("bundle_items", []):
        bundle_components.add(comp)

final_addons = []
for a in selected_effective:
    if a["id"] in bundle_components:
        # if component selected but bundle also selected, ignore component
        if any(b.get("bundle", False) and a["id"] in b.get("bundle_items", []) for b in bundles):
            continue
    final_addons.append(a)

rows = []
addon_total = 0
for a in final_addons:
    p = get_addon_price(a, base_choice)
    addon_total += p
    # Friendly name for LFT upgrade
    display_name = a["name"]
    if a["id"] == "LFT_PANEL" and base_choice.startswith("Standard"):
        display_name = "LFT Panel (อัปเกรดสำหรับ Standard: เพิ่ม bilirubin + protein/albumin)"
    rows.append({
        "หมวด": a["category"],
        "รายการ": display_name,
        "ตรวจเพื่ออะไร": a["purpose"],
        "ราคา (บาท)": p
    })

total = base_price + addon_total

st.divider()
st.subheader("สรุปรายการที่เลือกและราคารวม")

colA, colB, colC = st.columns([1, 1, 2])
with colA:
    st.metric("ค่า Add-on รวม", f"{money(addon_total)} บาท")
with colB:
    st.metric("ราคารวมสุทธิ", f"{money(total)} บาท")
with colC:
    st.info("Tip: ถ้าต้องการให้ลูกค้ารู้สึก “ซื้อเป็นชุดคุ้มกว่า” สามารถตั้งราคาชุด (Bundle) ให้ต่ำกว่ารวมรายตัว 10–15% ได้", icon="💡")

if rows:
    out_df = pd.DataFrame(rows).sort_values(["หมวด", "รายการ"])
    out_html = out_df.to_html(index=False, classes="inc-table", border=0)
    st.markdown(out_html, unsafe_allow_html=True)
else:
    st.write("ยังไม่ได้เลือก Add-on")

# Download summary
st.markdown("### ดาวน์โหลดสรุป")
exam_date = st.date_input("วันที่มาตรวจ", value=pd.Timestamp.today().date())
summary_text_lines = [
    f"วันที่มาตรวจ: {exam_date.strftime('%d/%m/%Y')}",
    f"Base package: {base_choice} = {money(base_price)} บาท",
    f"Add-on รวม: {money(addon_total)} บาท",
    f"รวมสุทธิ: {money(total)} บาท",
    "",
    "รายการ Add-on:"
]
if rows:
    for r in rows:
        summary_text_lines.append(f"- [{r['หมวด']}] {r['รายการ']} = {money(int(r['ราคา (บาท)']))} บาท | {r['ตรวจเพื่ออะไร']}")
else:
    summary_text_lines.append("- (ไม่มี)")

summary_text = "\n".join(summary_text_lines)

pdf_bytes = build_pdf_report(
    base_choice=base_choice,
    base_price=base_price,
    addon_total=addon_total,
    total=total,
    exam_date=pd.Timestamp(exam_date),
    base_df=inc_df,
    addon_rows=rows,
)
spacer_col, download_col1, download_col2, download_col3 = st.columns([6.2, 2.2, 2.0, 1.4])
with download_col1:
    st.download_button(
        label="ดาวน์โหลดไฟล์ข้อความ (TXT)",
        data=summary_text.encode("utf-8"),
        file_name="health_check_summary.txt",
        mime="text/plain"
    )
with download_col2:
    if rows:
        csv_bytes = out_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="ดาวน์โหลดไฟล์ตาราง (CSV)",
            data=csv_bytes,
            file_name="health_check_summary.csv",
            mime="text/csv"
        )
    else:
        st.download_button(
            label="ดาวน์โหลดไฟล์ตาราง (CSV)",
            data="",
            file_name="health_check_summary.csv",
            mime="text/csv",
            disabled=True
        )
with download_col3:
    if pdf_bytes:
        st.download_button(
            label="ดาวน์โหลดไฟล์ PDF",
            data=pdf_bytes,
            file_name="health_check_summary.pdf",
            mime="application/pdf"
        )
    else:
        st.caption("หมายเหตุ: หากต้องการดาวน์โหลด PDF ต้องติดตั้ง Pillow (pip install pillow)")

st.caption("หมายเหตุ: รายการ Tumor marker มีโอกาสผลบวกปลอมได้ ควรมีข้อความกำกับบนสื่อ/ใบเสนอราคาเพื่อการสื่อสารที่ปลอดภัย")
