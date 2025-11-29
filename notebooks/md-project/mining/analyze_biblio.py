import pandas as pd
from collections import Counter
from math import log10

IN_CSV = "scopus_all_anemia.csv"

df = pd.read_csv(IN_CSV)
df["pubYear"] = pd.to_numeric(df["pubYear"], errors="coerce")
df["citedby_count"] = pd.to_numeric(df["citedby_count"], errors="coerce").fillna(0)

# Tendencia y outlets
by_year = df.groupby("pubYear").size().dropna()
top_journals = df["publicationName"].value_counts().head(12)
top_cited = df.sort_values("citedby_count", ascending=False)[["title","publicationName","pubYear","citedby_count"]].head(10)

# Keywords
def split_kw(x):
    if pd.isna(x): return []
    return [k.strip().lower() for k in str(x).replace(";", ",").split(",") if k.strip()]
kw = Counter([k for row in df["authkeywords"].dropna().map(split_kw) for k in row]).most_common(20)

# Señales de novedad (proxies)
ml_hits = df["title"].str.contains(r"machine learning|deep learning|random forest|xgboost|artificial intelligence|data mining", case=False, na=False).sum()
dhs_hits = df["title"].str.contains(r"\bDHS\b|Demographic and Health Survey|ENDES", case=False, na=False).sum()
peru_hits = df["title"].str.contains(r"Peru|Per[uú]", case=False, na=False).sum()
wash_hits = df["title"].str.contains(r"WASH|water|sanitation", case=False, na=False).sum()

n_total = len(df)
novelty_score = max(1, min(5, 5 - log10(max(1, dhs_hits)) - 0.5*log10(max(1, peru_hits)) + (ml_hits>0)*0.5))

# Relevancia (proxies simples)
relevance_score = max(1, min(5, 3 + (wash_hits>0) + (peru_hits>0) + (dhs_hits>0)))

print("Publicaciones por año:\n", by_year.to_string())
print("\nTop journals:\n", top_journals.to_string())
print("\nTop 10 citados:\n", top_cited.to_string(index=False))
print("\nTop keywords:\n", kw)
print("\nSeñales:")
print(f"- Total: {n_total}, ML/AI: {ml_hits}, DHS/ENDES en título: {dhs_hits}, Perú en título: {peru_hits}, WASH: {wash_hits}")
print(f"\nPuntajes (proxy): Originalidad={novelty_score:.1f} /5, Relevancia={relevance_score:.1f} /5")

# Exportar resumen a Markdown
with open("scopus_report.md", "w", encoding="utf-8") as f:
    f.write("# Scopus – Anemia (resumen)\n\n")
    f.write(f"- Total artículos: {n_total}\n")
    f.write(f"- ML/AI: {ml_hits}; DHS/ENDES: {dhs_hits}; Perú: {peru_hits}; WASH: {wash_hits}\n")
    f.write(f"- Originalidad (proxy): {novelty_score:.1f}/5; Relevancia (proxy): {relevance_score:.1f}/5\n\n")
    f.write("## Publicaciones por año\n")
    f.write(by_year.to_csv(header=False))
    f.write("\n## Top journals\n")
    f.write(top_journals.to_csv(header=False))
    f.write("\n## Top 10 citados\n")
    f.write(top_cited.to_csv(index=False))
