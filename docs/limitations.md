# Known Limitations and Ideas to Evaluate

Things noticed while building, to measure in Step 3 (eval) before changing anything.
These feed the README's "Limitations" and "Trade-offs" sections in Step 5.

## Chunking

### Orphaned headings at the end of a chunk

- **Seen in:** `playground/check_chunking.py` on the food-products guide (2026-11-18).
  The first chunk ends with `### 1.3 Law`; its content starts the next chunk.
- **Why it happens:** `chunk_text` packs paragraphs greedily, and a heading is just
  another paragraph, so it can be the last one that fits.
- **Why it matters:** the heading is the best summary of the section it introduces.
  Separated from its content, it adds noise to one chunk and is missing from the other.
- **Does overlap fix it?** Only partly. With `CHUNK_OVERLAP = 50` the heading is carried
  into the next chunk only if it falls in the last 50 characters, and the character cut
  can start mid-word or split a long heading. The orphan copy still stays in the first chunk.
- **Fix to try:** never end a chunk with a heading; carry it forward to start the next chunk.
- **How to decide:** compare recall@k with and without the fix on the Step 3 eval set.

### Character-based overlap cuts mid-word

- The overlap is the last `chunk_overlap` characters, so the next chunk can start mid-word.
- **Alternative to try:** paragraph-level overlap (repeat the previous chunk's last paragraph).
  Compare in Step 3.
