import pandas as pd
from pathlib import Path
from scopus_search import scopus_search

OUT_DIR = Path(".")
QUERIES = {
    "anemia_endes_peru": 'TITLE-ABS-KEY(anemia AND (Peru OR "Latin America") AND ("Demographic and Health Survey" OR DHS OR ENDES))',
    "anemia_child_dhs": 'TITLE-ABS-KEY(anemia AND child* AND ("Demographic and Health Survey" OR DHS))',
    "anemia_ml_survey": 'TITLE-ABS-KEY(anemia AND (engineering OR "machine learning" OR "data mining") AND (survey OR DHS OR "Demographic and Health Survey"))',
    "hb_altitude_andes": 'TITLE-ABS-KEY(hemoglobin AND altitude AND (Peru OR Andes) AND (survey OR DHS))',
    "anemia_wash_dhs": 'TITLE-ABS-KEY(anemia AND (WASH OR water OR sanitation) AND (DHS OR survey))',
    "maternal_anemia_prenatal": 'TITLE-ABS-KEY("maternal anemia" AND (prenatal OR pregnancy) AND (DHS OR survey))',
}

def main():
    frames = []
    for tag, q in QUERIES.items():
        print(f"Buscando: {tag}")
        rows = scopus_search(q, start_year=2015, end_year=2025, max_results=500)
        df = pd.DataFrame(rows)
        if df.empty:
            continue
        df.insert(0, "source_tag", tag)
        df.insert(1, "source_query", q)
        out_csv = OUT_DIR / f"scopus_{tag}.csv"
        df.to_csv(out_csv, index=False)
        frames.append(df)

    if not frames:
        print("Sin resultados en las consultas.")
        return

    all_df = pd.concat(frames, ignore_index=True)
    # De-duplicar por DOI y EID
    all_df["doi_norm"] = all_df["doi"].str.lower().str.strip()
    all_df = all_df.drop_duplicates(subset=["doi_norm"]).drop(columns=["doi_norm"])
    all_df = all_df.drop_duplicates(subset=["eid"], keep="first")
    all_csv = OUT_DIR / "scopus_all_anemia.csv"
    all_df.to_csv(all_csv, index=False)
    print(f"Guardado combinado: {all_csv} ({len(all_df)} registros)")

if __name__ == "__main__":
    main()
