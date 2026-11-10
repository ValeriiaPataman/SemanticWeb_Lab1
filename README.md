# Лабораторна робота №1 - RDF та SPARQL

Для роботи використано Python і бібліотеку RDFLib. Дані зберігаються у форматах Turtle та RDF/XML. Також реалізовано SPARQL-запити, візуалізацію графа та зв'язок із Wikidata.

### Основні файли
- main.py - створення RDF-графа та його візуалізація.

- queries.py - виконання п'яти SPARQL-запитів.

- wikidata.py - отримання даних із Wikidata.

- books.ttl, books.xml - збережений RDF-граф.

- graph.html - візуалізація графа.

### Запуск

Встановити бібліотеки:

```bash
pip install -r requirements.txt
```

Запустити файли в такому порядку:

```bash
python main.py
python queries.py
python wikidata.py
```

Для роботи з Wikidata потрібне підключення до інтернету.