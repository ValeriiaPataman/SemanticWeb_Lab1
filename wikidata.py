import requests
from rdflib import Graph, Namespace, Literal, RDFS, XSD

EX = Namespace("https://example.org/semantic-books/")
WD = Namespace("http://www.wikidata.org/entity/")
WDT = Namespace("http://www.wikidata.org/prop/direct/")

local = Graph()
local.parse("books.ttl", format="turtle")
external = Graph()

for wikidata_id in ["Q35064", "Q39829", "Q34660"]:
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_id}.json"
    try:
        response = requests.get(url, timeout=20,
                                headers={"User-Agent": "SemanticBooksStudentLab/1.0"})
        response.raise_for_status()
        item = response.json()["entities"][wikidata_id]
        name = item["labels"].get("uk", item["labels"]["en"])["value"]
        date = item["claims"]["P569"][0]["mainsnak"]["datavalue"]["value"]["time"]
        date = date.lstrip("+").split("T")[0]
        external.add((WD[wikidata_id], RDFS.label, Literal(name)))
        external.add((WD[wikidata_id], WDT.P569, Literal(date, datatype=XSD.date)))
        print("Отримано з Wikidata:", name, date)
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError) as error:
        print("Не вдалося отримати", wikidata_id, ":", error)

if len(external) == 0:
    print("Зовнішні дані не завантажені. Перевір інтернет і повтори запуск.")
else:
    combined = local + external
    query = """
        PREFIX ex: <https://example.org/semantic-books/>
        PREFIX schema: <https://schema.org/>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        SELECT ?name ?birthDate WHERE {
            ?author a ex:Author ; schema:name ?name ; owl:sameAs ?wikiAuthor .
            ?wikiAuthor wdt:P569 ?birthDate .
        }
        ORDER BY ?name
    """
    print("\nАвтор із нашого графу | Дата народження з Wikidata")
    for row in combined.query(query):
        print(row.name, "|", row.birthDate)
    combined.serialize("books_with_wikidata.ttl", format="turtle")
    print("Створено books_with_wikidata.ttl")
