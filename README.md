# Downloader domande "Test di fine lezione"

Script CLI per scaricare le domande della sezione **Test di fine lezione** da una pagina di lezione LMS Multiversity.

## Requisiti
- Python 3 installato

## Utilizzo
Esegui lo script indicando l'URL della lezione. Le credenziali di base sono già precompilate.

```bash
python download_questions.py "https://lms.utsr.multiversity.click/videolezioni/0162206INF01/4"
```

Opzioni utili:
- `-o FILE` salva le domande anche in un file
- `-U USERNAME` e `-P PASSWORD` per sovrascrivere le credenziali di default

Le domande trovate vengono numerate e stampate su stdout; se la sezione non è presente, viene restituito un messaggio di errore.
