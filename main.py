import json
from io import BytesIO
from pathlib import Path

import httpx
from fastapi import FastAPI
from openpyxl import load_workbook

CKAN_API = "https://data.go.th/api/3/action"
DATASET = "zoo-visitors2569"
RESOURCE_ID = "0ecc96cf-d914-42a1-b184-dbbd013c3c9c"  # ไฟล์ XLSX รายงานเดือน ก.ค. 2569
SHEET = "statistics"
FISCAL_YEAR = 2569

# สำเนาไฟล์จริงของ resource เดียวกัน (ดาวน์โหลดจาก data.go.th ไว้) ใช้เมื่อเรียกสดไม่ได้
# เพราะ data.go.th ตอบ 403 กับ request จากเซิร์ฟเวอร์ต่างประเทศ เช่น Vercel
DATA_DIR = Path(__file__).parent / "data"
LOCAL_META = DATA_DIR / "resource_show.json"
LOCAL_XLSX = DATA_DIR / f"{RESOURCE_ID}.xlsx"

app = FastAPI(
    title="Zoo Visitors API",
    description="สถิติจำนวนผู้เข้าชมสวนสัตว์ ปีงบประมาณ 2569 "
    "องค์การสวนสัตว์แห่งประเทศไทย ในพระบรมราชูปถัมภ์ (ข้อมูลจาก data.go.th)",
)


def fetch_live():
    """ถาม data.go.th ว่าไฟล์อยู่ที่ไหน แล้วดาวน์โหลด XLSX"""
    meta = httpx.get(f"{CKAN_API}/resource_show", params={"id": RESOURCE_ID}, timeout=30)
    meta.raise_for_status()
    meta = meta.json()["result"]

    file = httpx.get(meta["url"], timeout=60, follow_redirects=True)
    file.raise_for_status()
    return meta, file.content


def read_statistics(xlsx):
    """อ่านชีต statistics โดยใช้ชื่อคอลัมน์ตามไฟล์จริง"""
    sheet = load_workbook(BytesIO(xlsx), read_only=True, data_only=True)[SHEET]
    rows = sheet.iter_rows(values_only=True)
    headers = next(rows)
    return [
        {h: v for h, v in zip(headers, row) if h is not None}
        for row in rows
        if row[0] is not None
    ]


@app.get("/api/zoo-visitors")
def zoo_visitors():
    try:
        meta, xlsx = fetch_live()
        retrieval = {"retrieved_from": "live"}
    except (httpx.HTTPError, KeyError) as e:
        meta = json.loads(LOCAL_META.read_text(encoding="utf-8"))["result"]
        xlsx = LOCAL_XLSX.read_bytes()
        retrieval = {"retrieved_from": "local_copy", "live_error": str(e).splitlines()[0]}

    records = read_statistics(xlsx)
    return {
        "source": {
            "organization": "องค์การสวนสัตว์แห่งประเทศไทย ในพระบรมราชูปถัมภ์",
            "portal": "data.go.th",
            "dataset": DATASET,
            "dataset_url": f"https://data.go.th/dataset/{DATASET}",
            "resource_id": RESOURCE_ID,
            "resource_name": meta["name"],
            "resource_url": meta["url"],
            "last_modified": meta.get("last_modified"),
            "sheet": SHEET,
            **retrieval,
        },
        "fiscal_year": FISCAL_YEAR,
        "total": len(records),
        "records": records,
    }
