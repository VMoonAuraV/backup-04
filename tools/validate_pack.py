#!/usr/bin/env python3
"""Validate the canonical GRE Context Lab JSON pack without third-party dependencies."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "packs" / "starter.json"
def fail(message):
    print(f"INVALID: {message}", file=sys.stderr)
    raise SystemExit(1)
def main():
    try: data = json.loads(PACK.read_text(encoding="utf-8"))
    except Exception as exc: fail(f"Cannot parse {PACK}: {exc}")
    for key in ("words", "comparisons", "se"):
        if not isinstance(data.get(key), list): fail(f"{key} must be an array")
    word_ids = [w.get("id") for w in data["words"]]
    if any(not isinstance(x, str) or not x for x in word_ids): fail("every word must have a non-empty string id")
    if len(set(word_ids)) != len(word_ids): fail("word IDs must be unique")
    word_id_set = set(word_ids)
    for i, word in enumerate(data["words"], 1):
        for key in ("word", "zh", "definition", "nuance", "group"):
            if not isinstance(word.get(key), str) or not word[key].strip(): fail(f"word #{i} ({word.get('id')}) is missing {key}")
        examples = word.get("examples")
        if not (isinstance(word.get("example"), str) and word["example"].strip()) and not (isinstance(examples, list) and examples):
            fail(f"word #{i} ({word.get('id')}) needs example or non-empty examples")
        if examples is not None:
            if not isinstance(examples, list): fail(f"word #{i} ({word.get('id')}) examples must be an array")
            for j, example in enumerate(examples, 1):
                if isinstance(example, str):
                    if not example.strip(): fail(f"word #{i} example #{j} is empty")
                elif not isinstance(example, dict) or not isinstance(example.get("text"), str) or not example["text"].strip():
                    fail(f"word #{i} example #{j} must be a non-empty string or an object with text")
    for key in ("comparisons", "se"):
        ids = [q.get("id") for q in data[key]]
        if any(not isinstance(x, str) or not x for x in ids) or len(set(ids)) != len(ids): fail(f"{key} IDs must be non-empty and unique")
        for q in data[key]:
            if not isinstance(q.get("prompt"), str) or not q["prompt"].strip(): fail(f"{key} item {q.get('id')} has no prompt")
            if not isinstance(q.get("options"), list) or len(q["options"]) < 3: fail(f"{key} item {q.get('id')} must have at least 3 options")
            refs = q.get("words")
            if not isinstance(refs, list) or not refs: fail(f"{key} item {q.get('id')} must reference at least one word")
            unknown = set(refs) - word_id_set
            if unknown: fail(f"{key} item {q.get('id')} references unknown words: {sorted(unknown)}")
            if not isinstance(q.get("explanation"), str) or not q["explanation"].strip(): fail(f"{key} item {q.get('id')} has no explanation")
            if key == "comparisons":
                answer = q.get("answer")
                if not isinstance(answer, int) or not 0 <= answer < len(q["options"]): fail(f"comparison {q.get('id')} has an invalid answer index")
            else:
                answers = q.get("answers")
                if (not isinstance(answers, list) or len(answers) != 2 or len(set(answers)) != 2 or any(not isinstance(a, int) or not 0 <= a < len(q["options"]) for a in answers)):
                    fail(f"SE item {q.get('id')} must have two distinct valid answer indices")
    print(f"OK: {len(data['words'])} words, {len(data['comparisons'])} distinctions, {len(data['se'])} SE questions")
if __name__ == "__main__": main()
