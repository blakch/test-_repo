"""
누리장터 민간입찰공고 데이터 수집 스크립트
- 실행 시 전날 입찰공고를 4개 유형(공사/용역/물품/기타)별로 조회
- 결과를 C:\Users\PC_01\Documents\누리장터_daily.json 에 저장
- Windows 작업 스케줄러로 매일 오전 6시에 실행 권장
"""

import urllib.request
import json
import os
from datetime import datetime, timedelta

# ── 설정 ──────────────────────────────────────────────
API_KEY = "9b2f2b8ef6886aba64c0de54c94b2df7f46afa045a8fa6795527d207e44f49a4"
BASE_URL = "https://apis.data.go.kr/1230000/ao/PrvtBidNtceService"
SAVE_PATH = r"C:\Users\PC_01\Documents\누리장터_daily.json"

ENDPOINTS = {
    "공사": "getPrvtBidPblancListInfoCnstwk",
    "용역": "getPrvtBidPblancListInfoServc",
    "물품": "getPrvtBidPblancListInfoThng",
    "기타": "getPrvtBidPblancListInfoEtc",
}
# ─────────────────────────────────────────────────────


def format_amount(val):
    """금액을 억/천만 단위 문자열로 변환"""
    try:
        n = int(float(val))
    except (TypeError, ValueError):
        return "-"
    if n == 0:
        return "-"
    if n >= 100_000_000:
        return f"{n / 100_000_000:.1f}억원"
    if n >= 10_000_000:
        return f"{n / 10_000_000:.1f}천만원"
    return f"{n:,}원"


def fetch_bids(endpoint_name, endpoint_path, bgn_dt, end_dt, num_rows=50):
    url = (
        f"{BASE_URL}/{endpoint_path}"
        f"?serviceKey={API_KEY}"
        f"&pageNo=1&numOfRows={num_rows}"
        f"&inqryDiv=1"
        f"&inqryBgnDt={bgn_dt}"
        f"&inqryEndDt={end_dt}"
        f"&type=json"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
        # 응답 구조: response > body > items
        # items는 배열(list) 또는 숫자키 dict("0","1",...) 또는 item 키를 가진 dict
        body = raw.get("response", {}).get("body", {})
        total = body.get("totalCount", 0)
        items_wrapper = body.get("items") or []
        if isinstance(items_wrapper, list):
            items = items_wrapper
        elif isinstance(items_wrapper, dict):
            if "item" in items_wrapper:
                item = items_wrapper["item"]
                items = item if isinstance(item, list) else [item]
            else:
                # 숫자 문자열 키("0","1",...) 형태
                items = list(items_wrapper.values())
        else:
            items = []
        return {"success": True, "total": total, "items": items, "error": None}
    except Exception as e:
        return {"success": False, "total": 0, "items": [], "error": str(e)}


def main():
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    date_str = yesterday.strftime("%Y%m%d")
    bgn_dt = date_str + "0000"
    end_dt = date_str + "2359"
    label_date = yesterday.strftime("%Y년 %m월 %d일")

    print(f"[누리장터 수집] 기준일: {label_date}")
    print(f"저장 위치: {SAVE_PATH}\n")

    results = {}
    for label, path in ENDPOINTS.items():
        print(f"  {label} 조회 중...", end=" ", flush=True)
        res = fetch_bids(label, path, bgn_dt, end_dt)
        if res["success"]:
            print(f"{res['total']}건")
        else:
            print(f"실패 - {res['error']}")
        results[label] = res

    # 저장
    output = {
        "fetch_date": today.strftime("%Y-%m-%d %H:%M:%S"),
        "target_date": label_date,
        "target_date_raw": date_str,
        "save_path": SAVE_PATH,
        "data": results,
    }

    os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    total_count = sum(r["total"] for r in results.values())
    print(f"\n완료. 총 {total_count}건 → {SAVE_PATH}")


if __name__ == "__main__":
    main()
