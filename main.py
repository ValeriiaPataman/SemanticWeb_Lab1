from rdflib import Graph, Namespace, Literal, RDF, OWL, URIRef
import networkx as nx
import plotly.graph_objects as go

EX = Namespace("https://example.org/semantic-books/")
SCHEMA = Namespace("https://schema.org/")
WD = Namespace("http://www.wikidata.org/entity/")

g = Graph()
g.bind("ex", EX)
g.bind("schema", SCHEMA)
g.bind("owl", OWL)
g.bind("wd", WD)


def add_item(code, kind, name):
    item = EX[code]
    g.add((item, RDF.type, EX[kind]))
    g.add((item, SCHEMA.name, Literal(name, lang="uk")))
    return item


countries = [
    ("ukraine", "Україна"),
    ("britain", "Велика Британія"),
    ("usa", "США")
]

publishers = [
    ("collins", "Коллінз Крайм Клаб"),
    ("doubleday", "Даблдей"),
    ("old_lion", "Видавництво Старого Лева"),
    ("bloomsbury", "Блумсбері"),
    ("mcelderry", "Маргарет К. Макелдеррі Букс")
]

genres = [
    ("detective", "Детективи / трилери"),
    ("horror", "Жахи / містика"),
    ("fantasy", "Фентезі")
]

authors = [
    ("agatha", "Агата Крісті", "britain", "Q35064"),
    ("king", "Стівен Кінг", "usa", "Q39829"),
    ("pavliuk", "Ілларіон Павлюк", "ukraine", None),
    ("rowling", "Джоан Роулінґ", "britain", "Q34660"),
    ("clare", "Кассандра Клер", "usa", None)
]

series = [
    ("poirot", "Еркюль Пуаро", "agatha"),
    ("potter", "Гаррі Поттер", "rowling"),
    ("instruments", "Знаряддя Смерті", "clare")
]

# Код, назва, рік першого видання, автор, жанри, видавець, серія
books = [
    ("orient", "Вбивство у «Східному експресі»", 1934, "agatha", ["detective"], "collins", "poirot"),
    ("nile", "Смерть на Нілі", 1937, "agatha", ["detective"], "collins", "poirot"),
    ("carrie", "Керрі", 1974, "king", ["horror"], "doubleday", None),
    ("shining", "Сяйво", 1977, "king", ["horror"], "doubleday", None),
    ("pet", "Кладовище домашніх тварин", 1983, "king", ["horror"], "doubleday", None),
    ("ash", "Білий попіл", 2018, "pavliuk", ["detective", "horror"], "old_lion", None),
    ("dance", "Танець недоумка", 2019, "pavliuk", ["detective"], "old_lion", None),
    ("darkness", "Я бачу, вас цікавить пітьма", 2020, "pavliuk", ["detective", "horror"], "old_lion", None),
    ("hp1", "Гаррі Поттер і філософський камінь", 1997, "rowling", ["fantasy"], "bloomsbury", "potter"),
    ("hp2", "Гаррі Поттер і таємна кімната", 1998, "rowling", ["fantasy"], "bloomsbury", "potter"),
    ("hp3", "Гаррі Поттер і в'язень Азкабану", 1999, "rowling", ["fantasy"], "bloomsbury", "potter"),
    ("city1", "Місто Кісток", 2007, "clare", ["fantasy"], "mcelderry", "instruments"),
    ("city2", "Місто Попелу", 2008, "clare", ["fantasy"], "mcelderry", "instruments"),
    ("city3", "Місто Скла", 2009, "clare", ["fantasy"], "mcelderry", "instruments")
]

for code, name in countries:
    add_item("country_" + code, "Country", name)

for code, name in publishers:
    add_item("publisher_" + code, "Publisher", name)

for code, name in genres:
    add_item("genre_" + code, "Genre", name)

for code, name, country, wiki_id in authors:
    author = add_item("author_" + code, "Author", name)
    g.add((author, EX.fromCountry, EX["country_" + country]))
    if wiki_id:
        g.add((author, OWL.sameAs, WD[wiki_id]))

