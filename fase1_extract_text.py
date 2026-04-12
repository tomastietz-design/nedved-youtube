#!/usr/bin/env python3
"""
FÁZE 1: Autonomní extrakce – žádné API nepotřeba.
Projde všech 970 souborů, vyextrahuje Honzovy věty,
filtruje hodnotný obsah, uloží na disk.
"""
import os, json, re
from pathlib import Path

SOURCE = "/home/claude/nedved-youtube"
OUT = "/home/claude/pipeline_output"
os.makedirs(OUT, exist_ok=True)

CHECKPOINT = f"{OUT}/fase1_checkpoint.json"
SNIPPETS_FILE = f"{OUT}/honza_snippets.jsonl"

# Klíčová slova signalizující hodnotný obsah
STORY_KEYWORDS = [
    "vzpomínám", "stalo se", "jednou", "příběh", "zažil", "zažila",
    "manželka", "manžel", "nikola", "nelinka", "zorinka", "dcera",
    "otec", "táta", "kamarád", "martin ambrož", "dalibor", "standa",
    "honza kováč", "sam owens", "kennedy", "roku 2013", "roku 2014",
    "roku 2015", "roku 2016", "roku 2017", "bylo mi", "byl jsem",
    "měl jsem", "přijel jsem", "letěl jsem", "volal jsem",
    "iniciо", "inizio", "konversky", "fapi", "myoweb",
]

PRINCIPLE_KEYWORDS = [
    "pravidlo", "princip", "klíč", "základ", "důvod proč",
    "funguje to", "nefunguje", "důležité je", "podstatné je",
    "vždy", "nikdy", "musíte", "musíš", "potřebujete",
    "chyba je", "problém je", "řešení je", "způsob je",
]

TACTIC_KEYWORDS = [
    "jak získat", "jak prodávat", "jak napsat", "jak natočit",
    "jak oslovit", "krok", "postup", "návod", "technika",
    "facebook reklama", "e-mail magnet", "webinář", "konverzka",
    "funnel", "trichtýř", "landing page", "přistávací stránka",
    "nadpis", "headline", "hook", "cta",
]

QUOTE_KEYWORDS = [
    "říkám", "říkávám", "říkal jsem", "vím že", "věřím že",
    "přesvědčen", "zjistil jsem", "naučil jsem se",
]

ALL_KEYWORDS = STORY_KEYWORDS + PRINCIPLE_KEYWORDS + TACTIC_KEYWORDS + QUOTE_KEYWORDS

def is_valuable(text):
    t = text.lower()
    return any(kw in t for kw in ALL_KEYWORDS)

def classify(text):
    t = text.lower()
    cats = []
    if any(kw in t for kw in STORY_KEYWORDS): cats.append("pribeh")
    if any(kw in t for kw in PRINCIPLE_KEYWORDS): cats.append("princip")
    if any(kw in t for kw in TACTIC_KEYWORDS): cats.append("taktika")
    if any(kw in t for kw in QUOTE_KEYWORDS): cats.append("citat")
    return cats or ["ostatni"]

def extract_honza_text(filepath):
    """Extrahuje text mluvený Honzou [A] z souboru."""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # Rozděl na segmenty podle mluvčích
    segments = re.split(r'\[([A-Z])\]', content)
    
    honza_blocks = []
    i = 1
    while i < len(segments) - 1:
        speaker = segments[i]
        text = segments[i+1].strip() if i+1 < len(segments) else ""
        if speaker == "A" and text:
            honza_blocks.append(text)
        i += 2
    
    # Pokud není [A] tagging, vezmi celý text (audiokniha)
    if not honza_blocks and content.strip():
        honza_blocks = [content]
    
    return " ".join(honza_blocks)

def process_file(filepath, filename):
    honza_text = extract_honza_text(filepath)
    
    # Rozděl na věty/odstavce
    sentences = re.split(r'(?<=[.!?])\s+', honza_text)
    
    snippets = []
    buffer = []
    
    for sent in sentences:
        sent = sent.strip()
        if len(sent) < 20:
            continue
        
        buffer.append(sent)
        
        # Tvoříme kontextové okno po 3 větách
        if len(buffer) >= 3:
            chunk = " ".join(buffer)
            if is_valuable(chunk):
                snippets.append({
                    "source": filename,
                    "text": chunk,
                    "categories": classify(chunk)
                })
            buffer = buffer[1:]  # posun okna
    
    # Zbytek
    if buffer:
        chunk = " ".join(buffer)
        if is_valuable(chunk):
            snippets.append({
                "source": filename,
                "text": chunk,
                "categories": classify(chunk)
            })
    
    return snippets

# Načti checkpoint
if os.path.exists(CHECKPOINT):
    with open(CHECKPOINT) as f:
        cp = json.load(f)
    processed_set = set(cp.get("processed", []))
    total_snippets = cp.get("total_snippets", 0)
else:
    processed_set = set()
    total_snippets = 0

files = sorted(Path(SOURCE).glob("*.txt"))
todo = [f for f in files if f.name not in processed_set]

print(f"Celkem souborů: {len(files)}")
print(f"Již zpracováno: {len(processed_set)}")
print(f"Zbývá: {len(todo)}")
print(f"Extrahovaných snippetů dosud: {total_snippets}")
print("Spouštím extrakci...\n")

# Zpracuj vše
with open(SNIPPETS_FILE, 'a', encoding='utf-8') as out:
    for i, filepath in enumerate(todo, 1):
        snippets = process_file(filepath, filepath.name)
        for s in snippets:
            out.write(json.dumps(s, ensure_ascii=False) + "\n")
        
        processed_set.add(filepath.name)
        total_snippets += len(snippets)
        
        if i % 50 == 0 or i == len(todo):
            # Ulož checkpoint
            with open(CHECKPOINT, 'w') as f:
                json.dump({
                    "processed": list(processed_set),
                    "total_snippets": total_snippets,
                    "total_files": len(files)
                }, f)
            print(f"[{len(processed_set)}/{len(files)}] hotovo | {total_snippets} snippetů extrahováno")

print(f"\n✓ HOTOVO! Celkem snippetů: {total_snippets}")
print(f"Soubor: {SNIPPETS_FILE}")
print(f"\nDalší krok: Claude analyzuje snippety v dávkách")
