# Question Classification — Metodologia e Risultati

## Panoramica

La classificazione delle 1.260 domande del dataset ITAMed è stata condotta attraverso un protocollo di **dual-annotator LLM** con successiva **adjudicazione da esperti medici** per le discordanze. L'approccio garantisce riproducibilità, trasparenza e rigore scientifico nella tassonomia specialistica.

---

## Pipeline di Classificazione

```
┌─────────────────────┐     ┌─────────────────────┐
│   Claude Opus 4.8   │     │      GPT-5.5        │
│  (Annotatore 1)     │     │  (Annotatore 2)     │
└──────────┬──────────┘     └──────────┬──────────┘
           │                           │
           ▼                           ▼
┌──────────────────────────────────────────────────┐
│         Inter-Rater Agreement Analysis           │
│   (Tabella di contingenza + Cohen's Kappa)       │
└──────────────────────┬───────────────────────────┘
                       │
           ┌───────────┴───────────┐
           │                       │
     Concordanti               Discordanti
     (1134 domande)            (126 domande)
           │                       │
           ▼                       ▼
   Categoria confermata    ┌───────────────────┐
                           │  Expert Review    │
                           │  (Medici esperti) │
                           └────────┬──────────┘
                                    │
                                    ▼
                           Categoria finale
                           (dataset aggiornato)
```

---

## Modelli Utilizzati

| Modello | Provider | Model ID (API) | Ruolo |
|:--------|:---------|:---------------|:------|
| Claude Opus 4.8 | Anthropic | `claude-opus-4-8` | Annotatore primario |
| GPT-5.5 | OpenAI | `gpt-5.5` | Annotatore secondario |

---

## Tassonomia Medica (28 categorie)

La tassonomia è stata definita a priori sulla base delle Scuole di Specializzazione italiane:

| # | Categoria |
|:-:|:----------|
| 1 | Cardiologia e Cardiochirurgia |
| 2 | Chirurgia Generale |
| 3 | Gastroenterologia |
| 4 | Neurologia e Neurochirurgia |
| 5 | Pneumologia e Chirurgia Toracica |
| 6 | Ortopedia e Traumatologia |
| 7 | Endocrinologia |
| 8 | Ginecologia e Ostetricia |
| 9 | Pediatria |
| 10 | Urologia |
| 11 | Nefrologia |
| 12 | Ematologia |
| 13 | Oncologia |
| 14 | Malattie Infettive |
| 15 | Immunologia e Reumatologia |
| 16 | Dermatologia e Venereologia |
| 17 | Psichiatria |
| 18 | Oftalmologia |
| 19 | Otorinolaringoiatria |
| 20 | Anestesia e Rianimazione |
| 21 | Igiene, Epidemiologia e Statistica |
| 22 | Medicina del Lavoro |
| 23 | Medicina Legale |
| 24 | Diagnostica per Immagini e Medicina Nucleare |
| 25 | Genetica Medica |
| 26 | Farmacologia e Tossicologia |
| 27 | Nutrizione Clinica |
| 28 | Medicina Interna |

Ogni domanda può ricevere **1 o 2 categorie** (separate da punto e virgola) nel caso di domande chiaramente multispecialistiche.

---

## Prompt di Classificazione

Il prompt è **identico** per entrambi i modelli, per garantire un confronto equo:

```
Sei un esperto medico italiano specializzato nella classificazione di domande
dell'esame SSM (Specializzazione in Medicina).

Il tuo compito è classificare ogni domanda in una o più delle seguenti
categorie mediche:

1. Cardiologia e Cardiochirurgia
2. Chirurgia Generale
[... tutte le 28 categorie ...]
28. Medicina Interna

REGOLE:
1. Assegna la categoria PRINCIPALE più appropriata per ogni domanda.
2. Se la domanda è chiaramente multispecialistica (es. un caso clinico che
   coinvolge due discipline in modo significativo), puoi assegnare fino a
   2 categorie, separate da punto e virgola.
3. NON assegnare più di 2 categorie per domanda.
4. Usa ESATTAMENTE i nomi delle categorie come elencati sopra.
5. Se una domanda riguarda un argomento trasversale (es. anatomia, fisiologia,
   biochimica) classificala in base al contesto clinico/organo/sistema coinvolto.
6. "Medicina Interna" va usata SOLO per domande generalistiche che non rientrano
   chiaramente in nessuna altra specialità.

Rispondi SOLO in formato JSON, un array di oggetti con "id" (numero della
domanda nel batch) e "categorie" (stringa con la/le categoria/e).
```

