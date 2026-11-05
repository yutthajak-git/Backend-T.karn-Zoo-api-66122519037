Zoo Visitors API
================
RESTful API ด้วย Python + FastAPI แสดงรายงานสถิติจำนวนผู้เข้าชมสวนสัตว์ ปีงบประมาณ 2569
ขององค์การสวนสัตว์แห่งประเทศไทย ในพระบรมราชูปถัมภ์ โดยดึงข้อมูลจริงจาก Data.go.th


1. URL สำหรับตรวจงาน
--------------------
API     : https://backend-t-karn-zoo-api-66122519037.vercel.app/api/zoo-visitors
Swagger : https://backend-t-karn-zoo-api-66122519037.vercel.app/docs
GitHub  : https://github.com/yutthajak-git/Backend-T.karn-Zoo-api-66122519037


2. แหล่งข้อมูล
--------------
หน่วยงาน     : องค์การสวนสัตว์แห่งประเทศไทย ในพระบรมราชูปถัมภ์
ชุดข้อมูล     : ข้อมูลรายงานสถิติจำนวนผู้เข้าชมสวนสัตว์ ปีงบประมาณ 2569 (zoo-visitors2569)
               https://data.go.th/dataset/zoo-visitors2569
Resource ID  : 0ecc96cf-d914-42a1-b184-dbbd013c3c9c
               (ข้อมูลรายงานสถิติจำนวนผู้เข้าชมสวนสัตว์ อสส กรกฎาคม 2569, ไฟล์ XLSX, ชีต "statistics")
สัญญาอนุญาต : Creative Commons Attributions

วิธีดึงข้อมูล (ทำใหม่ทุกครั้งที่มีการเรียก API ไม่มีข้อมูลสมมติ)
  1) เรียก CKAN API ของ data.go.th
     GET https://data.go.th/api/3/action/resource_show?id=0ecc96cf-d914-42a1-b184-dbbd013c3c9c
     เพื่อรับชื่อไฟล์ วันที่แก้ไขล่าสุด และ URL ดาวน์โหลด
  2) ดาวน์โหลดไฟล์ XLSX จริงจาก URL ที่ได้
  3) อ่านชีต "statistics" ด้วย openpyxl แล้วส่งกลับเป็น JSON โดยใช้ชื่อคอลัมน์ตามไฟล์ต้นฉบับ
  4) ถ้าเรียกสดไม่สำเร็จ จะอ่านจากสำเนาไฟล์จริงของ resource เดียวกันในโฟลเดอร์ data/ แทน
     (ดาวน์โหลดจาก data.go.th ไว้แล้ว ไฟล์ตรงกับต้นฉบับทุกไบต์)
     เหตุผล: data.go.th อยู่หลัง Cloudflare และตอบ 403 Forbidden กับ request จากเซิร์ฟเวอร์
     ต่างประเทศ เช่น Vercel แต่เรียกจากเครื่องในประเทศไทยได้ปกติ

หมายเหตุ: ไม่ใช้ datastore_search เพราะ Datastore ของ resource นี้มีเฉพาะชีตคำอธิบาย
(Data Dictionary) ไม่มีตัวเลขสถิติ


3. API
------
GET /api/zoo-visitors   คืนข้อมูลสถิติทั้งหมด (63 รายการ = 9 ประเภทผู้เข้าชม x 7 สวนสัตว์/โครงการ)
GET /docs               Swagger UI ของ FastAPI

โครงสร้าง JSON
  source       แหล่งที่มาของข้อมูล (หน่วยงาน, ชุดข้อมูล, resource id, ชื่อไฟล์, URL, วันที่แก้ไขล่าสุด)
    retrieved_from  "live" = เรียกสดจาก data.go.th
                    "local_copy" = อ่านจากสำเนาไฟล์จริงใน data/ (มี live_error บอกสาเหตุที่เรียกสดไม่ได้)
  fiscal_year  ปีงบประมาณ (2569)
  total        จำนวนรายการ
  records      รายการสถิติ แต่ละรายการมี รายการ, สวนสัตว์, ปีงบประมาณ และจำนวนผู้เข้าชมรายเดือน
               ต.ค. 68 - ก.ย. 69

