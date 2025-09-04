# ATTRIBUTION

This file documents third-party resources, licences and which parts of the code are original vs. adapted.
The list and links below were taken from the NEA write-up submitted with this project (see References section of the NEA).

---

## Quick summary
- **What I wrote:** core glue code, UI rendering/annotations, board deepcopy logic, undo/redo, integration and project-specific layout/UX.
- **What I adapted / was inspired by:** Minimax + alpha-beta pseudocode and high-level algorithm ideas, certain implementation patterns (e.g. sliding moves helper, move-undo patterns) and rule descriptions from public sources. See the "Files / functions" section below for specifics.

---

## Third-party resources referenced (as listed in the NEA)

### Official / documentation
- Pygame docs (display/time/rect/draw/font etc.) - https://www.pygame.org/docs/ref/display.html, https://www.pygame.org/docs/ref/time.html, https://www.pygame.org/docs/ref/rect.html, https://www.pygame.org/docs/ref/draw.html, https://www.pygame.org/docs/ref/font.html.

- Python stdlib docs (threading, heapq) - https://docs.python.org/3/library/threading.html, https://docs.python.org/3/library/heapq.html.

### Algorithms / theory / encyclopaedia
- Wikipedia pages used:
  - Stalemate - https://en.wikipedia.org/wiki/Stalemate.
  - Promotion - https://en.wikipedia.org/wiki/Promotion_(chess).
  - Castling - https://en.wikipedia.org/wiki/Castling.
  - En passant - https://en.wikipedia.org/wiki/En_passant.
  - Checkmate - https://en.wikipedia.org/wiki/Checkmate.
  - Chess piece relative value - https://en.wikipedia.org/wiki/Chess_piece_relative_value.
  - Minimax pseudocode - https://en.wikipedia.org/wiki/Minimax#Pseudocode.
  - Alpha–beta pruning - https://en.wikipedia.org/wiki/Alpha–beta_pruning.

### Tutorials & videos (inspirations referenced in the NEA)
- Sebastian Lague - *Chess / Minimax / AI* (YouTube). Example linked in NEA: https://www.youtube.com/watch?v=U4ogK0MIzqk (and other timestamps).
- Eddie Sharick - video(s) used for UI/highlighting and move/undo logic: https://www.youtube.com/watch?v=o24J3WcBGLg (and playlist entries). Example: https://www.youtube.com/watch?v=mUdUlhEaA-o.

### Other helpful resources cited
- StackOverflow threads (e.g. Python `hash()` usage) - e.g. https://stackoverflow.com/questions/17585730/what-does-hash-do-in-python.
- GeeksforGeeks (heapq / data structures) - https://www.geeksforgeeks.org/heap-queue-or-heapq-in-python/?ref=ml_lbp.
- W3Schools (Dijkstra example, data-structures reference) - https://www.w3schools.com/dsa/dsa_algo_graphs_dijkstra.php.
- Rustic-chess (MVV-LVA explanation) - https://rustic-chess.org/search/ordering/mvv_lva.html.
- Physics & Maths Tutor (algorithm pseudocode reference) - PMT PDF used for merge sort pseudocode.