---

## Parametri di Esecuzione

| Parametro | Claude Opus 4.8 | GPT-5.5 |
|:----------|:----------------|:--------|
| Temperature | — (default) | 1 |
| Max tokens (output) | 2000 | 2000 |
| Batch size | 10 domande | 10 domande |
| Retry su errore | 3 tentativi | 3 tentativi |
| Rate limit pause | 1s tra batch | 1s tra batch |
| Formato output | JSON array | JSON array |

---

## Dati di Input

- **Totale domande**: 1.260 (140 domande × 9 anni: 2017–2025)
- **Fonte**: File ufficiali verificati (`Official/IT/ITAMed_{year}_Checked.xlsx`)
- **Informazioni fornite al modello**: codice domanda, testo della domanda, 5 opzioni di risposta (A–E)
- **NON forniti**: risposta corretta, anno, immagini (per evitare bias)

---

## Risultati — Inter-Rater Agreement

### Statistiche Generali

| Metrica | Valore |
|:--------|-------:|
| Totale domande | 1.260 |
| Concordanza categoria primaria | 1.134 / 1.260 (**90,0%**) |
| Concordanza esatta (full string) | 880 / 1.260 (69,8%) |
| **Cohen's Kappa (categoria primaria)** | **κ = 0,8950** |
| Discordanze da risolvere | 126 |

### Interpretazione (Landis & Koch, 1977)

| Range κ | Interpretazione |
|:--------|:----------------|
| < 0,00 | Poor |
| 0,00–0,20 | Slight |
| 0,21–0,40 | Fair |
| 0,41–0,60 | Moderate |
| 0,61–0,80 | Substantial |
| **0,81–1,00** | **Almost perfect** ← il nostro risultato |

Il valore **κ = 0,8950** indica un accordo **quasi perfetto** tra i due annotatori LLM, ben al di sopra della soglia convenzionale di 0,80 per considerare affidabile una tassonomia.

### Kappa per Categoria (one-vs-all)

| Categoria | κ |
|:----------|--:|
| Medicina Interna | 1,0000 |
| Psichiatria | 1,0000 |
| Oftalmologia | 0,9814 |
| Ortopedia e Traumatologia | 0,9579 |
| Immunologia e Reumatologia | 0,9457 |
| Neurologia e Neurochirurgia | 0,9447 |
| Ginecologia e Ostetricia | 0,9440 |
| Endocrinologia | 0,9411 |
| Medicina del Lavoro | 0,9367 |
| Urologia | 0,9330 |
| Cardiologia e Cardiochirurgia | 0,9268 |
| Genetica Medica | 0,9177 |
| Ematologia | 0,9167 |
| Igiene, Epidemiologia e Statistica | 0,9165 |
| Otorinolaringoiatria | 0,9103 |
| Nutrizione Clinica | 0,9087 |
| Dermatologia e Venereologia | 0,9008 |
| Pneumologia e Chirurgia Toracica | 0,9005 |
| Gastroenterologia | 0,8822 |
| Anestesia e Rianimazione | 0,8775 |
| Malattie Infettive | 0,8731 |
| Medicina Legale | 0,8698 |
| Nefrologia | 0,8643 |
| Chirurgia Generale | 0,8319 |
| Pediatria | 0,8142 |
| Farmacologia e Tossicologia | 0,7829 |
| Oncologia | 0,7184 |
| Diagnostica per Immagini e Medicina Nucleare | 0,6951 |

Tutte le categorie raggiungono almeno un accordo "substantial" (κ > 0,60).

### Discordanze per Anno

| Anno | Discordanze | % |
|:-----|:-----------:|:---:|
| 2017 | 12 | 8,6% |
| 2018 | 13 | 9,3% |
| 2019 | 13 | 9,3% |
| 2020 | 11 | 7,9% |
| 2021 | 15 | 10,7% |
| 2022 | 15 | 10,7% |
| 2023 | 23 | 16,4% |
| 2024 | 10 | 7,1% |
| 2025 | 14 | 10,0% |

