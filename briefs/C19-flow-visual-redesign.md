# C19: make the Flow node editor look like a modern flow platform

Research and design only. No Studio code is shared and none is wanted back. Write one report plus mockup images.

## What Flow is

Urbanto Studio is a desktop CAD program for urban designers (Windows, C# on .NET 10, Avalonia 12, dark theme by default,
light theme too). **Flow** is its node editor, like Grasshopper or Blender Geometry Nodes: nodes such as Layer, Slider, Offset,
Divide, Count are wired together, and the result draws in the CAD drawing beside it. Flow sits in a docked panel under the
drawing or in its own window. The canvas is custom drawn (rectangles, text, bezier wires, no web view), so anything in your
spec must be drawable with plain 2D primitives: rounded rectangles, lines, curves, text, small SVG icons (Tabler outline set).

The owner's words: the Flow UI "still needs a lot of enhancement. The shape of it, the colour, it's not looking like a modern
UI program."

## The screenshots (all in `briefs/C19-images/`, taken from the real program on 2026-11-01)

| File | What it shows |
|---|---|
| `01-whole-window.png` | The whole window: menu, tool rail, Flow docked with its left panel (Flows, Library, Saved variants, Node palette), the canvas, Node properties, the right Properties panel |
| `02-error-node.png` | A node in error: red edge, `!` mark, message line under it |
| `03-zoomed-out-overlap.png` | Zoomed out: nodes overlap, wires and labels collide |
| `04-breakpoint-paused.png` | A run paused at a breakpoint, nodes marked "Ran" |
| `05-500-nodes.png` | Part of a 500 node flow at normal zoom: count badges sit on wires, labels crowded |
| `06-one-node.png` | One Number node alone, the plainest view of the node shape |
| `07-hover-thumbnail.png` | Hovering a node shows a small plan of its results |

## Current look, as tokens (dark theme)

- Background `#0F1828`, panel `#152238`, border `#253655`, strong border `#34496F`.
- Text `#E8EEF7`, muted text `#9DACC4`, accent (orange) `#E9AB4C`, danger `#EE7C7C`, success `#6FD98F`.
- Light theme: background `#F5F7FA`, panel `#FFFFFF`, text `#172B45`, accent `#955700`.
- UI font IBM Plex Sans; mono Cascadia Mono.
- Port colours today by data kind: shapes orange, numbers green, text/choices lilac.
- The accent orange is the program's brand colour: keep it as the accent, but you may change how much of it is used.

## Already decided (do not argue these, build on them)

From an earlier study (C5): nodes are a whole number of grid units wide with ports on grid rows; titles 13 px and port labels
11 px at 100 percent; below about 60 percent zoom port labels hide and titles keep a fixed screen size; below about 30 percent a
node is a coloured block with its state glyph; wires under opaque nodes; state shown by badges, not by header colours; inline
value editors on unwired inputs; count badges on outputs.

## What to do

1. **Study modern node platforms and flow tools** for their visual design, from their own docs, screenshots and design write-ups:
   ComfyUI (new frontend), Blender Geometry Nodes (4.x), Unreal Blueprints and Material editor, Houdini 20, Grasshopper 2,
   Dynamo, TouchDesigner, n8n, Make.com, Node-RED, React Flow / xyflow examples, Rete.js, Retool Workflows, Figma/FigJam
   widgets, Linear and Raycast (for the general "modern desktop UI" feel). For each: what makes it look modern (shape, colour,
   depth, density, typography, motion), with links.
2. **Critique each of the seven screenshots** specifically: what looks dated or wrong, in order of how much it hurts.
3. **Write a visual spec Studio can build from**, with exact numbers:
   - colour tokens for the canvas, node body, node header, selection, hover, wires by data kind, ports, badges, states (error,
     warning, running, stale, disabled, paused), groups/frames, minimap; dark AND light;
   - node anatomy: corner radius, header height, padding, port size and shape per data kind, row height, divider, shadow or
     elevation, icon in the header, how the category is shown (colour strip, icon, tint);
   - wires: width, curvature, colour, selected/hover/flowing state, how many wires before they fade;
   - typography scale for the canvas and the Flow side panels;
   - the Flow chrome: toolbar (Run, Stop, mode, zoom), left panel, node palette, properties, problem chip, minimap;
   - zoom levels (100, 60, 30 percent) drawn.
4. **Mockups**: draw the redesign as images the owner can look at: at least (a) the whole window like `01`, (b) a small flow of
   5 to 8 nodes including one error and one with an inline value, (c) the 500 node view at normal zoom and at 30 percent,
   (d) one node anatomy sheet with measurements, (e) the light theme of (b). Before/after pairs are best. Make them as HTML + CSS
   or SVG pages and render them to PNG (a headless browser is fine), and commit both.
5. **A ranked change list**: each change, its size (S/M/L), and what it fixes in which screenshot. Mark the 10 changes that
   give the biggest "looks modern" jump for the least work.

Ten things NOT to copy (with a reason each) from those platforms, briefly.

## Deliverable

- Branch `report/C19`, folder `reports/C19/`: `C19-flow-visual-redesign.md` (the report), `mockups/*.html|svg` and
  `mockups/*.png`, and `tokens.json` (every colour and size in the spec, dark and light).
- Plain English, short sentences, no em dashes. Cite sources with links.
