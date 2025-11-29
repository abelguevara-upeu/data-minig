import os, sys, time, csv, requests
from typing import List, Dict

API_KEY = "a4280fabb21fd2647398f0c3b53bef3f"
BASE = "https://api.elsevier.com/content/search/scopus"

def scopus_search(query: str, start_year: int = 2015, end_year: int = 2026, max_results: int = 500):
    if not API_KEY:
        print("Falta SCOPUS_API_KEY en el entorno.", file=sys.stderr)
        sys.exit(1)
    headers = {"X-ELS-APIKey": API_KEY, "Accept": "application/json"}
    params_base = {
        "query": f'{query} AND PUBYEAR > {start_year-1} AND PUBYEAR < {end_year+1}',
        "count": 25,
    }
    results: List[Dict] = []
    start = 0
    while start < max_results:
        params = params_base | {"start": start}
        r = requests.get(BASE, headers=headers, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        entries = data.get("search-results", {}).get("entry", [])
        if not entries:
            break
        for e in entries:
            results.append({
                "eid": e.get("eid"),
                "doi": e.get("prism:doi"),
                "title": e.get("dc:title"),
                "publicationName": e.get("prism:publicationName"),
                "coverDate": e.get("prism:coverDate"),
                "pubYear": (e.get("prism:coverDate") or "")[:4],
                "citedby_count": e.get("citedby-count"),
                "authkeywords": e.get("authkeywords"),
                "creator": e.get("dc:creator"),
                "aggregationType": e.get("prism:aggregationType"),
                "openAccess": e.get("openaccess"),
                "scopus_link": next((l.get("@href") for l in e.get("link", []) if l.get("@ref") == "scopus"), None),
            })
        start += params_base["count"]
        time.sleep(0.2)
    return results
