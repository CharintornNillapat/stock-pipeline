# 📈 Serverless Stock Data Pipeline

> ระบบดึงข้อมูลหุ้นไทยรายวันโดยอัตโนมัติ ประมวลผล เก็บใน GitHub และแสดงผลผ่าน Streamlit Cloud แบบ **0 บาท** ตั้งแต่ต้นจนจบ

![GitHub Actions](https://img.shields.io/github/actions/workflow/status/CharintornNillapat/stock-pipeline/daily_pipeline.yml?label=Daily%20Pipeline&style=flat-square)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

---

## 🌐 Live Dashboard

👉 **[https://stock-pipeline-ccu2i5yaznkqxqbfotgpuz.streamlit.app/](https://stock-pipeline-ccu2i5yaznkqxqbfotgpuz.streamlit.app/)** 

---

## 🏗️ Architecture

```
GitHub Actions (cron: ทุกวันจันทร์–ศุกร์ 18:00 น.)
    │
    ▼
[1] Ingest — yfinance API → data/raw/*.parquet
    │
    ▼
[2] Transform — Pandas (Cleaning + MA_20 + MA_50 + RSI_14 + Signal)
    │
    ▼
[3] Store — git commit → data/processed/*.parquet (GitHub as Free DB)
    │
    ▼
[4] Visualize — Streamlit Cloud reads from GitHub → Live Dashboard
```

---

## 📊 Data Flow

| ขั้นตอน | รายละเอียด |
|--------|-----------|
| **Ingest** | ดึงข้อมูลหุ้น `PTT.BK`, `AOT.BK`, `ADVANC.BK` จาก Yahoo Finance ด้วย `yfinance` แบบ Incremental (ดึงเฉพาะวันที่ยังไม่มี) พร้อม Retry Logic 3 รอบ |
| **Transform** | ทำความสะอาดข้อมูล, คำนวณ MA_20, MA_50, RSI_14 และตรวจจับ Golden Cross / Death Cross อัตโนมัติ |
| **Store** | บันทึกเป็น `.parquet` และ `git push` ขึ้น GitHub ซึ่งทำหน้าที่เป็น Free Database |
| **Visualize** | Streamlit Dashboard แสดง KPI Cards, Candlestick Chart, Volume Chart และตาราง Signal |

---

## 🛠️ Tech Stack

| Category | Tools |
|----------|-------|
| **Language** | Python 3.11 |
| **Data** | yfinance, Pandas, PyArrow |
| **Visualization** | Streamlit, Plotly |
| **Automation** | GitHub Actions (cron schedule) |
| **Storage** | GitHub Repository (.parquet files) |
| **Hosting** | Streamlit Cloud (Free tier) |

---

## 📁 Project Structure

```
stock-pipeline/
├── .github/
│   └── workflows/
│       └── daily_pipeline.yml   # GitHub Actions — รันทุกวันอัตโนมัติ
├── dashboard/
│   └── app.py                   # Streamlit Dashboard
├── data/
│   ├── raw/                     # ข้อมูลดิบจาก API
│   │   ├── PTT.BK.parquet
│   │   ├── AOT.BK.parquet
│   │   └── ADVANC.BK.parquet
│   └── processed/               # ข้อมูลหลัง Transform พร้อม MA, RSI, Signal
│       ├── PTT.BK.parquet
│       ├── AOT.BK.parquet
│       └── ADVANC.BK.parquet
├── pipeline/
│   ├── ingest.py                # ดึงข้อมูลจาก yfinance
│   ├── transform.py             # Cleaning + Feature Engineering
│   └── run_pipeline.py          # Entry point รัน pipeline ทั้งหมด
└── requirements.txt
```

---

## 🚀 Run Locally

```bash
# 1. Clone repo
git clone https://github.com/CharintornNillapat/stock-pipeline.git
cd stock-pipeline

# 2. สร้าง virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# 3. ติดตั้ง dependencies
pip install -r requirements.txt

# 4. รัน pipeline
python pipeline/run_pipeline.py

# 5. เปิด dashboard
streamlit run dashboard/app.py
```

---

## ⚙️ Automated Schedule

Pipeline รันอัตโนมัติผ่าน GitHub Actions ทุกวัน **จันทร์–ศุกร์ เวลา 18:00 น. (ไทย)** หลังตลาดหุ้นปิด

- Commit เฉพาะเมื่อมีข้อมูลใหม่จริงๆ (ป้องกัน commit history รก)
- GitHub Actions ฟรี 2,000 นาที/เดือน — แต่ละ run ใช้แค่ ~2-3 นาที

---

## 📈 Features

- **KPI Cards** — ราคาปิด, % เปลี่ยนแปลง, MA 20, MA 50, RSI 14
- **Candlestick Chart** — พร้อม Moving Average overlay
- **Volume Chart** — แบบ Interactive
- **Signal Detection** — Golden Cross (Bullish) / Death Cross (Bearish) อัตโนมัติ
- **Multi-ticker** — เลือกดูหุ้นได้จาก Sidebar

---

*Built with ♥ as a Portfolio Project · Serverless · Free Tier · End-to-End*
