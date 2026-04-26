"""
verify_urls.py — Check each website URL in family_offices.csv loads correctly.

Outputs verification status for each row. Marks dead/redirected URLs.
"""

import csv
import requests
from pathlib import Path

INPUT = Path("data/processed/family_offices.csv")
OUTPUT = Path("data/processed/url_verification.csv")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}


def check_url(url: str) -> dict:
    if not url or not url.startswith("http"):
        return {"status": "no_url", "code": 0, "final_url": ""}
    try:
        r = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        return {
            "status": "ok" if r.status_code == 200 else "error",
            "code": r.status_code,
            "final_url": r.url,
        }
    except requests.exceptions.Timeout:
        return {"status": "timeout", "code": 0, "final_url": ""}
    except requests.exceptions.ConnectionError:
        return {"status": "dead", "code": 0, "final_url": ""}
    except Exception as e:
        return {"status": f"error: {type(e).__name__}", "code": 0, "final_url": ""}


def main():
    rows = list(csv.DictReader(open(INPUT, encoding="utf-8")))
    print(f"Verifying {len(rows)} URLs...\n")

    results = []
    for i, r in enumerate(rows, 1):
        url = r["website"]
        check = check_url(url)
        flag = "✓" if check["status"] == "ok" else "✗"
        print(f"[{i:2d}/50] {flag} {check['status']:10s} {r['name'][:40]}")
        results.append({
            "id": r["id"],
            "name": r["name"],
            "website": url,
            "status": check["status"],
            "http_code": check["code"],
            "final_url": check["final_url"],
        })

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=results[0].keys())
        w.writeheader()
        w.writerows(results)

    ok = sum(1 for r in results if r["status"] == "ok")
    bad = [r for r in results if r["status"] != "ok"]
    print(f"\n{ok}/{len(results)} OK")
    if bad:
        print(f"\nFAILED ({len(bad)}):")
        for r in bad:
            print(f"  {r['id']}: {r['name']} — {r['status']}")
    print(f"\nFull report: {OUTPUT}")


if __name__ == "__main__":
    main()
