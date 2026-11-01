# C21: a script node (Python and C#), and a language that is text and blocks at once

Research and design only. Write one report with pictures (mockups rendered to PNG). No Studio code is shared or wanted.

## Context

Urbanto Studio is a desktop CAD program for urban designers (Windows, C# .NET 10, Avalonia 12, built to compile natively with AOT, so no
runtime reflection) with a node editor called Flow (like Grasshopper). Flow already has an Expression node and formula fields, loops,
for-each containers and sub-flows that open in place. Shapes are exact lines and arcs; data flows as typed lists with lineage.

The owner's words: "Python script node: very important, with a C# option too. Later we also need a semi-visual coding editor for our own
language; let the cloud do research on how we can do it, so the user can do text coding quickly, for example a loop becomes a container
that has UI for how many times or until... so it is still text coding but with UI, with the option to use text or block containers."

## What to do

1. **Script node, Python and C#.** How do Grasshopper (GhPython, the Rhino 8 Script Editor with CPython 3 and C#), Dynamo (Python
   node, CPython3), Houdini (Python SOP, VEX), Blender (Python), Revit (pyRevit), TouchDesigner, Unreal (Python), and C# scripting hosts do
   it? For a .NET 10 AOT desktop app: options for Python (embedded CPython via a C API binding, pythonnet, a separate Python process over
   a pipe, IronPython) and for C# (Roslyn scripting at run time vs a separate compile step, AOT limits, a non-AOT side process), with
   speed of a call, data passing (lists of shapes and attributes), package installs, sandboxing and security, crash isolation, debugging,
   licence, install size. Recommend one design for each language, with reasons and a measured or cited cost.
2. **Editor.** What the code editor needs (highlighting, completion of inputs, outputs and Studio's API, errors in place, a console, run
   on change or on demand) and which editor component to use in Avalonia (AvaloniaEdit and others), with licences.
3. **A language that is text and blocks at once.** Study structured and projectional editors and block languages: JetBrains MPS, Scratch
   and Blockly, Snap!, Hazel, Lamdu, Unison, Enso (Luna), Dark, Jupyter / Observable cells, Excel LAMBDA and LET, Houdini VEX with
   parameters, Grasshopper's Elefront and Anemone, Rhino's "node in code" ideas, Notion-like blocks. How could a Studio language let the
   user type code quickly while `for`, `while`, `if` and functions show as containers with UI (a count field, a stop condition, a
   preview of each pass), switchable between text and blocks, and round-tripping to Flow nodes? Propose its grammar sketch, how text maps
   to blocks and to Flow containers, and the editor interactions.
4. Mockups (PNG): the script node with its editor; the text-and-blocks editor showing the same loop as text and as a container with UI;
   dark and light in a calm slate style with an amber accent.
5. A ranked build plan (S/M/L), first step useful alone, risks, and ten things not to copy.

Deliverable: branch `report/C21`, folder `reports/C21/` (report .md, mockups .html and .png, sources). Plain English, no em dashes.
