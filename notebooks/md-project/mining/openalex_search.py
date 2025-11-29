import requests
import pandas as pd
from typing import List, Dict
import time
import json

def openalex_search(query: str, years: str = "2015-2025", per_page: int = 200, max_results: int = 1000) -> List[Dict]:
    """
    Buscar en OpenAlex API (alternativa gratuita a Scopus)

    Args:
        query: Términos de búsqueda
        years: Rango de años (ej: "2015-2025")
        per_page: Resultados por página (máx 200)
        max_results: Máximo total de resultados
    """
    base_url = "https://api.openalex.org/works"
    results = []
    page = 1
    max_pages = min(50, (max_results // per_page) + 1)

    print(f"Buscando: '{query}' ({years})")

    while page <= max_pages:
        params = {
            "search": query,
            "filter": f"publication_year:{years}",
            "per-page": per_page,
            "page": page,
            "mailto": "research@university.edu"  # Requerido por OpenAlex
        }

        try:
            r = requests.get(base_url, params=params, timeout=30)
            r.raise_for_status()
            data = r.json()

            works = data.get("results", [])
            if not works:
                break

            for work in works:
                # Extraer información clave
                host_venue = work.get("host_venue") or {}
                open_access = work.get("open_access") or {}

                # Procesar autores
                authors = []
                for auth in work.get("authorships", [])[:5]:  # Top 5 autores
                    author_info = auth.get("author", {})
                    if author_info.get("display_name"):
                        authors.append(author_info["display_name"])

                # Procesar conceptos/keywords
                concepts = []
                for concept in work.get("concepts", [])[:10]:
                    if concept.get("display_name") and concept.get("score", 0) > 0.3:
                        concepts.append({
                            "name": concept["display_name"],
                            "score": concept.get("score", 0)
                        })

                results.append({
                    "id": work.get("id"),
                    "doi": work.get("doi"),
                    "title": work.get("title"),
                    "publication_year": work.get("publication_year"),
                    "publication_date": work.get("publication_date"),
                    "cited_by_count": work.get("cited_by_count", 0),
                    "is_retracted": work.get("is_retracted", False),
                    "is_paratext": work.get("is_paratext", False),

                    # Journal/venue info
                    "journal": host_venue.get("display_name"),
                    "journal_issn": ";".join(host_venue.get("issn_l", []) if host_venue.get("issn_l") else []),
                    "publisher": host_venue.get("publisher"),
                    "venue_type": host_venue.get("type"),

                    # Open access
                    "is_oa": open_access.get("is_oa", False),
                    "oa_status": open_access.get("oa_status"),
                    "oa_url": open_access.get("oa_url"),

                    # Authors and concepts
                    "authors": ";".join(authors),
                    "author_count": len(work.get("authorships", [])),
                    "concepts": json.dumps(concepts),
                    "concept_names": ";".join([c["name"] for c in concepts]),

                    # Content
                    "abstract_available": bool(work.get("abstract_inverted_index")),
                    "language": work.get("language"),
                    "type": work.get("type"),
                    "type_crossref": work.get("type_crossref"),

                    # URLs
                    "openalex_url": work.get("id"),
                    "doi_url": f"https://doi.org/{work.get('doi')}" if work.get("doi") else None,

                    # Funding
                    "grants_count": len(work.get("grants", [])),
                    "has_funding": len(work.get("grants", [])) > 0,
                })

            print(f"  Página {page}: {len(works)} resultados (total: {len(results)})")

            # Parar si ya tenemos suficientes resultados
            if len(results) >= max_results:
                break

            page += 1
            time.sleep(0.1)  # Rate limiting cortés

        except requests.exceptions.RequestException as e:
            print(f"  Error en página {page}: {e}")
            break
        except Exception as e:
            print(f"  Error procesando página {page}: {e}")
            break

    print(f"  Completado: {len(results)} resultados totales")
    return results

def test_openalex():
    """Test rápido de OpenAlex API"""
    print("Probando OpenAlex API...")
    results = openalex_search("machine learning health survey", max_results=10)
    if results:
        print(f"✅ API funcionando. Ejemplo de resultado:")
        print(f"  Título: {results[0]['title']}")
        print(f"  Journal: {results[0]['journal']}")
        print(f"  Año: {results[0]['publication_year']}")
        print(f"  Citas: {results[0]['cited_by_count']}")
        return True
    else:
        print("❌ Sin resultados o error en API")
        return False

if __name__ == "__main__":
    # Test simple
    success = test_openalex()

    if success:
        print("\n" + "="*50)
        print("Ejecutando búsqueda de prueba más amplia...")
        results = openalex_search("anemia demographic health survey", max_results=50)

        if results:
            df = pd.DataFrame(results)
            df.to_csv("openalex_test_results.csv", index=False)
            print(f"Guardado: openalex_test_results.csv ({len(results)} registros)")