L'anno 2023 presenta un numero leggermente superiore di discordanze, probabilmente dovuto al formato PDF atipico di quell'anno.

---

## Struttura della Cartella

```
Question_Classification/
├── README.md                              ← Questo file
│
├── scripts/
│   ├── classify_claude.py                 # Classificazione con Claude Opus 4.8
│   ├── classify_gpt.py                    # Classificazione con GPT-5.5
│   ├── compute_agreement.py              # Analisi inter-rater agreement
│   └── apply_expert_review.py            # Applica le decisioni degli esperti al dataset
│
├── results/
│   ├── claude/                            # JSON: classificazioni Claude (1 file/anno)
│   │   ├── 2017_classifications_claude.json
│   │   ├── ...
│   │   └── 2025_classifications_claude.json
│   │
│   ├── gpt/                              # JSON: classificazioni GPT (1 file/anno)
│   │   ├── 2017_classifications_gpt.json
│   │   ├── ...
│   │   └── 2025_classifications_gpt.json
│   │
│   └── agreement/                         # Risultati dell'analisi di concordanza
│       ├── agreement_report.txt           #   Report testuale completo
│       ├── contingency_table.xlsx         #   Matrice di contingenza 28×28
│       ├── discordances.xlsx              #   Lista completa discordanze
│       └── discordances.json              #   Discordanze in formato JSON
│
└── expert_review/
    ├── discordances_to_review.xlsx        # FILE DA COMPILARE (esperti medici)
    └── instructions.md                    # Istruzioni per la compilazione
```

---

## Workflow per gli Esperti Medici

### 1. Aprire il file di revisione

Aprire `expert_review/discordances_to_review.xlsx`.

### 2. Per ogni riga (126 domande)

- Leggere la **domanda** e le **5 opzioni di risposta**
- Confrontare la **Categoria Claude** con la **Categoria GPT**
- Decidere quale classificazione è corretta (o proporne una terza se nessuna delle due è adeguata)
- Scrivere la decisione nella colonna verde **"CATEGORIA FINALE (compilare)"**

### 3. Regole per la compilazione

- Usare **esattamente** i nomi delle categorie dalla tassonomia (vedi sopra)
- Per domande multispecialistiche: separare con punto e virgola (es. `"Oncologia; Ematologia"`)
- Massimo 2 categorie per domanda
- Non lasciare celle vuote

### 4. Applicare le decisioni al dataset

```bash
cd Question_Classification/scripts
python apply_expert_review.py
```

Lo script:
- Verifica che tutte le 126 righe siano compilate
- Crea un backup dei file originali in `Official/IT/backup_pre_review/`
- Aggiorna tutti i file del dataset (XLSX per anno + JSON/XLSX completi)

---

## Riproducibilità

Per rieseguire l'intera pipeline da zero:

```bash
# 1. Classificazione Claude (richiede ANTHROPIC_API_KEY)
export ANTHROPIC_API_KEY="sk-ant-..."
python scripts/classify_claude.py

# 2. Classificazione GPT (richiede OPENAI_API_KEY)
export OPENAI_API_KEY="sk-..."
python scripts/classify_gpt.py

# 3. Analisi di concordanza
python scripts/compute_agreement.py

# 4. [Dopo revisione esperti] Applicazione al dataset
python scripts/apply_expert_review.py
```

---

## Nota Metodologica

La scelta di un protocollo dual-annotator con LLM segue le best practice della letteratura per la costruzione di dataset annotati:

1. **Indipendenza**: i due modelli classificano senza conoscere l'output dell'altro
2. **Stesso prompt**: garantisce equità nel confronto
3. **Cohen's Kappa**: metrica standard per l'accordo inter-annotatore che corregge per il caso
4. **Adjudicazione esperta**: le discordanze vengono risolte da professionisti del dominio (medici specialisti), non dall'algoritmo

Questo approccio è più robusto rispetto alla classificazione con un singolo modello, perché:
- Identifica le domande "ambigue" o di confine tra specialità
- Fornisce una misura quantitativa dell'affidabilità della tassonomia
- Garantisce che ogni assegnazione contestata sia validata da un esperto umano
