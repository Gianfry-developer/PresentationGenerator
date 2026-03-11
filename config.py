"""
Configurazione dell'applicazione
"""

import os
from pathlib import Path

# Configurazioni base
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
IMAGE_DIR = BASE_DIR / "images"

# Crea le directory se non esistono
for directory in [UPLOAD_DIR, OUTPUT_DIR, IMAGE_DIR]:
    directory.mkdir(exist_ok=True)

# Ollama configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = "llama3.2"

# Presentation settings
TARGET_PRESENTATION_MINUTES = 11
WORDS_PER_MINUTE = 130  # Velocità media di lettura professionale
TARGET_WORD_COUNT = TARGET_PRESENTATION_MINUTES * WORDS_PER_MINUTE  # ~1430 parole

# Slide settings
WORDS_PER_SLIDE_MIN = 50
WORDS_PER_SLIDE_MAX = 150
ESTIMATED_SLIDES = TARGET_WORD_COUNT // 100  # Circa 14-15 slides

# Formati supportati
SUPPORTED_FORMATS = {
    "docx": "Microsoft Word Document",
    "tex": "LaTeX Document",
    "md": "Markdown Document",
    "markdown": "Markdown Document"
}

# Prompt templates
SYSTEM_PROMPT = """Sei un esperto nella creazione di presentazioni professionali.
Il tuo compito è trasformare documenti in presentazioni efficaci per un pubblico professionale.
Mantieni sempre un tono formale e professionale.
"""

PRESENTATION_PROMPT_TEMPLATE = """
Crea una presentazione professionale dal seguente contenuto.

REQUISITI:
- Durata target: {duration} minuti di presentazione
- Numero di parole target: circa {word_count} parole nel testo delle slides
- Numero stimato di slides: {num_slides}
- Tono: Professionale e formale
- Includi riferimenti alle immagini disponibili quando appropriato

CONTENUTO DOCUMENTO:
{content}

IMMAGINI DISPONIBILI:
{images}

STRUTTURA RICHIESTA:
1. Slide titolo con titolo principale e sottotitolo
2. Agenda/Indice
3. Slides di contenuto (usa le immagini dove appropriato)
4. Slide di conclusione/summary
5. Slide "Domande?"

Genera la presentazione in formato JSON con questa struttura:
{{
  "title": "Titolo presentazione",
  "subtitle": "Sottotitolo",
  "author": "Autore",
  "slides": [
    {{
      "type": "title|content|image|conclusion",
      "title": "Titolo slide",
      "content": ["Punto 1", "Punto 2", ...],
      "notes": "Note per il relatore",
      "image": "nome_file_immagine.png" (opzionale)
    }}
  ]
}}
"""

CHAT_SYSTEM_PROMPT = """Sei un assistente AI specializzato nella creazione di presentazioni.
Puoi aiutare l'utente a:
- Caricare e analizzare documenti (DOCX, LaTeX, Markdown)
- Generare presentazioni professionali
- Modificare e ottimizzare le presentazioni
- Gestire modelli Ollama

Rispondi sempre in modo professionale e cordiale.
"""
