#!/usr/bin/env python3
import json
import os
import random

ANKI_BASE91_CHARS = '!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~'

def generate_anki_guid():
    num = random.randint(0, (1 << 64) - 1)
    result =[]
    for _ in range(10):
        result.append(ANKI_BASE91_CHARS[num %91])
        num //= 91
    return ''.join(result)

def load_deck():
    deck_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'deck.json')
    with open(deck_path, 'r', encoding='utf-8') as f:
        return json.load(f), deck_path

def save_deck(deck, deck_path):
    with open(deck_path, 'w', encoding='utf-8') as f:
        json.dump(deck, f, indent=4, ensure_ascii=False)

def select_tags(available_tags):
    if not available_tags:
        print("\nNo existing tags. Enter new tags separated by space (or press Enter to skip):")
        new_tags = input("Tags: ").strip()
        return new_tags.split() if new_tags else []
    
    print("\nAvailable tags:")
    for i, tag in enumerate(available_tags, 1):
        print(f"  {i}. {tag}")
    print("  0. Done selecting")
    print("  Or type new tags separated by space")
    
    selected = []
    while True:
        choice = input("Select tags: ").strip()
        if not choice or choice.lower() == 'done' or choice == '0':
            break
        
        try:
            indices = [int(x) for x in choice.split()]
            for idx in indices:
                if 1 <= idx <= len(available_tags):
                    tag = available_tags[idx - 1]
                    if tag not in selected:
                        selected.append(tag)
                        print(f"  Added: {tag}")
        except ValueError:
            for tag in choice.split():
                if tag and tag not in selected:
                    selected.append(tag)
                    print(f"  Added: {tag}")
    
    return selected

def get_existing_tags(deck):
    tags = set()
    for note in deck.get('notes', []):
        for tag in note.get('tags', []):
            tags.add(tag)
    return sorted(tags)

def main():
    deck, deck_path = load_deck()
    
    note_model_uuid = deck['note_models'][0]['crowdanki_uuid']
    
    available_tags = get_existing_tags(deck)
    
    print("=== Add Notes to Mantra Deck ===")
    print("Press Enter with empty text to exit.\n")
    
    while True:
        text = input("Text (use {{c1::word}} for cloze): ").strip()
        if not text:
            print("Exiting.")
            break
        
        extra = input("Extra (optional): ").strip()
        
        tags = select_tags(available_tags)
        
        note = {
            "__type__": "Note",
            "fields": [text, extra],
            "guid": generate_anki_guid(),
            "note_model_uuid": note_model_uuid,
            "tags": tags
        }
        
        deck['notes'].append(note)
        print(f"\nAdded note with GUID: {note['guid']}")
        print("-" * 40 + "\n")
    
    save_deck(deck, deck_path)
    print(f"Saved {len(deck['notes'])} notes to deck.json")

if __name__ == '__main__':
    main()