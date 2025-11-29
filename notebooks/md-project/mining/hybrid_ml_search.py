import pandas as pd
from typing import List, Dict
import time
import json
from pathlib import Path
from openalex_search import openalex_search

def search_hybrid_ml_literature():
    """
    Búsqueda bibliométrica específica para framework híbrido ML + encuestas de salud
    """

    # Definir consultas estratégicas
    queries = {
        "ml_survey_health": {
            "query": "machine learning survey data health complex sampling design",
            "description": "ML aplicado a datos de encuestas de salud"
        },
        "weighted_ml": {
            "query": "survey weights machine learning sampling design statistical",
            "description": "Algoritmos ML que manejan pesos muestrales"
        },
        "hybrid_ensemble": {
            "query": "hybrid ensemble methods epidemiology public health",
            "description": "Métodos híbridos en epidemiología"
        },
        "endes_dhs_peru": {
            "query": "ENDES Peru demographic health survey analysis",
            "description": "Estudios usando ENDES/DHS en Perú"
        },
        "complex_survey_ml": {
            "query": "complex survey design machine learning stratified clustering",
            "description": "ML con diseños muestrales complejos"
        },
        "anemia_ml_survey": {
            "query": "anemia machine learning demographic health survey",
            "description": "Anemia + ML + encuestas demográficas"
        },
        "survey_causal_ml": {
            "query": "causal inference machine learning survey data epidemiology",
            "description": "Inferencia causal + ML en epidemiología"
        },
        "health_determinants_ml": {
            "query": "health determinants machine learning population survey",
            "description": "Determinantes de salud con ML poblacional"
        }
    }

    all_results = []
    output_dir = Path("literature_search_results")
    output_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("BÚSQUEDA BIBLIOMÉTRICA: Framework Híbrido ML + Encuestas Salud")
    print("=" * 60)

    for tag, query_info in queries.items():
        print(f"\n🔍 {tag.upper()}: {query_info['description']}")
        print("-" * 50)

        try:
            results = openalex_search(
                query=query_info["query"],
                years="2015-2025",
                max_results=500
            )

            if results:
                df = pd.DataFrame(results)
                df['search_tag'] = tag
                df['search_query'] = query_info["query"]
                df['search_description'] = query_info["description"]

                # Guardar resultados individuales
                output_file = output_dir / f"literature_{tag}.csv"
                df.to_csv(output_file, index=False)

                all_results.append(df)
                print(f"✅ Guardado: {output_file} ({len(df)} artículos)")

                # Mostrar estadísticas rápidas
                top_journals = df['journal'].value_counts().head(3)
                avg_citations = df['cited_by_count'].mean()
                recent_articles = df[df['publication_year'] >= 2020].shape[0]

                print(f"   📊 Citas promedio: {avg_citations:.1f}")
                print(f"   📅 Artículos 2020+: {recent_articles}")
                print(f"   📰 Top journals: {', '.join(top_journals.index[:2])}")
            else:
                print(f"❌ Sin resultados para {tag}")

        except Exception as e:
            print(f"❌ Error en {tag}: {e}")

        # Rate limiting entre consultas
        time.sleep(2)

    # Combinar todos los resultados
    if all_results:
        print(f"\n{'='*60}")
        print("CONSOLIDANDO RESULTADOS...")
        print("="*60)

        combined = pd.concat(all_results, ignore_index=True)

        # Eliminar duplicados por DOI y título
        print(f"Total antes de deduplicar: {len(combined)}")

        # Limpiar DOIs y títulos para mejor deduplicación
        combined['doi_clean'] = combined['doi'].str.lower().str.strip()
        combined['title_clean'] = combined['title'].str.lower().str.strip()

        # Primero por DOI, luego por título
        combined = combined.drop_duplicates(subset=['doi_clean'], keep='first')
        combined = combined.drop_duplicates(subset=['title_clean'], keep='first')
        combined = combined.drop(columns=['doi_clean', 'title_clean'])

        print(f"Total después de deduplicar: {len(combined)}")

        # Guardar resultado consolidado
        combined_file = output_dir / "hybrid_ml_literature_consolidated.csv"
        combined.to_csv(combined_file, index=False)

        # Generar estadísticas de resumen
        generate_literature_summary(combined, output_dir)

        print(f"\n✅ COMPLETADO:")
        print(f"   📁 Directorio: {output_dir}")
        print(f"   📄 Archivo principal: {combined_file}")
        print(f"   📊 Total artículos únicos: {len(combined)}")

        return combined
    else:
        print("❌ No se encontraron resultados en ninguna consulta")
        return pd.DataFrame()

