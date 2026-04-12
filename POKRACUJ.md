# INSTRUKCE PRO NOVOU KONVERZACI

Zkopíruj toto a vlož do nové konverzace s Claudem:

---

Zpracovávám databázi Honzy Nedvěda. Fáze 1 hotová.

Prosím spusť tyto příkazy:
```
cd /home/claude
git clone https://github.com/tomastietz-design/nedved-youtube.git
cp nedved-youtube/honza_snippets.jsonl pipeline_output/
cp nedved-youtube/fase2_analyze.py .
cp nedved-youtube/fase2_next.py .
mkdir -p pipeline_output
python3 fase2_analyze.py
```

Stav: 19893 snippetů z 970 souborů extrahováno.
Zbývá: fáze 2 - inteligentní analýza a sestavení databáze.

---
