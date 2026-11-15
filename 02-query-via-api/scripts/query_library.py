#!/usr/bin/env python3
"""Query a MyGPT library from the command line.

Examples (run from the repo root):
    python 02-query-via-api/scripts/query_library.py --list
    python 02-query-via-api/scripts/query_library.py --question "What is version control?"
    python 02-query-via-api/scripts/query_library.py --questions data/BioASQ/questions_final.csv \
        --out workshop_outputs/02_query_results.csv

Connection settings come from .env (see .env.example); flags override them.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd  # noqa: E402

from common.mygpt_client import MyGPTClient  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--list", action="store_true", help="list libraries and exit")
    p.add_argument("--question", help="ask a single question")
    p.add_argument("--questions", help="CSV with a 'question' or 'questions' column")
    p.add_argument("--dataset", help="library name (default: MYGPT_DATASET)")
    p.add_argument("--max-chunks", type=int, default=5)
    p.add_argument("--no-score", action="store_true", help="skip ARS/HI scoring")
    p.add_argument("--out", help="write results to this CSV")
    args = p.parse_args()

    client = MyGPTClient.from_env()
    if args.dataset:
        client.dataset = args.dataset

    if args.list:
        for d in client.list_datasets():
            print(f"{d.get('dataset_name')}\t{d.get('dataset_size', '')}")
        return

    if args.question:
        questions = [args.question]
    elif args.questions:
        questions_frame = pd.read_csv(args.questions)
        question_column = next(
            (column for column in ("question", "questions") if column in questions_frame),
            None,
        )
        if question_column is None:
            p.error("questions CSV must contain a 'question' or 'questions' column")
        questions = questions_frame[question_column].dropna().tolist()
    else:
        p.error("use --list, --question or --questions")

    rows = []
    for i, q in enumerate(questions, 1):
        print(f"[{i}/{len(questions)}] {q}", file=sys.stderr)
        try:
            rows.append(client.ask(q, max_chunks=args.max_chunks, score=not args.no_score))
        except Exception as exc:  # keep going on a single failure
            print(f"   failed: {exc}", file=sys.stderr)
            rows.append({"question": q, "error": str(exc)})

    df = pd.DataFrame(rows)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        df.drop(columns=["context"], errors="ignore").to_csv(args.out, index=False)
        print(f"saved {len(df)} rows to {args.out}", file=sys.stderr)
    for r in rows:
        print(f"\nQ: {r['question']}\nA: {r.get('answer', r.get('error'))}")
        print(f"   QRS={r.get('QRS')}  ARS={r.get('ARS')}  HI={r.get('HI')}")


if __name__ == "__main__":
    main()
