from io import BytesIO

import httpx
from fastapi import FastAPI, HTTPException
from openpyxl import load_workbook

CKAN_API = "https://data.go.th/api/3/action"
DATASET = "zoo-visitors2569"
RESOURCE_ID = "0ecc96cf-d914-42a1-b184-dbbd013c3c9c"  # ไฟล์ XLSX รายงานเดือน ก.ค. 2569
SHEET = "statistics"
FISCAL_YEAR = 2569

app = FastAPI(
    title="Zoo Visitors API",
    description="สถิติจำนวนผู้เข้าชมสวนสัตว์ ปีงบประมาณ 2569 "
    "องค์การสวนสัตว์แห่งประเทศไทย ในพระบรมราชูปถัมภ์ (ข้อมูลจาก data.go.th)",
)


def fetch_resource():
    """ถาม data.go.th ว่าไฟล์อยู่ที่ไหน แล้วดาวน์โหลด XLSX มาอ่านชีต statistics"""
    meta = httpx.get(f"{CKAN_API}/resource_show", params={"id": RESOURCE_ID}, timeout=30)
    meta.raise_for_status()
    meta = meta.json()["result"]

    file = httpx.get(meta["url"], timeout=60, follow_redirects=True)
    file.raise_for_status()

    sheet = load_workbook(BytesIO(file.content), read_only=True, data_only=True)[SHEET]
    rows = sheet.iter_rows(values_only=True)
    headers = next(rows)
    records = [
        {h: v for h, v in zip(headers, row) if h is not None}  # ใช้ชื่อคอลัมน์ตามไฟล์จริง
        for row in rows
        if row[0] is not None
    ]
    return meta, records


@app.get("/api/zoo-visitors")
def zoo_visitors():
    try:
        meta, records = fetch_resource()
    except (httpx.HTTPError, KeyError) as e:
        raise HTTPException(status_code=502, detail=f"ดึงข้อมูลจาก data.go.th ไม่สำเร็จ: {e}")

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
        },
        "fiscal_year": FISCAL_YEAR,
        "total": len(records),
        "records": records,
    }
