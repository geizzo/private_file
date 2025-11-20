# Downloader domande "Test di fine lezione"

Script CLI per scaricare le domande della sezione **Test di fine lezione** da una pagina di lezione LMS Multiversity.

## Requisiti
- Python 3 installato

## Utilizzo
Esegui lo script indicando l'URL della lezione. Le credenziali richieste sono già incluse nello script.

```bash
python download_questions.py "https://lms.utsr.multiversity.click/videolezioni/0162206INF01/4"
```

Opzionalmente puoi passare un secondo argomento per salvare anche su file:

```bash
python download_questions.py "<URL_lezione>" domande.txt
```

Le domande trovate vengono numerate e stampate su stdout; se la sezione non è presente, viene restituito un messaggio di errore.
