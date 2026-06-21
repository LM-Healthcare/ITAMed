# Istruzioni per la Revisione delle Discordanze

## Contesto

Due modelli LLM (Claude Opus 4.8 e GPT-5.5) hanno classificato indipendentemente 1.260 domande dell'esame SSM in categorie mediche. Su 1.260 domande, **126 presentano una discordanza** nella categoria primaria assegnata.

Il vostro compito è decidere, per ciascuna di queste 126 domande, quale classificazione è corretta.

---

## Come Compilare il File

1. Aprire **`discordances_to_review.xlsx`**

2. Per ogni riga:
   - Leggere la **domanda** (colonna D) e le **risposte** (colonne E–I)
   - Confrontare la **Categoria Claude** (colonna J) con la **Categoria GPT** (colonna K)
   - Nella colonna **verde** (L) — `CATEGORIA FINALE (compilare)` — scrivere la classificazione corretta

3. Opzioni possibili:
   - Scegliere la categoria di **Claude** (copiarla esattamente)
   - Scegliere la categoria di **GPT** (copiarla esattamente)
   - Proporre una **terza opzione** se nessuna delle due è adeguata

---

## Regole Importanti

- **Usare esattamente i nomi** dalla lista delle 28 categorie (vedi sotto)
- Per domande multispecialistiche: **separare con punto e virgola** (es. `Oncologia; Ematologia`)
- **Massimo 2 categorie** per domanda
- **Non lasciare celle vuote** — ogni riga deve avere una decisione

---

## Lista delle 28 Categorie Ammesse

1. Cardiologia e Cardiochirurgia
2. Chirurgia Generale
3. Gastroenterologia
4. Neurologia e Neurochirurgia
5. Pneumologia e Chirurgia Toracica
6. Ortopedia e Traumatologia
7. Endocrinologia
8. Ginecologia e Ostetricia
9. Pediatria
10. Urologia
11. Nefrologia
12. Ematologia
13. Oncologia
14. Malattie Infettive
15. Immunologia e Reumatologia
16. Dermatologia e Venereologia
17. Psichiatria
18. Oftalmologia
19. Otorinolaringoiatria
20. Anestesia e Rianimazione
21. Igiene, Epidemiologia e Statistica
22. Medicina del Lavoro
23. Medicina Legale
24. Diagnostica per Immagini e Medicina Nucleare
25. Genetica Medica
26. Farmacologia e Tossicologia
27. Nutrizione Clinica
28. Medicina Interna

---

## Dopo la Compilazione

Una volta completato il file, salvarlo e comunicare il completamento. Lo script `apply_expert_review.py` aggiornerà automaticamente il dataset ufficiale.
