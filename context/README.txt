This folder holds optional supplemental documents for local retrieval (RAG).

Why this exists:
- Resume + job description are often not enough for deep interview prep.
- You can add role frameworks, leadership principles, architecture notes,
  and domain glossaries as plain text files.

How it is used:
- At startup, the app reads all *.txt files from /context.
- Files are chunked and embedded with sentence-transformers locally.
- The top chunks are included as additional context for question generation.
