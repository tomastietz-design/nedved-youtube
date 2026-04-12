#!/usr/bin/env python3
"""
FÁZE 2: Inteligentní analýza snippetů.
Claude čte dávky snippetů a extrahuje strukturovanou databázi.
Checkpointuje po každé dávce.
"""
import json, os
from pathlib import Path

OUT = "/home/claude/pipeline_output"
SNIPPETS = f"{OUT}/honza_snippets.jsonl"
CHECKPOINT = f"{OUT}/fase2_checkpoint.json"
BATCH_SIZE = 100  # snippetů na dávku pro Clauda

# Načti všechny snippety
with open(SNIPPETS) as f:
    all_snippets = [json.loads(l) for l in f]

# Načti checkpoint
if os.path.exists(CHECKPOINT):
    with open(CHECKPOINT) as f:
        cp = json.load(f)
else:
    cp = {"batch": 0, "total_batches": (len(all_snippets) // BATCH_SIZE) + 1}
    with open(CHECKPOINT, 'w') as f:
        json.dump(cp, f)

current_batch = cp["batch"]
total_batches = cp["total_batches"]
start = current_batch * BATCH_SIZE
end = min(start + BATCH_SIZE, len(all_snippets))

if start >= len(all_snippets):
    print("✓ Vše hotovo!")
    exit()

batch = all_snippets[start:end]

print(f"Dávka {current_batch+1}/{total_batches}")
print(f"Snippety {start+1}–{end} z {len(all_snippets)}")
print(f"Kategorie v této dávce: pribeh={sum(1 for s in batch if 'pribeh' in s['categories'])}, "
      f"princip={sum(1 for s in batch if 'princip' in s['categories'])}, "
      f"taktika={sum(1 for s in batch if 'taktika' in s['categories'])}")
print()
print("=== SNIPPETY PRO ANALÝZU ===")
for i, s in enumerate(batch):
    print(f"--- [{i+1}] {s['source'][:50]} | {','.join(s['categories'])} ---")
    print(s['text'][:400])
    print()

print("=== KONEC SNIPPETŮ ===")
print()
print("Claude: analyzuj výše a extrahuj do /home/claude/pipeline_output/fase2_results.jsonl")
print("Pak spusť: python3 /home/claude/fase2_next.py")