ค่า null = เดือนที่ยังไม่มีข้อมูลในไฟล์ (ไฟล์นี้เป็นรายงานถึงเดือน ก.ค. 69 จึงยังไม่มี ส.ค.-ก.ย. 69)


4. ตัวอย่าง JSON Response (ตัดมา 2 รายการแรก)
----------------------------------------------
{
  "source": {
    "organization": "องค์การสวนสัตว์แห่งประเทศไทย ในพระบรมราชูปถัมภ์",
    "portal": "data.go.th",
    "dataset": "zoo-visitors2569",
    "dataset_url": "https://data.go.th/dataset/zoo-visitors2569",
    "resource_id": "0ecc96cf-d914-42a1-b184-dbbd013c3c9c",
    "resource_name": "ข้อมูลรายงานสถิติจำนวนผู้เข้าชมสวนสัตว์ อสส กรกฎาคม 2569",
    "resource_url": "https://data.go.th/dataset/970c2632-1669-44aa-80c5-2c20cb2295e4/resource/0ecc96cf-d914-42a1-b184-dbbd013c3c9c/download/-.-..69.xlsx",
    "last_modified": "2026-08-11T10:31:06.429240",
    "sheet": "statistics",
    "retrieved_from": "live"
  },
  "fiscal_year": 2569,
  "total": 63,
  "records": [
    {
      "รายการ": "ผู้ใหญ่",
      "สวนสัตว์": "สวนสัตว์เปิดเขาเขียว",
      "ปีงบประมาณ": 2569,
      "ต.ค. 68": 59893,
      "พ.ย. 68": 31752,
      "ธ.ค. 68": 42297,
      "ม.ค.69": 27918,
      "ก.พ. 69": 25028,
      "มี.ค. 69": 37140,
      "เม.ย. 69": 47375,
      "พ.ค. 69": 43371,
      "มิ.ย. 69": 31181,
      "ก.ค. 69": 43190,
      "ส.ค. 69": null,
      "ก.ย. 69": null
    },
    {
      "รายการ": "เด็ก",
      "สวนสัตว์": "สวนสัตว์เปิดเขาเขียว",
      "ปีงบประมาณ": 2569,
      "ต.ค. 68": 16585,
      "พ.ย. 68": 5916,
      "ธ.ค. 68": 8025,
      "ม.ค.69": 3777,
      "ก.พ. 69": 4738,
      "มี.ค. 69": 9562,
      "เม.ย. 69": 14528,
      "พ.ค. 69": 10849,
      "มิ.ย. 69": 5515,
      "ก.ค. 69": 7564,
      "ส.ค. 69": null,
      "ก.ย. 69": null
    }
  ]
}


5. การทดสอบด้วย Postman
-----------------------
Method   : GET
URL      : https://backend-t-karn-zoo-api-66122519037.vercel.app/api/zoo-visitors
ผลที่ได้ : Status 200 OK และ JSON ตามหัวข้อที่ 4
(ภาพหน้าจอผลทดสอบแนบมาพร้อมงาน)


6. ไฟล์ในโปรเจกต์
-----------------
main.py           โค้ด FastAPI
requirements.txt  รายการ dependencies (fastapi[standard], httpx, openpyxl)
readme.txt        ไฟล์นี้
data/0ecc96cf-d914-42a1-b184-dbbd013c3c9c.xlsx  สำเนาไฟล์จริงของ resource จาก data.go.th
data/resource_show.json                          metadata ของ resource จาก data.go.th API


7. วิธีติดตั้งและรันบนเครื่อง (Windows PowerShell)
-------------------------------------------------
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
fastapi dev main.py

แล้วเปิด http://127.0.0.1:8000/api/zoo-visitors และ http://127.0.0.1:8000/docs


8. การ Deploy
-------------
Deploy บน Vercel โดย import repository จาก GitHub
Vercel ตรวจพบ FastAPI จาก main.py และติดตั้ง dependencies จาก requirements.txt ให้อัตโนมัติ
ไม่ต้องตั้ง Build Command และไม่ต้องตั้ง Environment Variables
บน Vercel ผลลัพธ์จะเป็น "retrieved_from": "local_copy" เพราะ data.go.th ปฏิเสธ request จากเซิร์ฟเวอร์ต่างประเทศ
