# Research code — WebMD drug reviews

Notebooks and scripts for loading WebMD-style drug review data, sentiment analysis (VADER, classical ML, LSTM, RoBERTa), and optional scraping.

## Python environment

Use Python 3.10+ (3.10 or 3.11 recommended).

### Install dependencies (one command)

From this folder:

```bash
pip install -r requirements.txt
```

If you use a virtual environment first:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### npm-style shortcut

If you have Node/npm installed, you can run:

```bash
npm run install-deps
```

That runs `python3 -m pip install -r requirements.txt`.

## Optional: spaCy English model

If you use spaCy with the `en_core_web_sm` model:

```bash
python -m spacy download en_core_web_sm
```

## Project layout (high level)

- `drug-analysis.ipynb` — broader pipeline (NLTK, sklearn, TensorFlow LSTM, transformers).
- `drug-analysis-roberta.ipynb` — RoBERTa sentiment on reviews.
- `drug-scraping.py` — Scrapy spider for WebMD (respect site terms and robots).
- CSV outputs such as `roberta_results.csv` / `webmd_1000.csv` are produced by the notebooks; large files are candidates for `.gitignore` if you use version control.

## PyTorch note

`torch` is installed from PyPI. For GPU-specific builds (CUDA), see [https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/) and adjust your install command if needed.
# webmd-sentiment-analysis
# webmd-sentiment-analysis
