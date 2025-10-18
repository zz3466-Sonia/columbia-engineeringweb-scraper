import time
import re
import csv
import pathlib
from typing import List, Dict

import requests
import pandas as pd
from bs4 import BeautifulSoup

# 你可以把更多 Bulletin 页面放到这里
URLS = [
    "https://bulletin.columbia.edu/columbia-engineering/academic-departments-programs/computer-science/undergraduate-programs/computer-science-bs/"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; columbia-bulletin-scraper; +https://example.com)"
}

OUT_DIR = pathlib.Path("data")
OUT_DIR.mkdir(parents=True, exist_ok=True)

COURSE_PREFIXES = ("COMS", "CSEE", "CSOR", "ELEN", "EECS",
                   "APMA", "MATH", "STAT", "IEOR",
                   "PHYS", "CHEM", "BIOL", "BMEN", "MECE", "MSAE")

def is_course_token(text: str) -> bool:
    """粗略识别课程代码（如 COMS W3134, STAT UN1201 等）"""
    text = " ".join(text.split())
    if not any(pref in text for pref in COURSE_PREFIXES):
        return False
    # 常见格式：DEPT [A-Z]{1,2}\d{4}，不过 Bulletin 上经常混合空格/破折号
    return bool(re.search(r"[A-Z]{3,4}\s*[A-Z]{0,2}\s*\d{3,4}", text))

def parse_page(url: str) -> Dict[str, pd.DataFrame]:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    title_el = soup.select_one("h1")
    title = title_el.get_text(strip=True) if title_el else url

    # 抓小节（h2/h3）及其后续段落/列表/表格，直到下一个同级标题
    sections: List[Dict[str, str]] = []
    for h in soup.select("h2, h3"):
        sec_title = h.get_text(" ", strip=True)
        content_parts = []
        for sib in h.find_all_next():
            if sib is h:
                continue
            if sib.name in ["h2", "h3"]:
                break
            if sib.name in ["p", "ul", "ol", "table"]:
                content_parts.append(sib.get_text(" ", strip=True))
        text = "\n".join([t for t in content_parts if t])
        if text.strip():
            sections.append({"page_title": title, "section": sec_title, "text": text})

    # 抓课程代码（基于 <a> 与纯文本双通道）
    courses = set()
    for a in soup.select("a"):
        label = a.get_text(" ", strip=True)
        if is_course_token(label):
            courses.add(" ".join(label.split()))

    # 也扫描所有列表项的纯文本，补漏
    for li in soup.select("li"):
        label = li.get_text(" ", strip=True)
        # 只取较短的 token 以降低误报
        if len(label) <= 80 and is_course_token(label):
            courses.add(" ".join(label.split()))

    df_sections = pd.DataFrame(sections)
    df_courses = pd.DataFrame({"page_title": [title]*len(courses), "course": sorted(courses)})

    return {"sections": df_sections, "courses": df_courses, "title": title}

def main():
    all_sections = []
    all_courses = []

    for i, url in enumerate(URLS, 1):
        print(f"[{i}/{len(URLS)}] Fetching: {url}")
        try:
            parsed = parse_page(url)
            if not parsed["sections"].empty:
                all_sections.append(parsed["sections"])
            if not parsed["courses"].empty:
                all_courses.append(parsed["courses"])
        except Exception as e:
            print("Error:", e)
        time.sleep(1.0)  # 礼貌抓取：简单限速

    if all_sections:
        df_sec = pd.concat(all_sections, ignore_index=True)
        df_sec.to_csv(OUT_DIR / "cs_bs_sections.csv", index=False, quoting=csv.QUOTE_MINIMAL)
        print(f"Saved: {OUT_DIR/'cs_bs_sections.csv'} ({len(df_sec)} rows)")
    else:
        print("No sections parsed.")

    if all_courses:
        df_courses = pd.concat(all_courses, ignore_index=True).drop_duplicates()
        df_courses.to_csv(OUT_DIR / "cs_bs_courses.csv", index=False, quoting=csv.QUOTE_MINIMAL)
        print(f"Saved: {OUT_DIR/'cs_bs_courses.csv'} ({len(df_courses)} rows)")
    else:
        print("No courses parsed.")

if __name__ == "__main__":
    main()
