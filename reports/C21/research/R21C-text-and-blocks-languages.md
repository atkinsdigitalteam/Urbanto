# R21C notes: text and blocks at once (for report C21)

Read on 2026-11-01. "Old" means older than about 5 years (before late 2021). "Third party" means not the vendor or author.
Numbers are quoted from the linked page unless the row says "measured" (simple arithmetic on published numbers, method shown).

---

### JetBrains MPS (docs read 2026-11-01; studies from 2016, old)
**How it works:**
- The program is a tree, not text. Edits change the tree directly through projections. Fowler's definition: "the core definition of a system should be held in a model and edited through projections" ([Fowler 2008, old](https://martinfowler.com/bliki/ProjectionalEditing.html)).
- The editor is built from nested cells: "an editor consists of cells, which themselves contain other cells, some text, or a UI component" ([MPS docs: Editor](https://www.jetbrains.com/help/mps/editor.html)).
- Typing is driven by completion: "In general, only the items suggested by a completion menu can be entered" ([MPS docs: Commanding the editor](https://www.jetbrains.com/help/mps/commanding-the-editor.html)).
- No parser: "every single next string is recognized as it is entered"; references are node IDs picked from completion, and programs are saved by serializing the tree (e.g. XML) ([Berger et al. 2016, PDF, old](https://gup.ub.gu.se/file/206790)).
- Invalid input in a cell turns it red while the model keeps the last valid value; type-over of the next character is on by default ([MPS docs: Editor](https://www.jetbrains.com/help/mps/editor.html)).
- "Grammar cells" were added to make text-like typing work, e.g. typing `3 * 4 + x` left to right and adding parentheses later, which needs "cross-tree editing" ([Voelter et al. 2016, PDF, old](https://www.pl.informatik.uni-mainz.de/files/2019/04/grammar-cells.pdf)).

**Good to use because:**
- Mixes tables, diagrams and text in one program, which a parser cannot easily do ([Berger et al. 2016, old](https://gup.ub.gu.se/file/206790)).
- Basic editing reached text-editor speed after a short training ([Berger et al. 2016, old](https://gup.ub.gu.se/file/206790)).
- Deleting a whole `if` with its body is one gesture; a beginner said "I used the possibility to clear the code just by going to the if statement" ([Berger et al. 2016, old](https://gup.ub.gu.se/file/206790)).

**Bad to use because:**
- Even the vendor says typing is an "illusion": "The editor gives you an illusion of editing text, which, however, has its limits" ([MPS docs](https://www.jetbrains.com/help/mps/commanding-the-editor.html)).
- Over-deletion and unpredictable caret: "Cursor placement was highly influential on what got deleted, which was not always what the user expects" ([Berger et al. 2016, old](https://gup.ub.gu.se/file/206790)).
- Expressions are the weak spot: "Editing expressions with their fine-grained tree structure is one of the major challenges in a projectional editor" ([Berger et al. 2016, old](https://gup.ub.gu.se/file/206790)).
- Invalid insertions: typed characters that do not bind leave code "not yet valid" ([Berger et al. 2016, old](https://gup.ub.gu.se/file/206790)).
- No standard storage format, so diff and version control must be rebuilt ([Fowler 2008, old](https://martinfowler.com/bliki/ProjectionalEditing.html)).
- Parentheses "at arbitrary locations in expressions" were only announced for MPS 3.1 (2014), years after release ([mbeddr blog 2014, old, MPS partner not vendor](https://mbeddr.com/2014/05/28/betterUsablity.html)).

**Numbers:**
| property | value | source |
|---|---|---|
| Study size | 19 (14 CS students + 5 industrial MPS users) | [Berger et al. 2016](https://gup.ub.gu.se/file/206790) |
| Training needed for basic editing parity | 45 minutes | [Berger et al. 2016](https://gup.ub.gu.se/file/206790) |
| Experts vs beginners, Task 3 / Task 4 | 3.08x / 1.92x faster | [Berger et al. 2016](https://gup.ub.gu.se/file/206790) |
| Experts vs text editor users, Task 3 / Task 4 | 3.03x / 1.77x faster | [Berger et al. 2016](https://gup.ub.gu.se/file/206790) |
| Prior survey of experienced MPS developers | 20 | [Voelter et al. 2016](https://www.pl.informatik.uni-mainz.de/files/2019/04/grammar-cells.pdf) |
| Effort spent building MPS editors at itemis | "roughly 30 person years" | [Voelter et al. 2016](https://www.pl.informatik.uni-mainz.de/files/2019/04/grammar-cells.pdf) |

**Take for Studio:**
- Do not make expressions and formulas projectional. Keep them as typed text inside a slot, and only make statements (loops, ifs, functions) into structure.
- Support left-to-right typing with operator precedence and late parentheses; that is the exact pain MPS needed 30 person years and grammar cells to fix.

---

### Scratch and block shapes (CACM 2017, old; Scratch wiki not verified)
**How it works:**
- Shape encodes grammar: "In Scratch, commands connect vertically with nubs and notches, whereas expressions are smooth shapes that fit into smooth holes" ([Bau et al. 2017, CACM, old](https://arxiv.org/abs/1705.09413)).
- A Boolean (diamond) expression only drops into a matching hole such as a loop test condition ([Bau et al. 2017](https://arxiv.org/abs/1705.09413)).
- Shapes can carry richer types: "OpenBlocks provides 14 connector shapes to represent different types" ([Bau et al. 2017](https://arxiv.org/abs/1705.09413)).

**Good to use because:**
- "Students report that the puzzle shapes are helpful for assembling programs" ([Bau et al. 2017](https://arxiv.org/abs/1705.09413)).
- Recognition over recall and visible grammar are the paper's core learnability claims ([Bau et al. 2017](https://arxiv.org/abs/1705.09413)).

**Bad to use because:**
- Viscosity: rearranging `(a/2+b/2)` to `(a+b)/2` "requires more gestures and more forethought than making the edits in text" ([Bau et al. 2017](https://arxiv.org/abs/1705.09413)).
- "Low density", hard "search and navigation" in a 2D canvas, and "collaboration and version control systems are difficult to use without a text representation" ([Bau et al. 2017](https://arxiv.org/abs/1705.09413)).

**Numbers:**
| property | value | source |
|---|---|---|
| Connector shapes in OpenBlocks | 14 | [Bau et al. 2017](https://arxiv.org/abs/1705.09413) |

**Take for Studio:**
- Use shape (or header style) to separate "statement container" from "value slot" from "condition slot"; the condition slot of a while/if should look different from a count field.
- Do not put arithmetic in blocks; it is the classic viscosity trap.

---

### Blockly (docs read 2026-11-01)
**How it works:**
- Each block has a "block-code generator", "a function that returns the code for that block as a string"; a language generator assembles them ([Blockly docs](https://docs.blockly.com/guides/create-custom-blocks/code-generation/overview)).
- "You can't "run" blocks directly. Instead you generate code strings, and then execute those" ([Blockly docs](https://docs.blockly.com/guides/create-custom-blocks/code-generation/overview)).
- Parentheses come from an `Order` precedence enum; they are added only "if the generated code is incorrect without them" ([Blockly docs](https://docs.blockly.com/guides/create-custom-blocks/code-generation/operator-precedence)).
- Types are modeled by connection checks: plain strings that must match between output and input ([Blockly docs](https://docs.blockly.com/guides/create-custom-blocks/inputs/connection-checks)).

**Good to use because:**
- Clean one-way design; built-in generators for five languages ([Blockly docs](https://docs.blockly.com/guides/create-custom-blocks/code-generation/overview)).
- Used as the base of MakeCode ([MakeCode language page](https://makecode.com/language)).

**Bad to use because:**
- No text-to-blocks in core. Issue "Convert from code to blocks" opened 2024-05-29 is still open (status Todo, 2026-07-08) ([GitHub #8183](https://github.com/RaspberryPiFoundation/blockly/issues/8183)).
- "Alice and Blockly provide non-editable views of text code" ([Bau et al. 2017, old](https://arxiv.org/abs/1705.09413)).
- Disabled blocks are skipped by generators; emitting them as commented-out code was pushed to a plugin ([GitHub #10468](https://github.com/RaspberryPiFoundation/blockly/issues/10468)).

**Numbers:**
| property | value | source |
|---|---|---|
| Built-in language generators | 5 (JS, Python, Lua, Dart, PHP) | [Blockly docs](https://docs.blockly.com/guides/create-custom-blocks/code-generation/overview) |
| Age of open code-to-blocks request | open since 2024-05-29 | [GitHub #8183](https://github.com/RaspberryPiFoundation/blockly/issues/8183) |

**Take for Studio:**
- A generator-only design (blocks to text) is easy; the hard part is text back to blocks. Design the text grammar first so it can always be parsed into containers.
- Copy the precedence-enum approach for printing formulas from nodes with minimal parentheses.

---

### Snap! (v10 2024-07-24; HISTORY lists 12.3.9 as newest)
**How it works:**
- v10 added a "LISP-like text syntax for blocks and scripts" and a "Lisp code..." context menu entry ([Snap! HISTORY.md](https://github.com/jmoenig/Snap/blob/master/HISTORY.md)).
- Round trip is SPLIT by "blocks" (text to syntax tree) and JOIN (tree to blocks); a "Code to Blocks to Code" library wraps this ([Snap! Lisp Syntax doc, 2024](https://github.com/jmoenig/Snap/blob/master/docs/Syntax.md)).
- "Blocks all the way": all palette blocks except hats and rings became custom blocks in v10 ([Snap! HISTORY.md](https://github.com/jmoenig/Snap/blob/master/HISTORY.md)).
- Visible stepping shows intermediate results of nested reporters ([Snap! HISTORY.md, 12.3.9](https://github.com/jmoenig/Snap/blob/master/HISTORY.md)).

**Good to use because:**
- Text is generated from blocks, so teams can diff and merge block code as text ([Snap! Lisp Syntax doc](https://github.com/jmoenig/Snap/blob/master/docs/Syntax.md)).

**Bad to use because:**
- Authors say it is "not (yet) meant for learners and end-users" and lacks "meaningful - if any - parsing error messages" ([Snap! Lisp Syntax doc](https://github.com/jmoenig/Snap/blob/master/docs/Syntax.md)).
- Comments are lost on text to blocks: "Characters following an un-escaped and unquoted semicolon are ignored by the parser" ([Snap! Lisp Syntax doc](https://github.com/jmoenig/Snap/blob/master/docs/Syntax.md)).

**Numbers:**
| property | value | source |
|---|---|---|
| Version that added text syntax | 10.0.0, 2024-07-24 | [Snap! HISTORY.md](https://github.com/jmoenig/Snap/blob/master/HISTORY.md) |

**Take for Studio:**
- A text form generated from the tree is cheap and useful for diffs even before full text editing exists.
- Parse errors need real messages from day one; Snap! shows what happens without them.

---

### Hazel and tylr (hazel.org read 2026-11-01; papers 2019 to 2025)
**How it works:**
- Incomplete programs have typed holes; Hazel says "There are no meaningless editor states" ([hazel.org](https://hazel.org/)).
- Evaluation continues past holes: "evaluation proceeds around holes, tracking the closure around each hole instance", with "fill-and-resume" ([Omar et al. POPL 2019, old](https://arxiv.org/abs/1805.00155)).
- Livelits: "a user-defined GUI embedded persistently into code" that expands to code like a macro and sees live closures ([PLDI 2021, old](https://pldi21.sigplan.org/details/pldi-2021-papers/34/Filling-Typed-Holes-with-Live-GUIs)).
- tall tylr repairs malformed text by inserting visible "obligations" (holes for missing operands, operators, delimiters) as you type ([Moon et al. 2025](https://arxiv.org/abs/2508.16848)).

**Good to use because:**
- Live values exist even while code is half typed ([POPL 2019](https://arxiv.org/abs/1805.00155)).
- tall tylr users liked it for typing new code: P8 said "the typing experience felt premium, bespoke, closer to video game than text editor" ([Moon et al. 2025, PDF](https://arxiv.org/pdf/2508.16848)).

**Bad to use because:**
- Ghost holes got in the way when changing existing code: "When I've created an invalid state [during refactoring], the placeholders often didn't feel helpful" ([Moon et al. 2025](https://arxiv.org/pdf/2508.16848)).
- Research system; tall tylr only supports whitespace-insensitive grammars "as of this writing" ([Moon et al. 2025](https://arxiv.org/pdf/2508.16848)).

**Numbers:**
| property | value | source |
|---|---|---|
| tall tylr study size | 9 participants | [Moon et al. 2025](https://arxiv.org/pdf/2508.16848) |
| Found it at least somewhat easy to use | 8 of 9 | [Moon et al. 2025](https://arxiv.org/pdf/2508.16848) |
| Obligations helped while writing | 7 of 9 | [Moon et al. 2025](https://arxiv.org/pdf/2508.16848) |
| Obligations got in the way while modifying | 5 of 9 | [Moon et al. 2025](https://arxiv.org/pdf/2508.16848) |
| Tried to delete ghost holes directly | at least 5 | [Moon et al. 2025](https://arxiv.org/pdf/2508.16848) |

**Take for Studio:**
- Invalid text while typing should become holes inside a still-valid container, so the Flow graph keeps running with the last good value or a hole.
- Livelits are the model for a `for` header with a count field: a GUI that is part of the code and expands to plain code.
- Let users delete or ignore auto-inserted placeholders; do not fight them.

---

### Pantograph (POPL 2025)
**How it works:**
- Typed structure editor that tries to stay well typed while staying fluid, using selection of "one-hole contexts" and type diffs ([Prinz et al. 2025](https://arxiv.org/abs/2411.16571)).

**Good to use because:**
- After a 1-hour tutorial "most of the participants" solved the tasks in Pantograph; 121 of 124 task attempts were solved ([Prinz et al. 2025, PDF](https://arxiv.org/pdf/2411.16571)).

**Bad to use because:**
- Slower than text; the slowest users "tried to input an entire expression consisting of multiple forms into a query such as 1 + 1", which the editor does not allow ([Prinz et al. 2025, PDF](https://arxiv.org/pdf/2411.16571)).

**Numbers:**
| property | value | source |
|---|---|---|
| Study size | 13 students (2 dropped from analysis) | [Prinz et al. 2025](https://arxiv.org/pdf/2411.16571) |
| Speed vs text editor | "1.4x slower on average" (geometric mean) | [Prinz et al. 2025](https://arxiv.org/pdf/2411.16571) |

**Take for Studio:**
- Typing `1 + 1` in one go must always work. Any editor that forces one form at a time loses text users.

---

### Lamdu (v0.8.1, site read 2026-11-01)
**How it works:**
- Non-text language with "rich code completions, without the possiblity of syntax errors" and automatic formatting ([lamdu.org](https://www.lamdu.org/)).
- Shows "the evaluation of each expression, whether the whole or a subexpression" as annotations under the code ([Lamdu README](https://github.com/lamdu/lamdu)).
- For recursive calls you step through invocations with arrows under the parameter ([Lamdu README](https://github.com/lamdu/lamdu)).

**Good to use because:**
- Values of each subexpression appear in place as you edit, and recursive calls can be stepped one by one ([Lamdu README](https://github.com/lamdu/lamdu)).

**Bad to use because:**
- Still "a technology preview and isn't yet recommended for production use" after starting in 2011 ([lamdu.org](https://www.lamdu.org/)).

**Numbers:**
| property | value | source |
|---|---|---|
| Version | 0.8.1 | [lamdu.org](https://www.lamdu.org/) |
| Started | 2011 | [lamdu.org](https://www.lamdu.org/) |

**Take for Studio:**
- "Arrows to step between invocations" is a compact way to preview each pass of a loop container.

---

### Unison (docs read 2026-11-01)
**How it works:**
- "Each Unison definition is identified by a hash of its syntax tree"; names are "separately stored metadata" ([Unison: The big idea](https://www.unison-lang.org/docs/the-big-idea/)).
- You still write text in a scratch file; once added, code is stored processed, and you get it back "pretty-printed, and using the latest names" ([The big idea](https://www.unison-lang.org/docs/the-big-idea/)).
- The codebase is "an immutable data structure where the elements of the structure never change" ([Unison FAQ](https://www.unison-lang.org/docs/usage-topics/general-faqs/)).

**Good to use because:**
- Renames are free and never break code, since references are hashes ([The big idea](https://www.unison-lang.org/docs/the-big-idea/)).
- Each definition is typechecked once and cached ([The big idea](https://www.unison-lang.org/docs/the-big-idea/)).

**Bad to use because:**
- Comments are dropped on `update` with no warning; a maintainer called it "by design" in Aug 2026 ([GitHub #6262](https://github.com/unisonweb/unison/issues/6262)).
- The problem is old: in 2019 comments "were discarded by the lexer" ([GitHub #443, old](https://github.com/unisonweb/unison/issues/443)).
- Your own formatting is replaced by the pretty printer ([The big idea](https://www.unison-lang.org/docs/the-big-idea/)).

**Numbers:**
| property | value | source |
|---|---|---|
| Hash | 512-bit SHA3 | [The big idea](https://www.unison-lang.org/docs/the-big-idea/) |

**Take for Studio:**
- Stable IDs for nodes and names-as-metadata are worth copying (renaming a variable should not touch the graph).
- If text is regenerated from a tree, comments must be tree nodes, or users lose them silently.

---

### Enso, formerly Luna (source read at commit 4135f92, 2026-11-01)
**How it works:**
- "These syntaxes are dual: visual and textual. Both are first-class" ([Enso syntax doc](https://github.com/enso-org/enso/blob/4135f929f1046ee4ab62d9d09c155377e8542a1f/docs/syntax/README.md)).
- Design rule: "New features must work across both" ([Enso philosophy](https://github.com/enso-org/enso/blob/4135f929f1046ee4ab62d9d09c155377e8542a1f/docs/enso-philosophy.md)).
- The file is plain text with a trailer after `#### METADATA ####`: an ID map of `[index, size] -> UUID` text spans, then JSON with node position and visualization per UUID ([default Main.enso](https://github.com/enso-org/enso/blob/4135f929f1046ee4ab62d9d09c155377e8542a1f/lib/scala/pkg/src/main/resources/default/src/Main.enso), [ensoFile.ts](https://github.com/enso-org/enso/blob/4135f929f1046ee4ab62d9d09c155377e8542a1f/app/ydoc-shared/src/ensoFile.ts)).
- Each node is a line `name = expression` in a function body ([default Main.enso](https://github.com/enso-org/enso/blob/4135f929f1046ee4ab62d9d09c155377e8542a1f/lib/scala/pkg/src/main/resources/default/src/Main.enso)).
- Graph edits are sent as text edits plus an `idMap`; `text/applyExpressionValue` swaps a literal (e.g. `98` to `99`) and "guarantees that the syntax tree is not changed", so no reparse ([Language server protocol doc](https://github.com/enso-org/enso/blob/4135f929f1046ee4ab62d9d09c155377e8542a1f/docs/language-server/protocol-language-server.md)).

**Good to use because:**
- Text stays the source of truth, so git and plain editors work; layout lives in metadata ([ensoFile.ts](https://github.com/enso-org/enso/blob/4135f929f1046ee4ab62d9d09c155377e8542a1f/app/ydoc-shared/src/ensoFile.ts)).
- Slider-style value edits are a fast path that skips recompiling ([protocol doc](https://github.com/enso-org/enso/blob/4135f929f1046ee4ab62d9d09c155377e8542a1f/docs/language-server/protocol-language-server.md)).

**Bad to use because:**
- Offsets are fragile: the docs warn an extra newline "is important for the precalculated metadata indexes" ([protocol doc](https://github.com/enso-org/enso/blob/4135f929f1046ee4ab62d9d09c155377e8542a1f/docs/language-server/protocol-language-server.md)).
- Editing the file outside the IDE can break the span-to-ID map (inference from the format above, not a published complaint).

**Numbers:**
| property | value | source |
|---|---|---|
| Metadata lines after marker | 2 (ID map, then JSON) | [ensoFile.ts](https://github.com/enso-org/enso/blob/4135f929f1046ee4ab62d9d09c155377e8542a1f/app/ydoc-shared/src/ensoFile.ts) |

**Take for Studio:**
- Closest prior art to "Studio language round-trips to Flow": text is canonical, each Flow node maps to a named binding, node layout and UI state live in a separate keyed sidecar.
- Key the sidecar by stable node IDs written in a way that survives edits (not raw character offsets).
- Copy the "value-only edit" fast path for sliders and count fields.

---

### Dark / Darklang (blog read 2026-11-01)
**How it works:**
- Dark had an online structured editor ([Dark blog 2023](https://blog.darklang.com/gpt/)). It was removed in February 2023 ("took it round back and shot it in the head last month") ([Dark blog, 28 Mar 2023](https://blog.darklang.com/gpt/)).
- Replacement: a new parser on tree-sitter, a language server and "a thin VS Code extension" ([Dark blog, 12 Mar 2024](https://blog.darklang.com/an-overdue-status-update/)).

**Good to use because:**
- Lesson value only: a clear public record of why a structured editor failed.

**Bad to use because:**
- Users rated the editor "somewhere between "Ok I guess" and "probably the worst part of Darklang"" ([Dark blog 2023](https://blog.darklang.com/gpt/)).
- Users could not "just type their code the way they wanted", and the editor was "pretty buggy" ([Dark blog 2024](https://blog.darklang.com/an-overdue-status-update/)).
- "Our online structured editor didn't make sense when the LLM is generating the code"; Dark Inc "has officially run out of money" ([Dark blog, 16 Jun 2025](https://blog.darklang.com/goodbye-dark-inc-welcome-darklang-inc/)).

**Numbers:**
| property | value | source |
|---|---|---|
| Structured editor removed | Feb 2023 | [Dark blog 2023](https://blog.darklang.com/gpt/) |
| Company out of money | announced 16 Jun 2025 | [Dark blog 2025](https://blog.darklang.com/goodbye-dark-inc-welcome-darklang-inc/) |

**Take for Studio:**
- Free typing must always be possible; structure is a view, not a gate.
- The language must accept pasted or AI-generated text, so a real parser with error recovery is required.

---

### Jupyter (study 2019, old)
**How it works:**
- Cells run in any order the user chooses; state lives in the kernel ([Pimentel et al. 2019, PDF, old](http://www.ic.uff.br/~leomurta/papers/pimentel2019a.pdf)).

**Good to use because:**
- Mixing text, code and results in one document is widely adopted ([Pimentel et al. 2019](http://www.ic.uff.br/~leomurta/papers/pimentel2019a.pdf)).

**Bad to use because:**
- Hidden state and out-of-order runs make results hard to reproduce ([Pimentel et al. 2019](http://www.ic.uff.br/~leomurta/papers/pimentel2019a.pdf)).

**Numbers:**
| property | value | source |
|---|---|---|
| Notebooks studied | 1.4 million from GitHub | [MSR 2019 page](https://2019.msrconf.org/details/msr-2019-papers/36/A-Large-scale-Study-about-Quality-and-Reproducibility-of-Jupyter-Notebooks) |
| Executed without errors | 24.11% of 863,878 attempted | [Pimentel et al. 2019](http://www.ic.uff.br/~leomurta/papers/pimentel2019a.pdf) |
| Same results as stored | 4.03% | [Pimentel et al. 2019](http://www.ic.uff.br/~leomurta/papers/pimentel2019a.pdf) |
| Out-of-order cells | 36.36% of 912,343 unambiguous notebooks | [Pimentel et al. 2019](http://www.ic.uff.br/~leomurta/papers/pimentel2019a.pdf) |

**Take for Studio:**
- Never let text blocks run in a user-chosen order; derive order from data flow like Flow does.

---

### Observable (runtime README and Framework docs read 2026-11-01)
**How it works:**
- "A variable defines a piece of state in a reactive program, akin to a cell in a spreadsheet" ([observablehq/runtime](https://github.com/observablehq/runtime)).
- "Code blocks in Markdown run in topological order determined by top-level variable references" ([Framework reactivity doc](https://github.com/observablehq/framework/blob/main/docs/reactivity.md)).
- Generators: "the runtime will pull values from the generator on every animation frame" ([observablehq/runtime](https://github.com/observablehq/runtime)).
- A variable is only computed if something observes its output ([observablehq/runtime](https://github.com/observablehq/runtime)).

**Good to use because:**
- Fixes Jupyter's order problem by design ([Framework reactivity doc](https://github.com/observablehq/framework/blob/main/docs/reactivity.md)).

**Bad to use because:**
- "Circular inputs are not allowed" ([observablehq/runtime](https://github.com/observablehq/runtime)), so loops must live inside a cell, not across cells.
- Main docs site returned 429 (rate limit) and was not verified.

**Numbers:** none published on the pages read.

**Take for Studio:**
- Text blocks in a Studio script should behave like Flow nodes: named outputs, recomputed in dependency order, lazy when not shown.
- Generator-style "yield per frame" is a model for streaming loop passes into a preview.

---

### Excel LET and LAMBDA (support pages read 2026-11-01; MSR blog Jan 2021, old)
**How it works:**
- LET names intermediate results inside one formula; the last argument is the result ([Microsoft: LET](https://support.microsoft.com/en-us/office/let-function-34842dd8-b92b-4d3f-b325-b8b8f9908999)).
- LAMBDA is named through Name Manager, with an optional comment of up to 255 characters shown in Insert Function and autocomplete ([Microsoft: LAMBDA](https://support.microsoft.com/en-us/office/lambda-function-bd212d27-1cd1-4321-a34a-ccbf254b8b67)).
- LAMBDA can be recursive; "With LAMBDA, Excel has become Turing-complete" ([MSR blog 2021, old](https://www.microsoft.com/en-us/research/blog/lambda-the-ultimatae-excel-worksheet-function/)).
- Microsoft later shipped a text editor for names: "Edit modules of named formulas using a single code editor", with indenting and comments ([Excel Labs README](https://github.com/microsoft/Excel-Labs)).

**Good to use because:**
- An expression used several times is calculated once, and names make formulas readable ([Microsoft: LET](https://support.microsoft.com/en-us/office/let-function-34842dd8-b92b-4d3f-b325-b8b8f9908999)).

**Bad to use because:**
- The built-in Name Manager was not enough for authoring, which is why the Advanced Formula Environment exists (inference from [Excel Labs README](https://github.com/microsoft/Excel-Labs): "designed for formula authoring").

**Numbers:**
| property | value | source |
|---|---|---|
| LET names | "supports up to 126" | [Microsoft: LET](https://support.microsoft.com/en-us/office/let-function-34842dd8-b92b-4d3f-b325-b8b8f9908999) |
| LAMBDA parameters | up to 253 | [Microsoft: LAMBDA](https://support.microsoft.com/en-us/office/lambda-function-bd212d27-1cd1-4321-a34a-ccbf254b8b67) |
| Name comment length | up to 255 characters | [Microsoft: LAMBDA](https://support.microsoft.com/en-us/office/lambda-function-bd212d27-1cd1-4321-a34a-ccbf254b8b67) |

**Take for Studio:**
- Allow `let` names inside Flow formula fields; they map to internal wires, not new nodes.
- A function's doc comment should become the help text and tooltip of the resulting sub-flow node.

---

### Houdini VEX and loops (docs read 2026-11-01)
**How it works:**
- "In a VEX snippet, use the chi, chf, chv, or chs functions wherever you want parameters", then the Create Parameters button "finds any channel references in the snippet that don't have corresponding parameters" and creates them ([SideFX: Spare parameters](https://www.sidefx.com/docs/houdini/network/spare.html)).
- `@name` reads and writes attributes; writing a missing one creates it ([SideFX: VEX snippets](https://www.sidefx.com/docs/houdini/vex/snippets.html)).
- Loops are Block Begin / Block End pairs with methods Fetch Feedback, Extract Piece or Point, Fetch Metadata ([SideFX: Block Begin](https://www.sidefx.com/docs/houdini/nodes/sop/block_begin.html)).
- Metadata gives `iteration`, `numiterations`, `value`, `ivalue`; Block End has Max Iterations, a Stop Condition evaluated before each pass, and Single Pass to show one piece ([SideFX: Looping](https://www.sidefx.com/docs/houdini/model/looping.html)).

**Good to use because:**
- Code creates its own UI: typed `ch` calls become sliders on the node ([SideFX: Spare parameters](https://www.sidefx.com/docs/houdini/network/spare.html)).
- Previewing one pass is built in, and the docs teach it: "start it at 1 and increase it to see the results of each loop" ([SideFX: Looping](https://www.sidefx.com/docs/houdini/model/looping.html)).

**Bad to use because:**
- No way to set a range from code; reply: "There is none", user: "Thats a lot of clicking IMHO"; RFEs exist ([SideFX forum 2022, third party users](https://www.sidefx.com/forum/topic/86085)).
- "Spare parameters only exist on a single node" ([SideFX: Spare parameters](https://www.sidefx.com/docs/houdini/network/spare.html)).
- Loops can blow up: "We recommend that you first start with 1 or 2 iterations until you know the loop is working"; Stop Condition is "not yet supported in compiled blocks" ([SideFX: Looping](https://www.sidefx.com/docs/houdini/model/looping.html)).

**Numbers:**
| property | value | source |
|---|---|---|
| Typed channel functions named in docs | 4 (chi, chf, chv, chs) | [SideFX: Spare parameters](https://www.sidefx.com/docs/houdini/network/spare.html) |
| `ivalue` needed above | "about 24 million" | [SideFX: Looping](https://www.sidefx.com/docs/houdini/model/looping.html) |

**Take for Studio:**
- `input("Radius", 5, min: 0, max: 20)` style calls in code should create exposed tool inputs, with range and hint in the call itself (fixing Houdini's gap).
- Loop container header = Max passes, Stop condition, Time limit, plus a "Single pass" scrubber for preview; default preview to the first 1 or 2 passes.

---

### Grasshopper loops: Anemone and native (group page read 2026-11-01; forum posts 2010 to 2018, old)
**How it works:**
- Two components: Loop Start and Loop End, "Where Loop End sends data back to Loop Start"; an Exit input (while-style), Repeats count, counter output, double-click to pause ([Anemone group page](https://www.grasshopper3d.com/group/anemone)).
- v0.4 added "fast" and "internalized" modes, each with an optional timeout ([Anemone group page](https://www.grasshopper3d.com/group/anemone)).
- Native Grasshopper had no loops: "Loops are a planned feature" (2010), still "in the pipeline" behind clusters (2011) ([Grasshopper forum, old](https://www.grasshopper3d.com/forum/topics/loop-component)).

**Good to use because:**
- Shows that a pass count, an exit condition and a timeout are the three parameters users need on a loop ([Anemone group page](https://www.grasshopper3d.com/group/anemone)).

**Bad to use because:**
- Slow per pass: "takes up over 5 seconds with NO data at all being passed" ([McNeel forum 2018, old, third party](https://discourse.mcneel.com/t/anemones-fast-loop-end-is-slow/63573)).
- Start/End pairs are separate components, so the loop body is not visually enclosed (inference from the two-component design on the [group page](https://www.grasshopper3d.com/group/anemone)).
- food4rhino page returned 405 and was not verified.

**Numbers:**
| property | value | source |
|---|---|---|
| Group members | 516 | [Anemone group page](https://www.grasshopper3d.com/group/anemone) |
| Empty-loop overhead reported | over 5 seconds | [McNeel forum 2018](https://discourse.mcneel.com/t/anemones-fast-loop-end-is-slow/63573) |

**Take for Studio:**
- Flow already has true containers; keep them. The text form should map one `for`/`while` block to one container, never to a start/end pair.

---

### Elefront (forum post 2013, old; food4rhino not verified)
**How it works:**
- "treat a 3d Rhino model as a data base, where each object "knows" what it is"; bake with attributes, and reference objects back by key-value filters ([McNeel forum 2013, old](https://discourse.mcneel.com/t/elefront-for-grasshopper/1026)).

**Good to use because:**
- Lets scripts find model objects by meaning (user text) instead of by manual picking ([McNeel forum 2013](https://discourse.mcneel.com/t/elefront-for-grasshopper/1026)).

**Bad to use because:**
- Docs domain now a placeholder ("This domain may be for sale", docs.elefront.io, read 2026-11-01), so current docs not verified.

**Numbers:** none verified.

**Take for Studio:**
- The language needs a query form like `objects where use = "housing"` that maps to a Flow reference node, since lineage and attributes already exist in Studio.

---

### Rhino 8 ScriptEditor and NodeInCode (developer docs read 2026-11-01)
**How it works:**
- ScriptEditor runs IronPython, Python 3 and C#, with in-file package lines like `#r: numpy` and `#r "nuget: RestSharp, 110.2.0"` ([Rhino dev: ScriptEditor](https://developer.rhino3d.com/guides/scripting/scripting-command/)).
- Grasshopper script components: in Script-Mode "the input parameters are magically defined and set before your script starts"; "Scripts in Grasshopper are not stored as files" ([Rhino dev: GH Python](https://developer.rhino3d.com/guides/scripting/scripting-gh-python/)).
- In SDK-Mode the `RunScript` signature mirrors the parameters, and the component is "capable of updating parameters on the component, when the RunScript signature is manually edited" ([Rhino dev: GH Python](https://developer.rhino3d.com/guides/scripting/scripting-gh-python/)).
- `Rhino.NodeInCode.Components` "Provides access to all Grasshopper runtime components" via `FindComponent` (since v6.0) ([RhinoCommon API](https://developer.rhino3d.com/api/rhinocommon/rhino.nodeincode.components)).

**Good to use because:**
- Two-way sync between function signature and node ports is a working, shipping example of code/UI round trip ([Rhino dev: GH Python](https://developer.rhino3d.com/guides/scripting/scripting-gh-python/)).

**Bad to use because:**
- Calling components from code is awkward: multi-output components return a nested list, staff reply "you are effectively creating a tree" ([McNeel forum 2020, old](https://discourse.mcneel.com/t/rhino-nodeincode/103190)).

**Numbers:**
| property | value | source |
|---|---|---|
| NodeInCode available since | Rhino v6.0 | [RhinoCommon API](https://developer.rhino3d.com/api/rhinocommon/rhino.nodeincode.components) |

**Take for Studio:**
- A Studio function header `fn offset(curve: Curve, d: Length = 2m) -> Curve` should be the sub-flow's port list, with edits flowing both ways.
- Every Flow node should be callable from text by name with named outputs (avoid NodeInCode's positional list of outputs).

---

### Notion blocks (help and engineering blog read 2026-11-01; blog May 2021, about 5 years old)
**How it works:**
- Every line is a block that can be dragged with the `⋮⋮` handle; the `/` menu adds content or applies actions ([Notion help](https://www.notion.com/help/writing-and-editing-basics)).
- Markdown shortcuts: "Type `#` followed by `space` to create an H1 heading" ([Notion help](https://www.notion.com/help/writing-and-editing-basics)).
- "Turn into" changes type; "Changing the type of a block doesn't change the block's properties or content" ([Notion engineering blog 2021](https://www.notion.com/blog/data-model-behind-notion)).
- "In Notion, indentation is structural" ([Notion engineering blog 2021](https://www.notion.com/blog/data-model-behind-notion)).

**Good to use because:**
- Typing stays primary; structure appears from short typed triggers ([Notion help](https://www.notion.com/help/writing-and-editing-basics)).

**Bad to use because:**
- No user-study numbers found on the pages read.

**Numbers:** none published on the pages read.

**Take for Studio:**
- Typing `for ` or `repeat ` at line start should turn the line into a container (Notion's `# ` pattern); `/` opens a node picker.
- A hover handle on each statement for drag and "turn into" (e.g. `for each` to `repeat`, keeping the body).

---

### Pencil Code and Droplet (papers 2017, old; repo read 2026-11-01)
**How it works:**
- Droplet aims to "re-envision 'block programming' as 'text editing'"; JavaScript and CoffeeScript modes; a language plugs in via a parser class that marks blocks, sockets and indents ([Droplet repo](https://github.com/droplet-editor/droplet)).
- "In dual-mode editors, the text code is the primary representation of the program, and blocks are a projected user interface view derived by parsing" ([Bau et al. 2017, old](https://arxiv.org/abs/1705.09413)).
- Pencil.cc hybrid: drag a block from the palette into a text editor and it "turns into the textual equivalent" ([Weintrop & Wilensky 2017, old](https://ccl.northwestern.edu/2017/Weintrop_Wilensky_IDC_2017.pdf)).

**Good to use because:**
- Text keeps spacing and formatting because text is primary ([Bau et al. 2017](https://arxiv.org/abs/1705.09413)).
- Students used blocks to find new constructs, especially control flow (numbers below) ([Weintrop & Holbert 2017, old](https://ccl.netlogo.org/2017/Blocks.pdf)).
- After 10 weeks of Java, the hybrid group's view of authenticity rose while the text group's fell (U = 437.5, p = .01) ([Weintrop & Wilensky 2017](https://ccl.northwestern.edu/2017/Weintrop_Wilensky_IDC_2017.pdf)).

**Bad to use because:**
- "Error-recovery heuristics convert simple text syntax errors to special error blocks, but complex errors can prevent mode switching" ([Bau et al. 2017](https://arxiv.org/abs/1705.09413)).
- At mid-study the hybrid was rated as authentic as blocks and below text; the authors say it "was not successful in addressing the authenticity concern" at that point ([Weintrop & Wilensky 2017](https://ccl.northwestern.edu/2017/Weintrop_Wilensky_IDC_2017.pdf)).

**Numbers:**
| property | value | source |
|---|---|---|
| Time in blocks mode (high school / graduate) | 92% / 91% | [Weintrop & Holbert 2017](https://ccl.netlogo.org/2017/Blocks.pdf) |
| Text-to-blocks switches logged | 217 | [Weintrop & Holbert 2017](https://ccl.netlogo.org/2017/Blocks.pdf) |
| Switches made to add a command | 65.4% | [Weintrop & Holbert 2017](https://ccl.netlogo.org/2017/Blocks.pdf) |
| Added control blocks that were first use | 86.7% | [Weintrop & Holbert 2017](https://ccl.netlogo.org/2017/Blocks.pdf) |
| Hybrid study size | 90 students, 15 weeks, 3 conditions | [Weintrop & Wilensky 2017](https://ccl.northwestern.edu/2017/Weintrop_Wilensky_IDC_2017.pdf) |
| Droplet repo commits | 1,489 | [Droplet repo](https://github.com/droplet-editor/droplet) |

**Take for Studio:**
- Users flip to blocks to discover loops and conditions, then type. Keep a palette of containers next to the text, and dragging one in inserts its text.
- Switching views must never be blocked by an error; map the broken span to an error block or hole.

---

### Microsoft MakeCode (docs read 2026-11-01)
**How it works:**
- Blocks are TypeScript functions annotated with `//% block` comments; "Both Blocks and Static Python are converted to Static TypeScript" ([MakeCode: Defining blocks](https://makecode.com/defining-blocks), [MakeCode languages](https://makecode.com/language)).
- Code that cannot become blocks becomes "a grey JavaScript block to preserve it", converted back on switching to text ([MakeCode Arcade docs](https://arcade.makecode.com/blocks/javascript-blocks)).
- Block comments appear as a comment line above the code in JavaScript or Python ([MakeCode: Comments](https://makecode.microbit.org/blocks/comments)).

**Good to use because:**
- Round trip never loses code: unknown code is kept as an opaque block ([MakeCode Arcade docs](https://arcade.makecode.com/blocks/javascript-blocks)).
- Comments survive blocks to text ([MakeCode: Comments](https://makecode.microbit.org/blocks/comments)).

**Bad to use because:**
- "The code in JavaScript blocks cannot be edited" ([MakeCode Arcade docs](https://arcade.makecode.com/blocks/javascript-blocks)).
- Narrow shapes: a for-loop only becomes a block if it starts at 0, uses `<` or `<=` with the variable on the left, and has all three parts ([pxt-sample docs](https://microsoft.github.io/pxt-sample/docs/blocks/javascript-blocks.html)).
- Users get stuck: "Oops, something went wrong trying to convert your code" and "It tells me nothing about why it can't convert" ([MakeCode forum 2023 to 2026, third party](https://forum.makecode.com/t/im-stuck-in-javascript-and-cant-convert-back-to-blocks/18177)).
- Even generated JS sometimes failed to return to blocks; maintainer: "Yep, this is a bug!" ([MakeCode forum 2022](https://forum.makecode.com/t/javascript-wont-translate-back-to-blocks/11786)).
- `blockId` "is serialized in block code so changing it will break your users" ([MakeCode: Defining blocks](https://makecode.com/defining-blocks)).

**Numbers:**
| property | value | source |
|---|---|---|
| for-loop rules for block conversion | 4 listed conditions | [pxt-sample docs](https://microsoft.github.io/pxt-sample/docs/blocks/javascript-blocks.html) |
| Forum thread unresolved span | Feb 2023 to Aug 2026 | [MakeCode forum](https://forum.makecode.com/t/im-stuck-in-javascript-and-cant-convert-back-to-blocks/18177) |

**Take for Studio:**
- Copy "preserve unknown code as a block", but make that block editable as text inline.
- When conversion fails, point at the exact line and reason.
- Accept many text spellings of a loop (e.g. any start value) instead of one canonical shape.

---

### Greenfoot Stride, frame-based editing (papers 2016, old)
**How it works:**
- Frames are statements; each has frame slots (bodies) and text slots (conditions, expressions). "Each frame is entered by pressing a single key", e.g. 'i' for if ([Brown, Altadmri, Kölling 2016, PDF, old](https://kar.kent.ac.uk/54394/1/frames.pdf)).
- Expressions are typed as text with "exactly the same keystrokes as in a text editor"; auto-inserted brackets can be overtyped ([Brown et al. 2016](https://kar.kent.ac.uk/54394/1/frames.pdf)).
- Disabling code is an explicit state, not comment-out: comment-out is "a convenient abuse of the comment construct"; disabled frames are shown blurred ([Brown et al. 2016](https://kar.kent.ac.uk/54394/1/frames.pdf)).
- Errors sit on slots with a red wavy underline; frames are rarely invalid except through their slots ([Brown et al. 2016](https://kar.kent.ac.uk/54394/1/frames.pdf)).

**Good to use because:**
- Big drop in time spent on pure syntax edits and with non-compiling code (numbers below) ([Price et al. ICER 2016, old](https://kar.kent.ac.uk/56259/1/icer027-priceA.pdf)).
- Stride "progressed faster and completed more objectives" ([Price et al. 2016](https://kar.kent.ac.uk/56259/)).

**Bad to use because:**
- Objective completion difference was not significant ([Price et al. 2016](https://kar.kent.ac.uk/56259/1/icer027-priceA.pdf)).
- Blocks-like tools are often "perceived as less authentic by students" (cited prior work) ([Price et al. 2016](https://kar.kent.ac.uk/56259/1/icer027-priceA.pdf)).

**Numbers:**
| property | value | source |
|---|---|---|
| Study size | 32 middle-school students, logs for 24 (13 Java, 11 Stride) | [Price et al. 2016](https://kar.kent.ac.uk/56259/1/icer027-priceA.pdf) |
| Time on purely syntactic edits (median) | Java 321 s vs Stride 94 s (p < 0.001) | [Price et al. 2016](https://kar.kent.ac.uk/56259/1/icer027-priceA.pdf) |
| Ratio of the two medians | 3.4x (measured: 321 / 94) | computed from [Price et al. 2016](https://kar.kent.ac.uk/56259/1/icer027-priceA.pdf) |
| Time with non-compilable code (mean) | Java 1447 s vs Stride 1000 s (p = 0.045) | [Price et al. 2016](https://kar.kent.ac.uk/56259/1/icer027-priceA.pdf) |
| Objectives completed (mean) | 60.4% vs 69.9% (not significant) | [Price et al. 2016](https://kar.kent.ac.uk/56259/1/icer027-priceA.pdf) |
| Model-predicted insertion time (CogTool, not users) | Scratch 4.9 s, NetBeans 5.1 s, Frames 1.6 s | [Brown et al. 2016](https://kar.kent.ac.uk/54394/1/frames.pdf) |

**Take for Studio:**
- This is the closest proven pattern for "type fast, containers have UI": statements are containers, everything inside a header field is text.
- Add "disable pass/container" as a real state that also mutes the Flow node, instead of comment-out.

---

### Strype (KCL, repo read 2026-11-01)
**How it works:**
- "a frame-based editor for Python that runs entirely in the browser, designed for use in secondary schools" ([Strype repo](https://github.com/k-pet-group/Strype)).
- Frames are inserted "using a single key command"; Strype converts to Python ([micro:bit news 2022, third party](https://microbit.org/news/2022-02-24/introducing-strype-a-framebased-editor/)).
- Removes indentation and bracket matching chores ([PyCon UK 2025 talk abstract](https://pretalx.com/pyconuk-2025/talk/GD9PX7/)).

**Good to use because:**
- Active: roadmap items for 2026 (charting Q2, micro:bit simulator Q3) ([Strype repo](https://github.com/k-pet-group/Strype)).

**Bad to use because:**
- Could not verify how pasted Python text becomes frames; KCL blog returned 403.

**Numbers:** none published on the pages read.

**Take for Studio:**
- Evidence that the frame pattern transfers from Java (Stride) to a mainstream text language.

---

### GP Blocks (site read 2026-11-01; CACM 2017, old)
**How it works:**
- "a free, general-purpose blocks programming language (similar to MIT's Scratch)" ([gpblocks.org](https://gpblocks.org/)).
- GP and Stride "let programmers enter blocks through an in-line autocomplete mechanism" ([Bau et al. 2017](https://arxiv.org/abs/1705.09413)).

**Good to use because:**
- Keyboard entry of blocks is the efficiency fix for experts ([Bau et al. 2017](https://arxiv.org/abs/1705.09413)).

**Bad to use because:**
- Site gives no version, makers or text view details ([gpblocks.org](https://gpblocks.org/)).

**Numbers:** none.

**Take for Studio:**
- Autocomplete-to-insert-container is required even in block view.

---

### Live previews per iteration (cross-cutting)
**How it works:**
- Bret Victor: "Show the data"; a loop timeline "depicts not just the flow, but all of the data calculated in that flow"; switch tables to plots when there are many passes ([Victor 2012, old](http://worrydream.com/LearnableProgramming/)).
- ShellVis puts a slider on the `for` line that reports how many passes ran; "Scrubbing the slider left and right, the user can see what other values this variable takes on", and the body annotations follow the selected pass ([Horowitz & Heer 2026](https://arxiv.org/pdf/2609.11000)).
- ShellVis first showed every pass side by side but dropped it: "these designs disrupt the visual correspondence between the visualizer and source code" ([Horowitz & Heer 2026](https://arxiv.org/pdf/2609.11000)).
- Houdini: Single Pass shows one piece; Max Iterations stepping ([SideFX: Looping](https://www.sidefx.com/docs/houdini/model/looping.html)). Lamdu: arrows step through invocations ([Lamdu README](https://github.com/lamdu/lamdu)). Hazel: per-hole closures ([POPL 2019](https://arxiv.org/abs/1805.00155)).

**Good to use because:**
- ShellVis participants were "unanimously expressing that ShellVis was helpful, comfortable to use, and desirable for their own work" ([Horowitz & Heer 2026](https://arxiv.org/pdf/2609.11000)).

**Bad to use because:**
- Projection Boxes (CHI 2020) also faced the layout problem; per ShellVis they "offer low peripheral visibility" ([Horowitz & Heer 2026](https://arxiv.org/pdf/2609.11000)). The Projection Boxes pages themselves returned 503 and were not verified.

**Numbers:**
| property | value | source |
|---|---|---|
| ShellVis study size | 7 participants, 1 to 20 years shell experience | [Horowitz & Heer 2026](https://arxiv.org/pdf/2609.11000) |

**Take for Studio:**
- Loop container header gets a pass scrubber ("pass 3 of 12"); the container body and the viewport show that pass. A small strip of thumbnails is optional, not the default.
- Cap preview cost: compute passes lazily and stop at the time limit, like Houdini's advice to start with 1 or 2 passes.

---

### Cross-cutting: what breaks round-tripping (synthesis of the sections above)
- **Invalid code while typing:** dual-mode editors can refuse to switch ([Bau et al. 2017](https://arxiv.org/abs/1705.09413); [MakeCode forum](https://forum.makecode.com/t/im-stuck-in-javascript-and-cant-convert-back-to-blocks/18177)). Fix: holes and error blocks ([hazel.org](https://hazel.org/); [Moon et al. 2025](https://arxiv.org/abs/2508.16848)).
- **Comments:** dropped by Unison ([#6262](https://github.com/unisonweb/unison/issues/6262)) and Snap! text parsing ([Syntax doc](https://github.com/jmoenig/Snap/blob/master/docs/Syntax.md)); kept by MakeCode as block comments ([MakeCode](https://makecode.microbit.org/blocks/comments)).
- **Formatting:** lost when text is regenerated from a tree ([Unison](https://www.unison-lang.org/docs/the-big-idea/)); kept when text is primary ([Bau et al. 2017](https://arxiv.org/abs/1705.09413); [Enso](https://github.com/enso-org/enso/blob/4135f929f1046ee4ab62d9d09c155377e8542a1f/app/ydoc-shared/src/ensoFile.ts)).
- **Unsupported shapes:** MakeCode grey blocks for non-canonical loops ([pxt-sample](https://microsoft.github.io/pxt-sample/docs/blocks/javascript-blocks.html)).
- **Commented-out code vs disabled:** Stride separates them ([Brown et al. 2016](https://kar.kent.ac.uk/54394/1/frames.pdf)); Blockly skips disabled blocks in output ([#10468](https://github.com/RaspberryPiFoundation/blockly/issues/10468)).
- **Layout and UI state:** needs a sidecar keyed by stable IDs ([Enso Main.enso](https://github.com/enso-org/enso/blob/4135f929f1046ee4ab62d9d09c155377e8542a1f/lib/scala/pkg/src/main/resources/default/src/Main.enso)).

**Take for Studio (overall):**
- Text is canonical and always typeable; containers (for, for each, while, if, fn) are projections of statements with header fields; expressions stay text; comments and "disabled" are tree nodes; layout and previews live in a keyed sidecar; errors become holes, never a blocked switch.

General code sketch of such a text form (illustrative only, not Studio code):

```
# offset every plot edge until area target is met
fn shrink(plot: Region, step: Length = 0.5m) -> Region {
  let target = plot.area * 0.8
  var r = plot
  repeat max 40 until (r.area <= target) limit 2s {   # header fields: Max passes, Stop when, Time limit
    r = offset(r, -step)
  }
  return r
}
```