for code, name, author in series:
    book_series = add_item("series_" + code, "Series", name)
    g.add((book_series, EX.createdBy, EX["author_" + author]))

for code, name, year, author, book_genres, publisher, book_series in books:
    book = add_item("book_" + code, "Book", name)
    g.add((book, EX.year, Literal(year)))
    g.add((book, EX.writtenBy, EX["author_" + author]))
    g.add((book, EX.publishedBy, EX["publisher_" + publisher]))
    for genre in book_genres:
        g.add((book, EX.hasGenre, EX["genre_" + genre]))
    if book_series:
        g.add((book, EX.inSeries, EX["series_" + book_series]))

print("Кількість RDF-трійок:", len(g))
print("Кількість сутностей:", len(set(g.subjects(RDF.type, None))))
print("\nПерші 8 трійок:")
for subject, predicate, obj in list(g)[:8]:
    print(subject, "->", predicate, "->", obj)

print("\nДані про книгу 'Сяйво':")
for predicate, obj in g.predicate_objects(EX.book_shining):
    print(predicate, "->", obj)

g.serialize("books.ttl", format="turtle")
g.serialize("books.xml", format="xml")
print("\nСтворено books.ttl і books.xml")

# Візуалізація зв'язків між сутностями (без текстових властивостей)
network = nx.DiGraph()
colors = {
    "Book": "#d8ecff", "Author": "#ffdfd1", "Genre": "#fff1ad",
    "Publisher": "#d8f4df", "Series": "#e9dcff", "Country": "#e1e1e1"
}
for subject, kind in g.subject_objects(RDF.type):
    name = str(g.value(subject, SCHEMA.name))
    network.add_node(str(subject), name=name, kind=str(kind).split("/")[-1])

for subject, predicate, obj in g:
    if isinstance(obj, URIRef) and str(subject) in network and str(obj) in network:
        network.add_edge(str(subject), str(obj), relation=str(predicate).split("/")[-1])

positions = nx.spring_layout(network, seed=5, k=1.1, iterations=180)
edge_x, edge_y, middle_x, middle_y, edge_names = [], [], [], [], []
for start, end, data in network.edges(data=True):
    x1, y1 = positions[start]
    x2, y2 = positions[end]
    edge_x += [x1, x2, None]
    edge_y += [y1, y2, None]
    middle_x.append((x1 + x2) / 2)
    middle_y.append((y1 + y2) / 2)
    edge_names.append(data["relation"])

lines = go.Scatter(x=edge_x, y=edge_y, mode="lines",
                   line=dict(color="#b5bdc9", width=1), hoverinfo="skip")
edge_hover = go.Scatter(x=middle_x, y=middle_y, mode="markers",
                        marker=dict(size=7, color="#aaa", opacity=0.5),
                        text=edge_names, hovertemplate="Зв'язок: %{text}<extra></extra>")

nodes = list(network.nodes())
node_points = go.Scatter(
    x=[positions[n][0] for n in nodes],
    y=[positions[n][1] for n in nodes],
    mode="markers+text",
    marker=dict(size=20, color=[colors[network.nodes[n]["kind"]] for n in nodes],
                line=dict(width=1, color="#555")),
    text=[network.nodes[n]["name"] for n in nodes],
    textposition="top center", textfont=dict(size=10),
    hovertext=[network.nodes[n]["kind"] + ": " + network.nodes[n]["name"] for n in nodes],
    hovertemplate="%{hovertext}<extra></extra>"
)

fig = go.Figure(data=[lines, edge_hover, node_points])
fig.update_layout(title="Граф книг: наведіть курсор на вузол або зв'язок",
                  showlegend=False, width=1500, height=1000,
                  xaxis=dict(visible=False), yaxis=dict(visible=False),
                  plot_bgcolor="white", margin=dict(l=20, r=20, t=60, b=20))
fig.write_html("graph.html", include_plotlyjs=True)
print("Створено graph.html")
