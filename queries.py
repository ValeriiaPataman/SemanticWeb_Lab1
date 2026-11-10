from rdflib import Graph, Namespace

EX = Namespace("https://example.org/semantic-books/")
g = Graph()
g.parse("books.ttl", format="turtle")
print("Зчитано RDF-трійок:", len(g))

print("\nВластивості книги 'Я бачу, вас цікавить пітьма':")
for predicate, obj in g.predicate_objects(EX.book_darkness):
    print(predicate, "->", obj)

queries = [
    ("1. Які книги написала Агата Крісті?", """
        PREFIX ex: <https://example.org/semantic-books/>
        PREFIX schema: <https://schema.org/>
        SELECT ?title ?year WHERE {
            ?book a ex:Book ; schema:name ?title ; ex:year ?year ;
                  ex:writtenBy ?author .
            ?author schema:name "Агата Крісті"@uk .
        }
        ORDER BY ?year
    """),

    ("2. Які книги вийшли після 2000 року?", """
        PREFIX ex: <https://example.org/semantic-books/>
        PREFIX schema: <https://schema.org/>
        SELECT ?title ?year WHERE {
            ?book a ex:Book ; schema:name ?title ; ex:year ?year .
            FILTER (?year > 2000)
        }
        ORDER BY DESC(?year)
    """),

    ("3. Скільки книг кожного автора є у графі?", """
        PREFIX ex: <https://example.org/semantic-books/>
        PREFIX schema: <https://schema.org/>
        SELECT ?authorName (COUNT(?book) AS ?count) WHERE {
            ?book ex:writtenBy ?author .
            ?author schema:name ?authorName .
        }
        GROUP BY ?authorName
        ORDER BY DESC(?count) ?authorName
    """),

    ("4. Які книги жанру фентезі та хто їх видав?", """
        PREFIX ex: <https://example.org/semantic-books/>
        PREFIX schema: <https://schema.org/>
        SELECT ?title ?authorName ?publisherName WHERE {
            ?book ex:hasGenre ex:genre_fantasy ; schema:name ?title ;
                  ex:writtenBy ?author ; ex:publishedBy ?publisher .
            ?author schema:name ?authorName .
            ?publisher schema:name ?publisherName .
        }
        ORDER BY ?authorName ?title
    """),

    ("5. Які книги входять до серій і з яких країн автори серій?", """
        PREFIX ex: <https://example.org/semantic-books/>
        PREFIX schema: <https://schema.org/>
        SELECT ?title ?seriesName ?authorName ?countryName WHERE {
            ?book ex:inSeries ?series ; schema:name ?title .
            ?series ex:createdBy ?author ; schema:name ?seriesName .
            ?author ex:fromCountry ?country ; schema:name ?authorName .
            ?country schema:name ?countryName .
        }
        ORDER BY ?seriesName ?title
    """)
]

for question, sparql in queries:
    print("\n" + question)
    for row in g.query(sparql):
        print(" | ".join(str(value) for value in row))
