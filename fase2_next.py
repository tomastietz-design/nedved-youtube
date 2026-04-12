#!/usr/bin/env python3
"""Posun checkpoint na další dávku."""
import json, os

CHECKPOINT = "/home/claude/pipeline_output/fase2_checkpoint.json"
with open(CHECKPOINT) as f:
    cp = json.load(f)
cp["batch"] += 1
with open(CHECKPOINT, 'w') as f:
    json.dump(cp, f)
print(f"Checkpoint posunut na dávku {cp['batch']}/{cp['total_batches']}")
if cp["batch"] >= cp["total_batches"]:
    print("✓ Všechny dávky zpracovány! Spusť: python3 /home/claude/fase3_merge.py")
else:
    print(f"Spusť: python3 /home/claude/fase2_analyze.py")
