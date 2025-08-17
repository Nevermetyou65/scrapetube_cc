"""Config for youtube data extraction"""

from datetime import datetime
from pathlib import Path
from pytz import timezone


def get_today_string():
    """Return today's date string in the format YYYYMMDD_HHMMSS (Bangkok time)."""
    bangkok_tz = timezone("Asia/Bangkok")
    today_date = datetime.now(bangkok_tz)
    today_string = today_date.strftime("%Y-%m-%d_%H-%M-%S").replace("-", "")
    return today_string


LOG_DIR = Path(__file__).parent.parent / "logs"
DATA_DIR = Path(__file__).parent.parent / "data"
KEYWORD_VIDEOS_META_PARQUET = DATA_DIR / f"meta_data_{get_today_string()}.parquet"
CHANNEL_VIDEOS_META_PARQUET = (
    DATA_DIR / f"channel_video_meta_{get_today_string()}.parquet"
)
SUBTITLES_PARQUET = DATA_DIR / f"subtitle_{get_today_string()}.parquet"
VIDEO_BASE_URL = "https://www.youtube.com/watch?v="
QUERY_STRINGS = [
    "คณิตศาสตร์",
    "ฟิสิกส์",
    "เคมี",
    "ชีววิทยา",
    "สังคมศาสตร์",
    "ประวัติศาสตร์",
    "การงานอาชีพ",
    "พลศึกษา",
    "ภาษาไทย",
    "สุขศึกษา",
    "การเมือง",
    "การท่องเที่ยว",
    "กฎหมาย",
    "วิศวกรรมศาสตร์",
    "คอมพิวเตอร์",
    "การเขียนโปรแกรม",
    "การใช้ชีวิต",
    "จิตวิทยา",
    "การเกษตร",
    "การแพทย์",
    "การรักษาโรค",
    "สถาปัตยกรรม",
    "การบริหารธุรกิจ",
    "การประมง",
    "การศึกษา",
    "อุตสหกรรม",
    "สิ่งแวดล้อม",
    "การพยาบาล",
    "กีฬา",
    "การโรงแรม",
    "สาธารณสุข",
    "ทรัพยากรธรรมชาติ",
    "เศรษฐศาสตร์",
    "การเงิน",
    "มหาวิทยาลัย",
    "การพัฒนาตนเอง",
    "ดาราศาสตร์",
    "การถ่ายภาพ",
    "การออกแบบกราฟิก",
    "ภาษาอังกฤษ",
    "วัฒนธรรม",
    "เทคโนโลยี",
    "การทำอาหาร",
    "ดนตรี",
    "การเงินส่วนบุคคล",
    "เกมออนไลน์",
    "การลงทุน",
    "สุขภาพจิต",
    "ปัญญาประดิษฐ์",
    "การเรียนรู้ของเครื่อง",
    "การออกกำลังกาย",
    "โยคะ",
    "การวางแผนชีวิต",
    "มังสวิรัติ",
    "การจัดการเวลา",
    "งานฝีมือ",
    "การออกแบบภายใน",
    "การทำสวน",
    "การเขียนนิยาย",
    "การซ่อมแซมบ้าน",
    "หุ่นยนต์",
    "การเขียนโค้ด",
    "ข้อมูลขนาดใหญ่",
    "การสอนออนไลน์",
    "การวิเคราะห์ข้อมูล",
    "ภาพยนตร์",
    "อนิเมะ",
    "การเดินทางท่องเที่ยว",
    "เพลงไทย",
    "การเรียนภาษาใหม่",
]
