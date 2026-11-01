# C19 R2: flow editors and modern app chrome

Agent R2. Read 2026-10-31. Tools: n8n, Make.com, Node-RED, React Flow (xyflow + React Flow UI), Rete.js v2, Retool Workflows, Linear, Raycast, Figma UI3, Figma/FigJam widgets.

How numbers were collected:
- **quoted**: read from open source files (pinned npm versions on cdn.jsdelivr.net, or `master`/`main` on raw.githubusercontent.com) or from official docs. File and line are given where useful.
- **measured**: rendered with Playwright (Chromium) on 2026-10-31 and read with `getComputedStyle` or the page DOM. Pages: React Flow overview example, Rete.js basic example, linear.app (root CSS variables), Figma plugin docs token table (Light and Dark tabs).
- n8n has no public editor demo, so n8n numbers come from its source, not from measurement.
- Make.com pages are behind a Cloudflare bot check from this machine (HTTP 403 "Just a moment...", 2026-10-31), and Retool needs a login. For both, only documented behaviour is reported; sizes are "not verified".

Notes for Studio (Avalonia 12, custom drawn, Tabler outline icons): CSS `px` here are device-independent pixels at 100% zoom, the same unit as Avalonia DIPs. `oklch(...)`, `hsl(...)` and alpha hex values are given as written; convert once into the theme table. Tabler outline icons are drawn on a 24 x 24 viewBox with `stroke-width="2"`, round caps and joins ([Tabler 3.50.0 circle.svg](https://cdn.jsdelivr.net/npm/@tabler/icons@3.50.0/icons/outline/circle.svg)), so at 16 px the stroke renders at 1.33 px.

---

### n8n (canvas on Vue Flow; `master` branch editor-ui read 2026-10-31, @n8n/design-system 2.44.7 published 2026-10-30)

**Looks modern because:**
- Calm neutral surfaces, colour saved for icons and state. Light canvas is `neutral-125` = `hsl(0, 0%, 96%)`, dark canvas is `neutral-950` = `oklch(20.46% 0 89.88)`, dark nodes are `neutral-850` = `hsl(0, 0%, 17%)` ([_tokens.scss L78-92, L765-777](https://cdn.jsdelivr.net/npm/@n8n/design-system@2.44.7/dist/css/_tokens.scss), [_primitives.scss L56-61, L214-216](https://cdn.jsdelivr.net/npm/@n8n/design-system@2.44.7/dist/css/_primitives.scss)).
- Shape tells the role. Default node is a 96 x 96 rounded square (6 grid cells of 16), trigger nodes get a 36 px left radius (a "D" shape), AI configuration nodes are 80 px circles, configurable nodes are 256 x 96 ([nodeViewUtils.ts L36-44](https://raw.githubusercontent.com/n8n-io/n8n/master/packages/frontend/editor-ui/src/app/utils/nodeViewUtils.ts), [CanvasNodeDefault.vue L272-296](https://raw.githubusercontent.com/n8n-io/n8n/master/packages/frontend/editor-ui/src/features/workflows/canvas/components/elements/nodes/render-types/CanvasNodeDefault.vue)).
- State lives on the outline, not the fill: 1.5 px hairline at rest, 2 px green, amber or red for success, warning, error, 2 px purple when pinned, a 6 px soft outer ring when selected, and a 1 px strike-through line across a disabled node ([_canvasNodeStyles.scss](https://raw.githubusercontent.com/n8n-io/n8n/master/packages/frontend/editor-ui/src/features/workflows/canvas/components/elements/nodes/render-types/_canvasNodeStyles.scss), [CanvasNodeDisabledStrikeThrough.vue](https://raw.githubusercontent.com/n8n-io/n8n/master/packages/frontend/editor-ui/src/features/workflows/canvas/components/elements/nodes/render-types/parts/CanvasNodeDisabledStrikeThrough.vue)).
- Zoom-aware contrast. Edge lightness, handle border lightness and node border opacity are interpolated between zoom 1.0 and zoom 0.2 with a gamma 2.2 curve, so wires and outlines get stronger as you zoom out instead of fading ([useZoomAdjustedValues.ts L16-80](https://raw.githubusercontent.com/n8n-io/n8n/master/packages/frontend/editor-ui/src/features/workflows/canvas/composables/useZoomAdjustedValues.ts)).
- Quiet wires: 2 px neutral grey bezier, square caps; wires that go backwards are routed as rounded steps (radius 16) 130 px below the source; non-main (AI) connections are dashed `5,6` ([CanvasEdge.vue L69, L212-213](https://raw.githubusercontent.com/n8n-io/n8n/master/packages/frontend/editor-ui/src/features/workflows/canvas/components/elements/edges/CanvasEdge.vue), [getEdgeRenderData.ts L6-8](https://raw.githubusercontent.com/n8n-io/n8n/master/packages/frontend/editor-ui/src/features/workflows/canvas/components/elements/edges/utils/getEdgeRenderData.ts)).
- One variable font (Geist) with fine weights 450, 500, 600 and a radius scale from 2 to 20 px ([_primitives.scss L235-277](https://cdn.jsdelivr.net/npm/@n8n/design-system@2.44.7/dist/css/_primitives.scss)).

**Looks dated / weak:**
- The title sits under the node (absolute, `top: 100%`, up to 2 lines, min width 2 x node width), so in dense graphs labels collide with wires and neighbours ([CanvasNodeDefault.vue L436-472](https://raw.githubusercontent.com/n8n-io/n8n/master/packages/frontend/editor-ui/src/features/workflows/canvas/components/elements/nodes/render-types/CanvasNodeDefault.vue)).
- "Running" is a rotating conic gradient in coral `rgba(255, 109, 90, 1)`, animated 1.5 s per turn on every running node ([_canvasNodeStyles.scss L58-80](https://raw.githubusercontent.com/n8n-io/n8n/master/packages/frontend/editor-ui/src/features/workflows/canvas/components/elements/nodes/render-types/_canvasNodeStyles.scss)).
- The big visual change was the 2024 canvas rewrite (beta in 1.70.0); later releases describe only small canvas refinements ([canvas beta thread, 2024-10-29](https://community.n8n.io/t/help-us-test-the-new-n8n-canvas-beta/60070), [release notes](https://docs.n8n.io/release-notes/)).

**Numbers:**

| property | value | source |
|---|---|---|
| grid | 16 px dots, node sizes are grid multiples | [nodeViewUtils.ts L36](https://raw.githubusercontent.com/n8n-io/n8n/master/packages/frontend/editor-ui/src/app/utils/nodeViewUtils.ts), [CanvasBackground.vue](https://raw.githubusercontent.com/n8n-io/n8n/master/packages/frontend/editor-ui/src/features/workflows/canvas/components/elements/background/CanvasBackground.vue), quoted |
| node size | 96 x 96; configurable 256 x 96; configuration circle 80 | nodeViewUtils.ts L38-44, quoted |
| node corner radius | 16 px (`--radius--lg`); trigger left side 36 px | CanvasNodeDefault.vue L272-296, quoted |
| node border | 1.5 px; black at 0.1 alpha (light), white at 0.2 alpha (dark) at zoom 1, rising to 0.7 at zoom 0.2 | [_canvasNodeStyles.scss L4-22](https://raw.githubusercontent.com/n8n-io/n8n/master/packages/frontend/editor-ui/src/features/workflows/canvas/components/elements/nodes/render-types/_canvasNodeStyles.scss), useZoomAdjustedValues.ts L79-80, quoted |
| state border | 2 px (`--spacing--5xs`): success green-600, warning gold-600, error red-600 (red-400 dark), pinned purple | _canvasNodeStyles.scss L30-44, quoted |
| selected | outer ring `0 0 0 6px hsla(220, 47%, 30%, 0.1)` light; white 40% alpha dark | _canvasNodeStyles.scss L24-27, [_tokens.scss L82, L768](https://cdn.jsdelivr.net/npm/@n8n/design-system@2.44.7/dist/css/_tokens.scss), quoted |
| running | conic gradient ring, inset -3 px, 1.5 s per turn (waiting 4.5 s) | _canvasNodeStyles.scss L58-80, quoted |
| handle (port) | 16 x 16 hit area; dot is a circle; non-main ports are a diamond (45 deg, scale 0.8); hover scale 1.5 | [_canvasHandleStyles.scss](https://raw.githubusercontent.com/n8n-io/n8n/master/packages/frontend/editor-ui/src/features/workflows/canvas/components/elements/handles/_canvasHandleStyles.scss), [CanvasHandleDot.vue](https://raw.githubusercontent.com/n8n-io/n8n/master/packages/frontend/editor-ui/src/features/workflows/canvas/components/elements/handles/render-types/parts/CanvasHandleDot.vue), [CanvasHandleDiamond.vue](https://raw.githubusercontent.com/n8n-io/n8n/master/packages/frontend/editor-ui/src/features/workflows/canvas/components/elements/handles/render-types/parts/CanvasHandleDiamond.vue), quoted |
| wire | 2 px, square cap, `oklch(0.84 0 0)` light / `oklch(0.42 0 0)` dark at zoom 1; `0.6` / `0.66` at zoom 0.2 | CanvasEdge.vue L212-213, useZoomAdjustedValues.ts L42-47, quoted |
| backward wire | smooth step, radius 16, 130 px below, 40 px side offset | getEdgeRenderData.ts L6-8, quoted |
| title / subtitle / port label | 16 px weight 500, 2-line clamp / 13 px weight 450 / 12 px | CanvasNodeDefault.vue L451-472, [CanvasHandleMainOutput.vue L141](https://raw.githubusercontent.com/n8n-io/n8n/master/packages/frontend/editor-ui/src/features/workflows/canvas/components/elements/handles/render-types/CanvasHandleMainOutput.vue), quoted |
| canvas colours | light `hsl(0,0%,96%)` + dots `oklch(68.3% 0 0)`; dark `oklch(20.46% 0 0)` + dots `oklch(38.67% 0 0)` | _tokens.scss L78-79, L765-766, quoted |
| minimap | 200 x 120, bottom left, node radius 16 | [Canvas.vue L2197-2207](https://raw.githubusercontent.com/n8n-io/n8n/master/packages/frontend/editor-ui/src/features/workflows/canvas/components/Canvas.vue), quoted |
| zoom range | 0 to 4 | Canvas.vue L2076-2077, quoted |

**Steal for Flow:**
- Port the zoom-to-contrast curve: between zoom 1.0 and 0.2, raise wire contrast and node outline alpha (0.1 to 0.7) with gamma 2.2. In Avalonia this is only a brush/pen recalculation per zoom change, no extra geometry.
- Keep state on the outline (2 px coloured border) and selection on a separate outer ring (6 px), so error + selected can show together.
- Disabled = a 1 px strike-through line plus muted outline. It reads at any zoom and costs one line.

---

### Make.com scenario builder (help center pages read 2026-10-31; dark mode 2026-07-30; toolbar redesign 2026-10-07)

**Looks modern because:**
- Run results are drawn on the canvas: after **Run once**, "the numbers shown in the bubbles indicate how many operations were used", and the bubbles open the input and output bundles ([Step 5. Test your scenario](https://help.make.com/step-5-test-your-scenario.md)).
- Logic sits on the wire: "To add a filter between two modules, click on the connecting line between them" ([Filtering](https://help.make.com/filtering.md)); a router is inserted by right-clicking "the bridge between two modules" ([Router](https://help.make.com/router.md)).
- Notes attach to a module or a route and show as markers with a hover preview ([Scenario notes](https://help.make.com/scenario-notes.md)).
- A dark mode built as its own colour system, where "Text, labels, modules, and other UI elements meet ... WCAG AA contrast standards" ([Dark mode in Make is here, 2026-07-30](https://help.make.com/dark-mode-in-make-is-here.md)).
- A compact, collapsible toolbar: Run once and Save side by side; scheduling and the Active toggle top right, and "the toggle is green when the scenario is active" ([Improved scenario toolbar, 2026-10-07](https://help.make.com/improved-scenario-toolbar-and-version-control.md), [Editor revamp, 2025-03-13](https://help.make.com/editor-revamp-and-subscenarios-launch.md), [Make Academy: scenario UI](https://academy-content.make.com/courses/make-foundation-scenarios/01-scenario-ui)).
- Canvas input auto-detects mouse, trackpad or touch ([Canvas interaction model](https://help.make.com/canvas-interaction-model.md), [Unified canvas navigation](https://help.make.com/unified-canvas-navigation.md)).

**Looks dated / weak:**
- Right-click drag is the default pan, and left drag is marquee select ([Canvas interaction model](https://help.make.com/canvas-interaction-model.md)). That fights CAD habits.
- The filter help page still shows a 2021 screenshot (file name `screen-shot-2021-12-10`), about 5 years old ([Filtering](https://help.make.com/filtering.md)).

**Numbers:**

| property | value | source |
|---|---|---|
| module shape, diameter, app icon colours, connector dash pattern | not verified (official pages blocked by Cloudflare from this machine; help text gives no sizes) | [make.com template page](https://www.make.com/en/templates/2952-controlled-distribution-of-data-flow), blocked 403 |
| notes per module or route | 200, each up to 10,000 characters | [Scenario notes](https://help.make.com/scenario-notes.md), quoted |
| active toggle | green when active | [Improved scenario toolbar](https://help.make.com/improved-scenario-toolbar-and-version-control.md), quoted |
| contrast target (dark mode) | WCAG AA for text, labels, modules | [Dark mode in Make is here](https://help.make.com/dark-mode-in-make-is-here.md), quoted |

**Steal for Flow:**
- Click a count badge to open that port's data (Flow already has count badges and hover peek; make the badge the entry point).
- Put filters and conditions on the wire as a small midpoint glyph, so the graph shows where data is dropped.
- Notes pinned to a node or wire as a small marker, preview on hover.

---

### Node-RED (5.0.9, published 2026-10-21; 4.x is now maintenance, 4.1.17; source on `master`)

**Looks modern because:**
- 5.0 ships a built-in dark theme that follows the OS ([Version 5.0 released, 2026-06-09](https://nodered.org/blog/2026/06/09/version-5-0-released)), with near-black layers: canvas `#0e0e12`, primary `#15151a`, secondary `#1b1b23` ([style.min.css 5.0.9, `html.nr-theme-dark`](https://cdn.jsdelivr.net/npm/@node-red/editor-client@5.0.9/public/red/style.min.css)).
- In 5.0, "selected nodes now show as a blue halo around the node, rather than just changing the node's border" ([5.0 blog](https://nodered.org/blog/2026/06/09/version-5-0-released)). The halo is a rect 3 px outside the node with radius 8 and stroke 2 ([view.js L5762-5765](https://raw.githubusercontent.com/node-red/node-red/master/packages/node_modules/@node-red/editor-client/src/js/ui/view.js), [flow.scss L366-372](https://raw.githubusercontent.com/node-red/node-red/master/packages/node_modules/@node-red/editor-client/src/sass/flow.scss)).
- A strict grid and small fixed nodes (100 x 30 on a 20 px grid) keep big flows tidy ([view.js L37-38, L70](https://raw.githubusercontent.com/node-red/node-red/master/packages/node_modules/@node-red/editor-client/src/js/ui/view.js)).
- Simple LOD: zoom bands at 0.75 and 0.5 add CSS classes, and highlight strokes thicken to 4 px at zoom 0.5 or less ([view.js L7764-7776](https://raw.githubusercontent.com/node-red/node-red/master/packages/node_modules/@node-red/editor-client/src/js/ui/view.js), [flow.scss L373-380](https://raw.githubusercontent.com/node-red/node-red/master/packages/node_modules/@node-red/editor-client/src/sass/flow.scss)).
- Disabled is drawn, not just greyed: node outline dashed `8,3` with fill opacity 0.5, wires dashed `10,8` at 2 px ([flow.scss L465-476](https://raw.githubusercontent.com/node-red/node-red/master/packages/node_modules/@node-red/editor-client/src/sass/flow.scss)).

**Looks dated / weak:**
- Each node is filled with its category colour and keeps dark label text even in dark theme (`--red-ui-node-label-color: #191919`), so the dark canvas fills with pastel bricks ([view.js L5704-5706](https://raw.githubusercontent.com/node-red/node-red/master/packages/node_modules/@node-red/editor-client/src/js/ui/view.js), [style.min.css dark block](https://cdn.jsdelivr.net/npm/@node-red/editor-client@5.0.9/public/red/style.min.css)).
- Icon in a 30 px shaded slot behind a 1 px divider, FontAwesome glyphs, `'Helvetica Neue', Arial` at 14 px ([view.js L5745, L5754](https://raw.githubusercontent.com/node-red/node-red/master/packages/node_modules/@node-red/editor-client/src/js/ui/view.js), [colors.scss L17-18](https://raw.githubusercontent.com/node-red/node-red/master/packages/node_modules/@node-red/editor-client/src/sass/colors.scss), [flow.scss L212-222](https://raw.githubusercontent.com/node-red/node-red/master/packages/node_modules/@node-red/editor-client/src/sass/flow.scss)).
- Dark theme selection is red `#e84a4a`, which can be confused with errors ([style.min.css dark block](https://cdn.jsdelivr.net/npm/@node-red/editor-client@5.0.9/public/red/style.min.css)).

**Numbers:**

| property | value | source |
|---|---|---|
| node | 100 x 30, corner rx 5, border 1 px `#999` light / `#888888` dark | view.js L37-38, L5704; [colors.scss L214](https://raw.githubusercontent.com/node-red/node-red/master/packages/node_modules/@node-red/editor-client/src/sass/colors.scss), quoted |
| icon slot / label start | divider at x = 30; label at x = 38 | view.js L5745, L5754, quoted |
| port | 10 x 10 square, rx 3, fill `#d9d9d9` light / `#b8b8b8` dark | view.js L5962, colors.scss L219, quoted |
| grid | 20 px lines, 1 px, `#eee` light / `#282828` dark | view.js L70, [workspace.scss L76-81](https://raw.githubusercontent.com/node-red/node-red/master/packages/node_modules/@node-red/editor-client/src/sass/workspace.scss), quoted |
| wire | bezier, curve scale 0.75, 3 px, `#999` light / `#888888` dark; selected `#0090ff` | view.js L35, L1531-1556; flow.scss L525-530, L572-574, quoted |
| selection halo | offset 3 px, rx 8, stroke 2 (4 at zoom <= 0.5), `#0090ff` light / `#e84a4a` dark | view.js L5762-5765, flow.scss L366-380, quoted |
| disabled | node dash `8,3`, fill opacity 0.5; wire dash `10,8`, 2 px, `#ccc` | flow.scss L465-476, colors.scss L252, quoted |
| status dot colours | red `#dc3e42`, green `#30a46c`, yellow `#F9DF31`, blue `#53A3F3`, grey `#d3d3d3` | colors.scss L238-244, quoted |
| type | 14 px node label, 9 pt status label, 12 px port tooltip | flow.scss L43, L502, L608, quoted |
| group | corner 4, stroke 2 `#999` | view.js L6541, flow.scss L178-185, quoted |

**Steal for Flow:**
- Outer selection halo (3 px outside, radius = node radius + 3, 2 px, 4 px at zoom 0.5 or less), never a border change.
- Dashed outline for disabled or bypassed nodes and dashed wires leaving them. It reads in grayscale and is only a dash array on the pen.
- Two zoom bands (0.75 and 0.5) as the LOD switch points.

---

### React Flow / xyflow (@xyflow/react 12.12.0, published 2026-09-24; @xyflow/system 0.0.83; React Flow UI components; read and measured 2026-10-31)

**Looks modern because:**
- Every default is a CSS variable (`--xy-*`) with a light set and a `.dark` set, and `colorMode` takes "dark", "light" or "system" ([style.css L3-97](https://cdn.jsdelivr.net/npm/@xyflow/react@12.12.0/dist/style.css), [Theming](https://reactflow.dev/learn/customization/theming)).
- The official examples restyle the defaults: 8 px radius, 1 px `#ededed` border, a three-layer soft shadow, white handles with a `#aaa` ring, canvas `#f7f9fb` (measured on the [Overview example](https://reactflow.dev/examples/overview), CSS in [261-MDCXNnzL.css](https://example-apps.xyflow.com/assets/261-MDCXNnzL.css)).
- React Flow UI `BaseNode` is a card: `rounded-md border`, header `px-3 py-2` with a semibold title, content `p-3` with `gap-y-2`, footer with `border-t`; selected adds a muted border and `shadow-lg` ([Base Node](https://reactflow.dev/ui/components/base-node), [registry source](https://ui.reactflow.dev/base-node)).
- UI kit handles are 11 px circles with a 1 px border, and `LabeledHandle` puts the label next to the handle with `px-3` ([base-handle](https://ui.reactflow.dev/base-handle), [labeled-handle](https://ui.reactflow.dev/labeled-handle), [Labeled Handle page](https://reactflow.dev/ui/components/labeled-handle)).
- Status as a 2 px border around a 9 px radius box, or a spinning border while loading ([node-status-indicator](https://ui.reactflow.dev/node-status-indicator), [page](https://reactflow.dev/ui/components/node-status-indicator)).
- LOD pattern: "the current zoom level can be used by a node to decide which content to show" ([Contextual zoom](https://reactflow.dev/examples/interaction/contextual-zoom)).

**Looks dated / weak:**
- The raw default node is a wireframe: 3 px radius, 1 px `#1a192b` border, 150 px wide, centred 12 px text, 6 px dark handles, 1 px `#b1b1b7` wires ([style.css L6-36, L245-255, L454-466](https://cdn.jsdelivr.net/npm/@xyflow/react@12.12.0/dist/style.css)).
- Dark defaults are low contrast: wires `#3e3e3e` on `#141414` ([style.css L54, L71](https://cdn.jsdelivr.net/npm/@xyflow/react@12.12.0/dist/style.css)).

**Numbers:**

| property | value | source |
|---|---|---|
| default node | width 150, padding 10, radius 3, font 12 px, border 1 px `#1a192b` (dark `#3c3c3c`), fill `#fff` (dark `#1e1e1e`) | style.css L29-34, L76-77, L454-466, quoted |
| hover / selected shadow | `0 1px 4px 1px rgba(0,0,0,0.08)` / `0 0 0 0.5px #1a192b` | style.css L32-33, quoted |
| handle | 6 x 6 (min 5), radius 100%, 1 px border, fill `#1a192b` (dark `#bebebe`) | style.css L36-37, L82-83, L245-255, quoted |
| wire | 1 px `#b1b1b7`, selected `#555`; dark `#3e3e3e`, selected `#727272`; animated dash 5 at 0.5 s | style.css L6-8, L54-56, L162-165, quoted |
| bezier curvature | 0.25 | [@xyflow/system index.mjs L1018](https://cdn.jsdelivr.net/npm/@xyflow/system@0.0.83/dist/esm/index.mjs), quoted |
| smooth step | corner radius 5, offset 20 | @xyflow/system index.mjs L1411, quoted |
| background | gap 20, dot size 1, cross size 6; dots `#91919a` light / `#555` dark; dark canvas `#141414` | [index.mjs L4455-4465](https://cdn.jsdelivr.net/npm/@xyflow/react@12.12.0/dist/esm/index.mjs), style.css L24, L71-72, quoted |
| selection box | fill `rgba(0,89,220,0.08)`, border 1 px dotted `rgba(0,89,220,0.8)` | style.css L39-40, quoted |
| minimap | 200 x 150, node radius 5, mask `rgba(240,240,240,0.6)` | index.mjs L4707-4708, L4754; style.css L15-21, quoted |
| controls | 26 x 26 buttons, padding 4, icon max 12 | style.css L415-443, quoted |
| zoom range | 0.5 to 2 | index.mjs L3767, quoted |
| example theme node | radius 8 px, border 1 px `rgb(237,237,237)`, shadow `0 3.54px 4.55px rgba(0,0,0,0.02), 0 3.54px 4.55px rgba(0,0,0,0.05), 0 0.51px 1.01px rgba(0,0,0,0.1)` | [Overview example](https://reactflow.dev/examples/overview), measured |
| UI kit handle | 11 x 11, 1 px border | [base-handle](https://ui.reactflow.dev/base-handle), quoted |

**Steal for Flow:**
- One token table with a light column and a dark column as the single source (maps 1:1 to Avalonia `ResourceDictionary.ThemeDictionaries`).
- Card anatomy from `BaseNode`: header padding 8 x 12, body padding 12, 8 px gaps, footer divider (Tailwind default scale, 4 px per step).
- Optional orthogonal wire mode using the smooth-step parameters (corner radius, offset 20); default bezier with curvature about 0.25.

---

### Rete.js v2 (rete-react-plugin 2.1.2 classic preset, published 2026-07-10; rete 2.0.6; measured 2026-10-31)

**Looks modern because:**
- Little by default. Its strength is that the preset is meant to be replaced: "extend the current component and use `styled-components`", or "implement your own component similar to Node.tsx" ([React renderer guide](https://retejs.org/docs/guides/renderers/react)).
- Port rows have a fixed rhythm: socket 24 px, margin 6 px, label line height 24 px, sockets pulled half outside the node edge ([Node.tsx](https://raw.githubusercontent.com/retejs/react-plugin/main/src/presets/classic/components/Node.tsx), [vars.ts](https://raw.githubusercontent.com/retejs/react-plugin/main/src/presets/classic/vars.ts)).
- The minimap preset is a rounded 8 px panel with a translucent fill ([Minimap.tsx](https://raw.githubusercontent.com/retejs/react-plugin/main/src/presets/minimap/components/Minimap.tsx)).

**Looks dated / weak:**
- Translucent periwinkle fill `rgba(110,136,255,0.8)` with a 2 px `#4e58bf` border, and selection floods the whole node yellow `#ffd92c` ([vars.ts](https://raw.githubusercontent.com/retejs/react-plugin/main/src/presets/classic/vars.ts), [Node.tsx](https://raw.githubusercontent.com/retejs/react-plugin/main/src/presets/classic/components/Node.tsx)).
- Oversized parts and default fonts: 24 px sockets in `#96b38a` with a white ring (4 px on hover), 5 px `steelblue` wires, 18 px white title, Arial ([Socket.tsx](https://raw.githubusercontent.com/retejs/react-plugin/main/src/presets/classic/components/Socket.tsx), [Connection.tsx](https://raw.githubusercontent.com/retejs/react-plugin/main/src/presets/classic/components/Connection.tsx)); measured node 180 x 122, radius 10 px ([Basic example](https://retejs.org/examples/basic/react)).

**Numbers:**

| property | value | source |
|---|---|---|
| node | width 180, radius 10, border 2 px `#4e58bf`, fill `rgba(110,136,255,0.8)`, padding-bottom 6 | Node.tsx, vars.ts, quoted; [Basic example](https://retejs.org/examples/basic/react) measured 180 x 122 |
| selected | fill `#ffd92c`, border `#e3c000` | Node.tsx, vars.ts, quoted |
| title | 18 px white, padding 8 (measured height 37) | Node.tsx quoted; Basic example measured |
| port label | 14 px, margin 6, line height 24 | Node.tsx, quoted |
| socket | 24 x 24 circle, `#96b38a`, 1 px white border, 4 px on hover | Socket.tsx quoted; measured 24 x 24, radius 12 |
| wire | 5 px `steelblue` (measured `rgb(70,130,180)`) | Connection.tsx quoted; measured |
| minimap | fill `rgba(229,234,239,0.65)`, border 1 px `#b1b7ff`, radius 8; viewport `rgba(255,251,128,0.32)` | Minimap.tsx, [MiniViewport.tsx](https://raw.githubusercontent.com/retejs/react-plugin/main/src/presets/minimap/components/MiniViewport.tsx), quoted |

**Steal for Flow:**
- Only the port row rhythm: fixed row height per port with the socket centred on the node edge.
- Use it as the "before" picture of what dates a node: translucent saturated fill, flood-fill selection, thick wires, big sockets.

---

### Retool Workflows (docs read 2026-10-31; editor needs login, numbers not verified)

**Looks modern because:**
- Blocks are code cards linked by a control-flow line from `startTrigger`; "Blocks that have two connected inputs are executed after both inputs complete execution" ([Blocks concept](https://docs.retool.com/workflows/concepts/blocks)).
- Layout tools on the canvas: Autolayout, Expand all, Collapse all, Toggle comments, Fit view, a minimap at the lower right, and a Graph / Tree (vertical) switch at top centre ([Workflow IDE](https://docs.retool.com/workflows/concepts/ide)).
- Error routing is explicit: "Drag the red On Error connector" once a block's Finally is set to Continue ([Error handlers](https://docs.retool.com/workflows/guides/error-handlers)).
- Unconnected blocks "display a warning"; blocks run singly from their toolbar or "with previous blocks" ([Assemble workflow blocks](https://docs.retool.com/workflows/guides/blocks)).
- A status bar holds environment, run history and per-block status ([Workflow IDE](https://docs.retool.com/workflows/concepts/ide), [Blocks concept](https://docs.retool.com/workflows/concepts/blocks)).

**Looks dated / weak:**
- No dark mode for the editor: the "Developer Dark Mode" request opened 2021-10-21 and was still active 2026-03-12 ([community thread](https://community.retool.com/t/developer-dark-mode/6935)). A user wrote "The light background is too much to stare at all day" (2025, third party, [Soothing Workflow Editor](https://community.retool.com/t/soothing-workflow-editor/59148)).
- The canvas appears to be stock React Flow with a grey dotted background: that user's CSS targets `.react-flow__edge-path` and `.react-flow__background` ([same post](https://community.retool.com/t/soothing-workflow-editor/59148); third party, inference).

**Numbers:**

| property | value | source |
|---|---|---|
| block size, header, port size, wire width, colours | not verified (login required; docs give no sizes) | [Workflow IDE](https://docs.retool.com/workflows/concepts/ide) |
| error connector colour | "red" (no hex published) | [Error handlers](https://docs.retool.com/workflows/guides/error-handlers), quoted |
| minimap position | lower right | [Workflow IDE](https://docs.retool.com/workflows/concepts/ide), quoted |

**Steal for Flow:**
- Per-node expand/collapse plus "collapse all" for big flows; a left-to-right vs top-to-bottom switch for tidy layout.
- An error output that only appears when error handling is turned on, drawn in the error colour.

---

### Linear (UI posts 2024-03-28 and 2026-03-12; website tokens measured 2026-10-31)

**Looks modern because:**
- A theme comes from three inputs (base colour, accent colour, contrast) in LCH, replacing "98 specific variables for each theme"; background, panel, dialog and modal surfaces are derived from them ([How we redesigned the Linear UI, part II, 2024-03-28](https://linear.app/now/how-we-redesigned-the-linear-ui)).
- A contrast input that can produce very high-contrast themes for accessibility ([same post](https://linear.app/now/how-we-redesigned-the-linear-ui)).
- 2026 refresh: the sidebar is "a few notches dimmer" than the content, greys moved from "a cool, blue-ish hue" to a warmer, less saturated grey, fewer separators with softer contrast, redrawn and smaller icons, compact rounded tabs ([A calmer interface for a product in motion, 2026-03-12](https://linear.app/now/behind-the-latest-design-refresh), [UI refresh changelog](https://linear.app/changelog/2026-03-12-ui-refresh)).
- Dense type with fine weights: sizes 11, 12, 13, 15, 18 px and weights 400, 510, 590 (measured on [linear.app](https://linear.app/), root CSS variables).
- Dark layers in tiny steps: `#08090a`, `#0f1011`, `#141516`, `#191a1b`, with borders `#23252a` and four text levels (measured on [linear.app](https://linear.app/)).

**Looks dated / weak:**
- Linear publishes no in-app sizes. All numbers here come from the marketing site and may differ from the app (measured, [linear.app](https://linear.app/)).
- The dark level steps are very small (for example `#0f1011` to `#141516`); on uncalibrated monitors they may merge (our judgement from the measured values).

**Numbers:**

| property | value | source |
|---|---|---|
| dark background levels 0 to 3 | `#08090a`, `#0f1011`, `#141516`, `#191a1b` | [linear.app](https://linear.app/), measured |
| dark panel / secondary / tertiary bg | `#0f1011` / `#1c1c1f` / `#232326` | linear.app, measured |
| dark border primary / secondary / tertiary | `#23252a` / `#34343a` / `#3e3e44` | linear.app, measured |
| dark text primary to quaternary | `#f7f8f8`, `#d0d6e0`, `#8a8f98`, `#62666d` | linear.app, measured |
| light bg levels 0 to 3 | `#fff`, `#f8f8f8`, `#f4f4f4`, `#f0f0f0` | linear.app, measured |
| light text primary to quaternary | `#282a30`, `#3c4149`, `#6f6e77`, `#86848d` | linear.app, measured |
| font sizes | micro 11, mini 12, small 13, regular 15, large 18 px | linear.app, measured |
| weights | 400 / 510 / 590 / 680 | linear.app, measured |
| radius scale | 4, 6, 8, 12, 16, 24, 32 px | linear.app, measured |
| accent / status | indigo `#5e6ad2`, red `#eb5757`, green `#27a644`, orange `#fc7840`, yellow `#f0bf00` | linear.app, measured |
| theme inputs | 3 (base, accent, contrast), replacing 98 variables | [part II post](https://linear.app/now/how-we-redesigned-the-linear-ui), quoted |

**Steal for Flow:**
- Generate Studio's whole theme from base grey + accent `#E9AB4C` + contrast, in an LCH/OKLCH space, deriving canvas, panel, node and raised levels.
- Make side panels slightly dimmer than the canvas content, use fewer dividers, and keep icons small.

---

### Raycast (2.0, 2026-05-14; Windows public beta 2025-11-20; docs read 2026-10-31)

**Looks modern because:**
- A full theme is 12 colours: background, backgroundSecondary, text, selection, loader, plus red, orange, yellow, green, blue, purple, magenta ([ray-so theme.ts](https://raw.githubusercontent.com/raycast/ray-so/main/app/%28navigation%29/themes/lib/theme.ts)).
- Colour safety: a raw colour "will be adjusted to achieve high contrast with the Raycast user interface" unless `adjustContrast` is false ([Colors](https://developers.raycast.com/api-reference/user-interface/colors.md)).
- One outline icon set with the same stroke width and corner radius rules and a heavier stroke ([A fresh look and feel, 2022-07-19, about 4 years old](https://www.raycast.com/blog/a-fresh-look-and-feel)), shipped as 16 px light and dark SVG variants (file names like `icon-anchor-16@dark.svg` in [Icons & Images](https://developers.raycast.com/api-reference/user-interface/icons-and-images.md); size inferred from file names).
- A bottom action bar shows the current actions "along with their keyboard shortcut" ([A fresh look and feel](https://www.raycast.com/blog/a-fresh-look-and-feel)).
- Strict copy rules: Title Case actions, give all actions icons or none, ellipsis for submenus ([Prepare an extension for the Store](https://developers.raycast.com/basics/prepare-an-extension-for-store)).

**Looks dated / weak:**
- 2.0 leans on Liquid Glass on macOS and on "acrylic blur-behind effects" on Windows ([The New Raycast](https://raycast.com/blog/the-new-raycast), [Technical deep dive](https://raycast.com/blog/a-technical-deep-dive-into-the-new-raycast)). That is outside Studio's no-blur rule.
- No published row heights, window size or colour hex values; the Colors page shows swatches only as images ([Colors](https://developers.raycast.com/api-reference/user-interface/colors.md)).

**Numbers:**

| property | value | source |
|---|---|---|
| theme size | 12 colours | [ray-so theme.ts](https://raw.githubusercontent.com/raycast/ray-so/main/app/%28navigation%29/themes/lib/theme.ts), quoted |
| built-in icon size | 16 px, separate light and dark SVGs | [Icons & Images](https://developers.raycast.com/api-reference/user-interface/icons-and-images.md), quoted file names (size inferred) |
| store screenshot (window aspect) | 2000 x 1250, 16:10 | [Store guide](https://developers.raycast.com/basics/prepare-an-extension-for-store), quoted |
| row height, window size, palette hex | not verified | not published |

**Steal for Flow:**
- Command palette with a bottom action bar that lists actions and their shortcuts.
- Auto-adjust user-picked group and sticky-note colours for contrast against the current theme.
- One icon stroke weight everywhere. Tabler at 16 px gives a 1.33 px stroke; pick one size (16 or 20) for all canvas glyphs.

---

### Figma UI3 (redesign shipped to all users October 2024; token table read 2026-10-31)

**Looks modern because:**
- Semantic tokens named `--figma-color-{type}-{color role}-{prominence}-{interaction}`, with types bg, text, icon and border, and roles like brand, selected, danger, warning, success ([CSS Variables and Theming](https://developers.figma.com/docs/plugins/css-variables/)).
- Text hierarchy by alpha in dark: text `#ffffff`, secondary `#ffffffb2` (70%), tertiary `#ffffff66` (40%) on `#2c2c2c` (same page, Dark tab, measured with Playwright).
- Canvas first: "Toolbars will float at the bottom of all Figma products"; panels are "fixed, but still resizable"; Minimize UI collapses side panels ([Our approach to designing UI3, 2024-10-01](https://www.figma.com/blog/our-approach-to-designing-ui3/), [Figma 2024 recap, 2024-12-04](https://www.figma.com/blog/figma-2024-we-shipped-it-you-shaped-it/)).
- Property panel: labels are nouns and tooltips give direction, "visible labels match aria-labels", Auto Layout controls "always show pixel values", about 200 hand-drawn icons ([Our approach to designing UI3](https://www.figma.com/blog/our-approach-to-designing-ui3/)).

**Looks dated / weak:**
- Floating side panels were the beta's signature change and were reversed: "The nail in the coffin was learning that they slowed people down" ([Figma 2024 recap](https://www.figma.com/blog/figma-2024-we-shipped-it-you-shaped-it/)).
- Large menu radius drew complaints: a forum user reports a 14 px menu radius versus 8 px on Windows (third party, not verified; [forum post, 2025-05-01](https://forum.figma.com/share-your-feedback-26/ui3-figma-s-menu-corner-radius-is-too-big-14px-40094)).
- Figma publishes no UI3 type sizes, panel widths or radii (not verified).

**Numbers:**

| property | value | source |
|---|---|---|
| dark bg / secondary / tertiary / hover | `#2c2c2c` / `#383838` / `#444444` / `#383838` | [CSS Variables](https://developers.figma.com/docs/plugins/css-variables/), measured (Dark tab) |
| dark text / secondary / tertiary | `#ffffff` / `#ffffffb2` / `#ffffff66` | same, measured |
| dark border / strong | `#444444` / `#ffffffe5` | same, measured |
| dark brand / selected bg | `#0c8ce9` / `#4a5878` | same, measured |
| dark danger / warning / success | `#e03e1a` / `#f3c11b` / `#198f51` | same, measured |
| light bg / secondary / tertiary | `#ffffff` / `#f5f5f5` / `#e6e6e6` | same, measured (Light tab) |
| light text / secondary / tertiary | `#000000e5` / `#00000080` / `#0000004d` | same, measured |
| light brand / danger / warning / success | `#0d99ff` / `#f24822` / `#ffcd29` / `#14ae5c` | same, measured |
| component (purple) | `#9747ff` light / `#8a38f5` dark | same, measured |
| menu corner radius | 14 px (user claim) | [forum post](https://forum.figma.com/share-your-feedback-26/ui3-figma-s-menu-corner-radius-is-too-big-14px-40094), quoted, third party |

**Steal for Flow:**
- The token naming scheme and alpha-based text levels (100 / 70 / 40%) on a mid-dark panel grey.
- Docked, resizable side panels plus a "minimise UI" toggle; a small floating tool strip at the bottom of the canvas only.

---

### Figma / FigJam widgets (Widget API docs read 2026-10-31; @figma/widget-typings 1.13.0, 2026-08-06; official widget-samples repo)

**Looks modern because:**
- Cards are plain auto-layout frames. `AutoLayout` takes direction, spacing, padding, alignment, cornerRadius, fill and stroke, and every default is zero or empty, so each widget states its look explicitly ([AutoLayout](https://developers.figma.com/docs/widgets/api/component-AutoLayout/)).
- Strokes sit inside by default (`strokeAlign "inside"`, `strokeWidth 1`), so a border never grows the card ([AutoLayout defaults](https://developers.figma.com/docs/widgets/api/component-AutoLayout/)).
- The official counter sample is a white card: cornerRadius 8, padding 16 left and 8 elsewhere, spacing 12, an inner `#E6E6E6` value chip with radius 8 and padding 24 x 12, and a zero-offset shadow (black 20%, blur 2, spread 2) ([WidgetCounter code.tsx](https://raw.githubusercontent.com/figma/widget-samples/main/WidgetCounter/widget-src/code.tsx)).
- Text defaults: Inter, 16, weight 400, `#000000`, line height auto ([Text](https://developers.figma.com/docs/widgets/api/component-Text/)).
- Performance advice that matches Studio's limits: "Blurs and shadows", non-normal blend modes and complex SVG are "particularly expensive for FigJam to render" ([Best Practices](https://developers.figma.com/docs/widgets/best-practices/)).
- Interaction advice: keep actions on the canvas, "Avoid making the entire widget clickable", "40x40 icons look best in the property menu", icons with tooltips ([Best Practices](https://developers.figma.com/docs/widgets/best-practices/)).

**Looks dated / weak:**
- "FigJam only supports a light theme", and widgets must hard-code fill, stroke and opacity ([Figma and FigJam Widgets](https://developers.figma.com/docs/widgets/figma-figjam-widgets/)).
- The samples are old (README images uploaded to GitHub in 2021 and 2022) and the counter uses a placeholder-looking stroke `#123456` ([widget-samples README](https://raw.githubusercontent.com/figma/widget-samples/main/README.md), [counter](https://raw.githubusercontent.com/figma/widget-samples/main/WidgetCounter/widget-src/code.tsx)).

**Numbers:**

| property | value | source |
|---|---|---|
| AutoLayout defaults | cornerRadius 0, padding 0, spacing 0, strokeWidth 1, strokeAlign inside, fill [], overflow hidden, direction horizontal, size hug-contents | [AutoLayout](https://developers.figma.com/docs/widgets/api/component-AutoLayout/), quoted |
| Text defaults | fontFamily Inter, fontSize 16, fontWeight 400, fill `#000000`, lineHeight auto, letterSpacing 0 | [Text](https://developers.figma.com/docs/widgets/api/component-Text/), quoted |
| doc shadow example | `#00000040`, offset 4,4, blur 4 | [Effect](https://developers.figma.com/docs/widgets/api/type-Effect/), quoted |
| sample card | radius 8; padding L16 R8 T8 B8; spacing 12; fill `#FFFFFF`; shadow black 0.2, offset 0,0, blur 2, spread 2 | [WidgetCounter](https://raw.githubusercontent.com/figma/widget-samples/main/WidgetCounter/widget-src/code.tsx), quoted |
| sample value chip | fill `#E6E6E6`, radius 8, padding 24 x 12, text 32 | same, quoted |
| sample add button | 32 x 32 circle, stroke black at 10%, glyph black at 80% | same, quoted |
| notepad sample | padding 8, text 12 px, width 100 | [WidgetNotepad](https://raw.githubusercontent.com/figma/widget-samples/main/WidgetNotepad/widget-src/code.tsx), quoted |
| property menu icon | 40 x 40 | [Best Practices](https://developers.figma.com/docs/widgets/best-practices/), quoted |

**Steal for Flow:**
- Card recipe for nodes, groups and sticky notes: radius 8, padding 8 to 16, spacing 8 to 12, 1 px inside stroke, explicit fill per theme.
- Treat shadows as optional and cheap (zero offset, blur 2, spread 2, 20% black) or drop them and rely on the outline; never blur.
- Leave a non-clickable margin on each node so selecting it does not trigger inline controls (sliders, toggles).
