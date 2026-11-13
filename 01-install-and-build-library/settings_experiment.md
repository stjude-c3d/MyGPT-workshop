# Settings experiment worksheet

Pick **one** setting to change, build a second library with it, and ask both libraries
the same questions. If you are in a group, have each person choose a different row, then
compare results at the end.

| Experiment | Library A (baseline) | Library B (changed) | What to look for |
|---|---|---|---|
| Chunk size | 1000 / overlap 200 | 300 / overlap 50 | Do precise facts get higher QRS? Are answers more fragmented? |
| Overlap | 1000 / overlap 200 | 1000 / overlap 0 | Are answers that span two chunks now incomplete? |
| Embedding model | nomic-embed-text | bge-m3 or MedCPT | Change in QRS for domain terms |
| Keyword search | BM25 on | BM25 off | Questions with IDs, gene names or acronyms |
| Reranker | off | on | Source order, answer quality, latency |
| Max chunks (chat setting, no rebuild needed) | 5 | 10 | Longer answers? More noise? Change in ARS? |

Name Library B `workshop-library-b`, or add the setting to the name, e.g. `workshop-chunk300`.

## Results

| Question | Setting | QRS (A) | QRS (B) | ARS (A) | ARS (B) | HI (A) | HI (B) | Which answer is better? Why? |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |
| | | | | | | | | |
| | | | | | | | | |
| | | | | | | | | |

## Reflect

1. Did the setting change the **retrieved chunks**, the **scores**, or both?
2. Did a higher QRS always mean a better answer? Note any case where it didn't. You
   will measure this properly in modules 3 and 4.
3. Which setting would you keep for your own documents?

You can also run this comparison from code in module 2: point
`02_query_api.ipynb` at each library and compare the two CSVs.