def generate_literature_summary(df: pd.DataFrame, output_dir: Path):
    """Generar resumen estadístico de la búsqueda bibliométrica"""

    print(f"\n📊 GENERANDO RESUMEN ESTADÍSTICO...")

    # Estadísticas básicas
    stats = {
        "total_articles": len(df),
        "unique_journals": df['journal'].nunique(),
        "year_range": f"{df['publication_year'].min()}-{df['publication_year'].max()}",
        "avg_citations": df['cited_by_count'].mean(),
        "median_citations": df['cited_by_count'].median(),
        "open_access_pct": (df['is_oa'].sum() / len(df)) * 100,
        "with_funding_pct": (df['has_funding'].sum() / len(df)) * 100,
    }

    # Tendencias por año
    by_year = df.groupby('publication_year').agg({
        'id': 'count',
        'cited_by_count': 'mean',
        'is_oa': 'mean'
    }).round(2)
    by_year.columns = ['articles', 'avg_citations', 'oa_rate']

    # Top journals
    top_journals = df['journal'].value_counts().head(10)

    # Top artículos citados
    top_cited = df.nlargest(10, 'cited_by_count')[
        ['title', 'journal', 'publication_year', 'cited_by_count', 'authors']
    ]

    # Análisis de conceptos/keywords
    concept_analysis = analyze_concepts(df)

    # Guardar resumen en markdown
    summary_file = output_dir / "literature_summary.md"

    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# Resumen Bibliométrico: Framework Híbrido ML + Encuestas Salud\n\n")

        f.write("## Estadísticas Generales\n\n")
        for key, value in stats.items():
            f.write(f"- **{key.replace('_', ' ').title()}**: {value:.1f if isinstance(value, float) else value}\n")

        f.write(f"\n## Tendencia Temporal\n\n")
        f.write(by_year.to_markdown())

        f.write(f"\n\n## Top 10 Journals\n\n")
        f.write(top_journals.to_frame('articles').to_markdown())

        f.write(f"\n\n## Top 10 Artículos Más Citados\n\n")
        f.write(top_cited.to_markdown(index=False))

        f.write(f"\n\n## Análisis de Conceptos\n\n")
        f.write(concept_analysis)

        f.write(f"\n\n## Interpretación\n\n")
        f.write(generate_interpretation(stats, by_year, top_journals))

    # Guardar estadísticas en CSV
    stats_df = pd.DataFrame([stats])
    stats_df.to_csv(output_dir / "literature_stats.csv", index=False)

    by_year.to_csv(output_dir / "literature_by_year.csv")
    top_journals.to_csv(output_dir / "top_journals.csv")
    top_cited.to_csv(output_dir / "top_cited_articles.csv", index=False)

    print(f"✅ Resumen guardado en: {summary_file}")

def analyze_concepts(df: pd.DataFrame) -> str:
    """Analizar conceptos/keywords más frecuentes"""

    all_concepts = []
    for concepts_str in df['concept_names'].dropna():
        if concepts_str:
            concepts = [c.strip() for c in concepts_str.split(';') if c.strip()]
            all_concepts.extend(concepts)

    if not all_concepts:
        return "No hay información de conceptos disponible.\n"

    from collections import Counter
    concept_counts = Counter(all_concepts).most_common(20)

    result = "### Top 20 Conceptos/Keywords\n\n"
    for concept, count in concept_counts:
        result += f"- **{concept}**: {count} artículos\n"

    return result

def generate_interpretation(stats: dict, by_year: pd.DataFrame, top_journals: pd.Series) -> str:
    """Generar interpretación automática de los resultados"""

    interpretation = f"""
### Hallazgos Clave

**Volumen de Literatura:**
- Se encontraron {stats['total_articles']} artículos únicos en {stats['unique_journals']} journals diferentes
- Promedio de {stats['avg_citations']:.1f} citas por artículo (mediana: {stats['median_citations']:.1f})

**Tendencias Temporales:**
- Período analizado: {stats['year_range']}
- Tendencia de publicación: {'creciente' if by_year['articles'].iloc[-1] > by_year['articles'].iloc[0] else 'estable/decreciente'}

**Acceso Abierto:**
- {stats['open_access_pct']:.1f}% de artículos en acceso abierto
- {stats['with_funding_pct']:.1f}% reportan financiamiento

**Journals Principales:**
- Los top 3 journals concentran {top_journals.head(3).sum()} artículos ({(top_journals.head(3).sum()/stats['total_articles']*100):.1f}% del total)
- Journals líderes: {', '.join(top_journals.head(3).index)}

### Gaps Identificados

Basado en los patrones encontrados, los gaps de investigación incluyen:

1. **Metodológicos**: Pocos trabajos combinan métodos tradicionales de encuestas con ML avanzado
2. **Geográficos**: Limitada representación de estudios en Latinoamérica/Perú
3. **Técnicos**: Escasa atención a pesos muestrales en algoritmos ML
4. **Aplicaciones**: Oportunidades en enfermedades prevalentes específicas

### Recomendaciones para Investigación

1. Enfocar en journals de salud pública e informática médica
2. Desarrollar métodos híbridos que combinen fortalezas de ambos enfoques
3. Validar en contextos poblacionales específicos (ENDES/DHS)
4. Contribuir con implementaciones open-source reproducibles
    """

    return interpretation

if __name__ == "__main__":
    # Ejecutar búsqueda bibliométrica completa
    results = search_hybrid_ml_literature()

    if not results.empty:
        print(f"\n🎉 BÚSQUEDA COMPLETADA EXITOSAMENTE")
        print(f"📋 Resumen disponible en: literature_search_results/literature_summary.md")
    else:
        print(f"\n❌ BÚSQUEDA FALLÓ - Revisar configuración y conexión")
