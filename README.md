# Downloader domande "Test di fine lezione"

Script CLI per scaricare le domande della sezione **Test di fine lezione** da una pagina di lezione LMS Multiversity.

## Requisiti
- Python 3 installato
- [Selenium](https://pypi.org/project/selenium/) installato (`pip install selenium`)
- Un driver disponibile nel `PATH` (es. `chromedriver` o `geckodriver`) per l'esecuzione headless

## Utilizzo
Esegui semplicemente lo script: usa automaticamente l'URL della lezione preconfigurata e le credenziali già incluse.

```bash
python download_questions.py
```

Se vuoi indicare un URL diverso oppure salvare anche su file, puoi passare i parametri opzionali:

```bash
python download_questions.py "<URL_lezione>" domande.txt
```

Le domande trovate vengono numerate e stampate su stdout; se la sezione non è presente, viene restituito un messaggio di errore.
