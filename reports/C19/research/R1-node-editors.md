# R1: node editor look, seven tools

Agent R1. Read 2026-10-31. All pixel values are at 1x UI scale unless noted. "Computed" means a published constant multiplied out (for example Blender's 0.2 x 20 px widget unit); the constant itself is quoted at the link. Source-code links point at the exact branch or commit read. Studio context: canvas drawn in Avalonia 12, Tabler outline icons, IBM Plex Sans, accent #E9AB4C, so the "Steal" bullets favour things that are plain rects, rounded rects, lines, dashes and small icons.

---

### ComfyUI frontend (v1.60.0, commit 834cce9 of 2026-10-31; "Nodes 2.0" Vue node renderer plus classic LiteGraph canvas)

**Looks modern because:**
- Nodes 2.0 moves node drawing from the LiteGraph canvas to Vue/DOM components ([Comfy blog, 2025-12-05](https://blog.comfy.org/p/comfyui-node-2-0); [docs](https://docs.comfy.org/interface/nodes-2)). The setting is labelled "Modern Node Design (Nodes 2.0)" and is on by default for new Cloud and Desktop installs from 1.41.0 ([coreSettings.ts L1206-L1217](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/platform/settings/constants/coreSettings.ts#L1206-L1217)).
- One token set drives everything: a 10-step charcoal neutral ramp plus semantic tokens (background, card, node, node-header, primary, destructive, warning) ([_palette.css](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/packages/design-system/src/css/_palette.css#L1-L98); [theme.css L81-L107](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/packages/design-system/src/css/theme.css#L81-L107)). The node itself is two flat greys (header #202121, body #262729) with no category colour by default ([dark.json L66-L83](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/assets/palettes/dark.json#L66-L83)).
- States are drawn as rings and strips around the node, not by repainting it: 3 px selection border outside the node, blue outline while executing, 4 px error ring, an 8 px progress bar, a 60% plum overlay for bypass ([LGraphNode.vue L15-L93, L486, L541-L547](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/renderer/extensions/vueNodes/components/LGraphNode.vue#L15-L93)).
- Level of detail is tied to readable text, not a fixed zoom: classic mode switches to low quality when 14 px node text would fall under a minimum of 8 px on screen ([LGraphCanvas.ts L783-L801, L887](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/lib/litegraph/src/LGraphCanvas.ts#L783-L801); [setting L1026-L1040](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/platform/settings/constants/coreSettings.ts#L1026-L1040)). Low quality draws plain rects with no shadow or text ([LGraphCanvas.ts L5775-L5782](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/lib/litegraph/src/LGraphCanvas.ts#L5775-L5782)).
- Canvas chrome is a small bottom-right toolbar (select/hand mode, fit, zoom popover, minimap, link visibility) and a floating selection toolbox; the minimap paints node status colours ([canvas controls docs](https://docs.comfy.org/interface/canvas-controls); [minimapCanvasRenderer.ts L16-L46](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/renderer/extensions/minimap/minimapCanvasRenderer.ts#L16-L46)).

**Looks dated / weak:**
- Reader comments on the launch post call Nodes 2.0 "baby-toy-like" and "less compact and space efficient" (third party, comments under [the blog post](https://blog.comfy.org/p/comfyui-node-2-0)). The 12 px radius and 225 px minimum width explain it ([LGraphNode.vue L514](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/renderer/extensions/vueNodes/components/LGraphNode.vue#L510-L516); [graphRenderTransform.ts L10](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/renderer/core/layout/transform/graphRenderTransform.ts#L10)).
- The default dark palette still uses a 100 x 100 px base64 PNG as the canvas grid, and classic bypass colour is pure #FF00FF ([dark.json L24-L35](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/assets/palettes/dark.json#L24-L35)).
- Docs admit "minor visual issues" at extreme zoom or in very large workflows ([docs](https://docs.comfy.org/interface/nodes-2)).

**Numbers:**

| property | value | source |
|---|---|---|
| Vue node corner radius | `rounded-xl` = 0.75rem = 12 px | [LGraphNode.vue L514](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/renderer/extensions/vueNodes/components/LGraphNode.vue#L510-L516) + [Tailwind 4.3.2 theme.css](https://unpkg.com/tailwindcss@4.3.2/theme.css), quoted |
| Vue node min width | 225 px | [graphRenderTransform.ts L10](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/renderer/core/layout/transform/graphRenderTransform.ts#L10), quoted |
| Header padding / title size | `p-1` 4 px / `text-xs` 12 px (line 16 px) | [NodeHeader.vue L7](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/renderer/extensions/vueNodes/components/NodeHeader.vue#L7), quoted |
| Port row height | `h-5` = 20 px | [InputSlot.vue L13](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/renderer/extensions/vueNodes/components/InputSlot.vue#L13), quoted |
| Slot dot | 8 px circle, 1 px border white at 10%, hover scale 1.25, hit area 24 px; list slot = square with 1 px radius | [SlotConnectionDot.vue L44-L62](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/renderer/extensions/vueNodes/components/SlotConnectionDot.vue#L44-L62), quoted |
| Multi-type slot | up to 3 colour slices | [slotColors.ts L1](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/constants/slotColors.ts#L1-L7), quoted |
| Body padding / row gap | top 4 px, bottom 12 px / 4 px | [LGraphNode.vue L161](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/renderer/extensions/vueNodes/components/LGraphNode.vue#L159-L164), quoted |
| Node shadow | `drop-shadow-lg` = 0 9px 7px rgb(0 0 0 / 0.4) | [theme.css L64, L107](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/packages/design-system/src/css/theme.css#L54-L107), quoted |
| Selection outline | 3 px, white, 3 px outside node, radius 15 px | [LGraphNode.vue L66-L77, L534](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/renderer/extensions/vueNodes/components/LGraphNode.vue#L66-L77), quoted |
| Error ring | 4 px, #b33a3a (missing input: #fd9903) | [LGraphNode.vue L87-L89](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/renderer/extensions/vueNodes/components/LGraphNode.vue#L80-L93), [dark.json L77-L82](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/assets/palettes/dark.json#L66-L83), quoted |
| Running | outline #0b8ce9; progress bar 8 px | [LGraphNode.vue L21, L486](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/renderer/extensions/vueNodes/components/LGraphNode.vue#L486), quoted |
| Bypass / muted | overlay #6a246a at 60%, node opacity x0.5 | [LGraphNode.vue L386-L396, L541-L547](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/renderer/extensions/vueNodes/components/LGraphNode.vue#L386-L396), quoted |
| Dark layers | canvas #141414, app bg #171718, header #202121, node #262729, muted #3c3d42, border #494a50, node text #a0a0a0 | [dark.json](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/assets/palettes/dark.json#L25-L83), quoted |
| Light theme | canvas "lightgray", node #F5F5F5, link #4CAF50 | [light.json L26-L44](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/assets/palettes/light.json#L26-L44), quoted |
| Font | Inter (variable 100 to 900) | [_palette.css L3](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/packages/design-system/src/css/_palette.css#L3), quoted |
| Wire | spline default, width 3 px, midpoint marker circle, colour by slot type (fallback #9A9) | [LGraphCanvas.ts L1394-L1400](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/lib/litegraph/src/LGraphCanvas.ts#L1383-L1400), [coreSettings.ts L709-L773](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/platform/settings/constants/coreSettings.ts#L709-L773), quoted |
| Classic node | title 30 px, slot row 20 px, radius 8 px, text 14 px, shadow 2/2/3 px rgba(0,0,0,0.5), grid 10 | [LiteGraphGlobal.ts L83-L135](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/lib/litegraph/src/LiteGraphGlobal.ts#L83-L135), quoted |
| LOD threshold | min font 8 px; zoom = 8 / (14 x sqrt(dpr)), about 0.57 at dpr 1 (computed) | [LGraphCanvas.ts L793-L801](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/lib/litegraph/src/LGraphCanvas.ts#L783-L801), quoted |
| Group | title 30 px, title font 20 px, fill at 25% alpha, 1 px stroke | [LGraphGroup.ts L336-L353](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/lib/litegraph/src/LGraphGroup.ts#L336-L353), quoted |
| Minimap | 253 x 200 px, 1 px border, radius 8 px; nodes primary at 60%, groups 40%, error #FF0000, running #00FF00 | [useMinimapSettings.ts L26-L41](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/renderer/extensions/minimap/composables/useMinimapSettings.ts#L26-L41), [minimapCanvasRenderer.ts L30-L46](https://github.com/Comfy-Org/ComfyUI_frontend/blob/834cce976e330fedaa7f85f5aab930d7b8a205e8/src/renderer/extensions/minimap/minimapCanvasRenderer.ts#L16-L46), quoted |

**Steal for Flow:**
- Draw every state as a layer outside the node body (selection ring, error ring, progress strip, dim overlay) so the node fill and header never change colour. In Avalonia that is one extra rounded rect per state, easy to batch.
- Use a "readable text" LOD rule: switch to simplified nodes when the 12 to 13 px title would render under about 8 px on screen.
- Copy the minimap that paints status (error, running, bypassed) rather than only node boxes.

---

### Blender Geometry Nodes (5.2 LTS release branch; main is 5.4 alpha)

**Looks modern because:**
- 5.0 made nodes flatter: "Nodes look more flat with less of a drop-shadow", collapsed nodes became rectangular, and group nodes show a stack of cards instead of an icon ([5.0 UI release notes](https://developer.blender.org/docs/release_notes/5.0/user_interface/); stack code at [node_draw.cc L1717-L1732](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/source/blender/editors/space_node/node_draw.cc#L1717-L1732)).
- Header colours were muted hard between 4.5 and 5.x: Geometry went from #00D6A3 to #1D725E, Input from #FF3371 to #82354C, Converter from #12ADFF to #246283 ([4.5 theme](https://projects.blender.org/blender/blender/src/branch/blender-v4.5-release/release/datafiles/userdef/userdef_default_theme.c#L843-L909) vs [5.2 theme L652-L698](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/release/datafiles/userdef/userdef_default_theme.c#L652-L698)).
- Socket shape now means data structure, independent of type colour: Single = tall rectangle, Dynamic = circle, Field = diamond, Grid = four squares, List = three lines ([manual 5.2](https://docs.blender.org/manual/en/latest/interface/controls/nodes/parts.html); [Jacques Lucke, code blog 2025-08-08](https://code.blender.org/2025/08/new-socket-shapes/); [node_tree_update.cc L1005-L1025](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/source/blender/blenkernel/intern/node_tree_update.cc#L1005-L1025)).
- Wires carry meaning with stroke: field links are dashed and 0.7x thinner, invalid links turn red, links to selected nodes blend toward white, and links whose ends are both off screen fade down to 5% ([drawnode.cc L2285-L2302](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/source/blender/editors/space_node/drawnode.cc#L2273-L2302); [node_edit.cc L889-L910](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/source/blender/editors/space_node/node_edit.cc#L889-L910)).
- Zones (repeat, simulation, for-each, closure) are tinted backdrops at 20% alpha behind the nodes they enclose ([5.2 theme L690-L693](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/release/datafiles/userdef/userdef_default_theme.c#L652-L698)).
- Everything is derived from one unit (widget_unit = 20 px at 1x), so spacing is consistent ([wm_window.cc L778-L780](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/source/blender/windowmanager/intern/wm_window.cc#L778-L780); [node_intern.hh L333-L342](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/source/blender/editors/space_node/node_intern.hh#L333-L342)).

**Looks dated / weak:**
- Font is Inter at 11 pt with 20 px rows, which is dense for a desktop CAD audience ([UI_interface_c.hh L425-L428](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/source/blender/editors/include/UI_interface_c.hh#L425-L428); [fonts list](https://projects.blender.org/api/v1/repos/blender/blender/contents/release/datafiles/fonts?ref=blender-v5.2-release)).
- No minimap in the node editor (none is mentioned in the [5.0 node editor notes](https://developer.blender.org/docs/release_notes/5.0/user_interface/) or the [Node Parts page](https://docs.blender.org/manual/en/latest/interface/controls/nodes/parts.html)).

**Numbers:**

| property | value | source |
|---|---|---|
| Base unit | widget_unit = 18 x scale + 2 px = 20 px at 1x | [wm_window.cc L778-L780](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/source/blender/windowmanager/intern/wm_window.cc#L778-L780), quoted |
| Corner radius | 0.2 x unit = 4 px (computed) | [node_intern.hh L333](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/source/blender/editors/space_node/node_intern.hh#L333-L342), quoted |
| Header and row height | 1 unit = 20 px; panel header 10 px; item spacing 2 px | [node_intern.hh L334-L336](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/source/blender/editors/space_node/node_intern.hh#L333-L342), quoted |
| Horizontal margin | 1.2 x unit = 24 px | [node_intern.hh L339](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/source/blender/editors/space_node/node_intern.hh#L333-L342), quoted |
| Socket | radius 0.25 x unit = 5 px, so 10 px across; 1 px outline | [node_intern.hh L340](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/source/blender/editors/space_node/node_intern.hh#L333-L342), [node_draw.cc L1570](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/source/blender/editors/space_node/node_draw.cc#L1570), quoted |
| Node outline | 1 px, #FFFFFF at 0x26 (15%) | [theme L681](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/release/datafiles/userdef/userdef_default_theme.c#L652-L698), [node_draw.cc L3187-L3210](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/source/blender/editors/space_node/node_draw.cc#L3187-L3210), quoted |
| Selected / active outline | #ED5700 / #FFFFFF | [theme L663-L664](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/release/datafiles/userdef/userdef_default_theme.c#L652-L698), quoted |
| Shadow | width 0.4 x unit = 8 px, alpha 0.2, plus a black 0.4 alpha ring 0.5 px outside | [node_draw.cc L1694-L1715](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/source/blender/editors/space_node/node_draw.cc#L1694-L1715), quoted |
| Node backdrop / canvas / grid | #303030 / #1A1A1A / #303030 dots, 20 px step, 3 levels | [theme L653-L673](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/release/datafiles/userdef/userdef_default_theme.c#L652-L698), [field map](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/source/blender/makesrna/intern/rna_userdef.cc#L3577-L3690), [ED_node_c.hh L31-L32](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/source/blender/editors/include/ED_node_c.hh#L31-L32), quoted |
| Header colours 5.2 | Geometry #1D725E, Input #82354C, Converter #246283, Vector #3C3C83, Output #3E232A, Group #374725, Attribute #1D2546, Texture #79461D, Shader #2B652B, Color #6E6E23 | [theme L673-L689](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/release/datafiles/userdef/userdef_default_theme.c#L652-L698), quoted |
| Header alpha | 0.55 + backdrop alpha x 0.45; selected = 1.0 | [node_draw.cc L2778-L2805](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/source/blender/editors/space_node/node_draw.cc#L2778-L2815), quoted |
| Muted node | header blended 0.6 to canvas, body 0.8, both alpha -0.2, plus a pass-through wire drawn across | [node_draw.cc L2810-L2813, L3134, L3160-L3163](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/source/blender/editors/space_node/node_draw.cc#L3134-L3165), quoted |
| Wire | 2.5 px; field links x0.7, dash 10 px, dash factor 0.75, dash alpha 0.5 | [drawnode.cc L1959, L2296-L2302](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/source/blender/editors/space_node/drawnode.cc#L2285-L2302), quoted |
| Wire colours | outline #1A1A1A, inner #8D8D8D, selected mix #FFFFFF at 70% | [theme L662-L680](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/release/datafiles/userdef/userdef_default_theme.c#L652-L698), quoted |
| Noodle curving | 4 (range 0 to 10); moved to Preferences in main | [theme L670](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/release/datafiles/userdef/userdef_default_theme.c#L652-L698), [main rna L6237-L6241](https://projects.blender.org/blender/blender/src/branch/main/source/blender/makesrna/intern/rna_userdef.cc#L6237-L6241), quoted |
| Socket colours (float RGB as written) | Float 0.63 grey, Vector 0.39/0.39/0.78, Int 0.35/0.55/0.36, Bool 0.80/0.65/0.84, String 0.44/0.70/1.00, Geometry 0.00/0.84/0.64 | [drawnode.cc L987-L1013](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/source/blender/editors/space_node/drawnode.cc#L987-L1013), quoted |
| Zones | Simulation #664162, Repeat #76512F, For-each #33527F, Closure #7D7D3A, each at 0x33 alpha (20%) | [theme L690-L693](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/release/datafiles/userdef/userdef_default_theme.c#L652-L698), quoted |
| Frame | #0F0F0F at 0xcc (80%); margin 1.5 x unit = 30 px; label 20 | [theme L694](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/release/datafiles/userdef/userdef_default_theme.c#L652-L698), [node_draw.cc L3472](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/source/blender/editors/space_node/node_draw.cc#L3472), [node_common.cc L567](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/source/blender/nodes/intern/node_common.cc#L567), quoted |
| Group stack indicator | offset 3.6 px x, 2.4 px y per copy | [node_draw.cc L1731-L1732](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/source/blender/editors/space_node/node_draw.cc#L1717-L1732), quoted |
| LOD | sockets and stack hidden when view scale <= 0.2 | [node_draw.cc L1595-L1611](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/source/blender/editors/space_node/node_draw.cc#L1595-L1611), quoted |
| Header icon size | 0.8 x unit = 16 px | [node_draw.cc L2143](https://projects.blender.org/blender/blender/src/branch/blender-v5.2-release/source/blender/editors/space_node/node_draw.cc#L2143), quoted |

**Steal for Flow:**
- Encode structure with port shape and type with colour, exactly Flow's case: small bar or dot for one item, a "three lines" glyph for list, a doubled glyph for list of lists, a diamond or hollow shape for lazy. All are 10 px plain geometry.
- Muted, dark category headers (lightness near 25 to 35%) with a 1 px white-at-15% outline; reserve saturated colour for wires, ports and states.
- Stacked-card indicator (two offset copies, 3.6 x 2.4 px) for sub-flows; translucent 20% tinted backdrop for loop and for-each containers.

---

### Unreal Engine Blueprints and Material Editor (UE 5.8 docs)

**Looks modern because:**
- Pins show connection state by fill: "displayed as an outline when not wired ... and solid when wired", for both execution and data pins ([Nodes, UE 5.8](https://dev.epicgames.com/documentation/en-us/unreal-engine/nodes-in-unreal-engine)).
- Two wire families: white execution wires and data wires coloured by pin type; during play the execution wire highlight "fades away over time" ([Nodes](https://dev.epicgames.com/documentation/en-us/unreal-engine/nodes-in-unreal-engine)). The editor exposes this trace as attack, sustain and release phases with their own thickness and colour ([UGraphEditorSettings](https://dev.epicgames.com/documentation/unreal-engine/API/Editor/GraphEditor/UGraphEditorSettings)).
- Title colour is by node role, not by library category: separate settings for Event, Function call, Pure function call, Branch, Sequence, Function terminator, Parent call, Result, Preview and Comment ([UGraphEditorSettings](https://dev.epicgames.com/documentation/unreal-engine/API/Editor/GraphEditor/UGraphEditorSettings)).
- Comment box text scales with zoom, while per-node comment bubbles do not, and a "comment bubble when zoomed out" option exists ([Comments](https://dev.epicgames.com/documentation/en-us/unreal-engine/comments-in-unreal-engine); [settings](https://dev.epicgames.com/documentation/unreal-engine/API/Editor/GraphEditor/UGraphEditorSettings)).
- Material Editor: the node being previewed "turns blue", and the viewport preview is realtime by default ([Previewing materials](https://dev.epicgames.com/documentation/unreal-engine/previewing-and-applying-your-materials-in-unreal-engine)).

**Looks dated / weak:**
- 12 or more named pin colours (maroon, sherpa blue, sea green, moss green, yellow green, mauve, magenta, pink, gold, cornflower blue, orange, blue) carry type alone ([Blueprint Variables](https://dev.epicgames.com/documentation/en-us/unreal-engine/blueprint-variables-in-unreal-engine)). Hard to tell apart and to learn.
- Default hex values for pins and titles are not published in the docs (all colour fields show no default on [UGraphEditorSettings](https://dev.epicgames.com/documentation/unreal-engine/API/Editor/GraphEditor/UGraphEditorSettings)), and many doc images still come from UE4 (file names like `k2_pins_data.png` on [Nodes](https://dev.epicgames.com/documentation/en-us/unreal-engine/nodes-in-unreal-engine)).

**Numbers:**

| property | value | source |
|---|---|---|
| Padding above / below a pin | 4 / 4 | [UGraphEditorSettings, UE 5.8](https://dev.epicgames.com/documentation/unreal-engine/API/Editor/GraphEditor/UGraphEditorSettings), quoted ("defaults to 4") |
| Padding right of input / left of output | 10 / 10 | same page, quoted ("defaults to 10") |
| Padding towards node edge | 10 (can be negative so pins stick out) | same page, quoted |
| Auto-collate padding | 20 | same page, quoted |
| Pin colour names | Boolean maroon, Byte sherpa blue, Integer sea green, Integer64 moss green, Float yellow green, Name mauve, String magenta, Text pink, Vector gold, Rotator cornflower blue, Transform orange, Object blue | [Blueprint Variables](https://dev.epicgames.com/documentation/en-us/unreal-engine/blueprint-variables-in-unreal-engine), quoted |
| Pin fill rule | outline when unwired, solid when wired | [Nodes](https://dev.epicgames.com/documentation/en-us/unreal-engine/nodes-in-unreal-engine), quoted |
| Wire thickness defaults | not published (fields exist: data, execution, trace attack/sustain/release) | [UGraphEditorSettings](https://dev.epicgames.com/documentation/unreal-engine/API/Editor/GraphEditor/UGraphEditorSettings), not verified |

**Steal for Flow:**
- Hollow port when unconnected, filled when connected: free, readable, works at any size.
- A "run trace" on wires: bright for a moment after data flows, then decays to normal. Good for the running state without a spinner on every node.
- Colour the header strip by role (source, value, command, container, sub-flow) rather than one hue per CAD command category.

---

### Houdini network editor (Houdini 22.0 docs)

**Looks modern because:**
- Three wire styles: Straight (default, slight curve at connectors), Rounded (right-angle exits, wide circular turns, horizontal and vertical runs) and Metro (horizontal, vertical and diagonal with tight turns "similar to a modern subway map"); Shift+S cycles ([display options](https://www.sidefx.com/docs/houdini/network/options.html)).
- Clutter control is built in: "Fade Long Wires" fades the middle of very long wires, and the overview map appears only "when needed", in the bottom left ([options](https://www.sidefx.com/docs/houdini/network/options.html); [navigation](https://www.sidefx.com/docs/houdini/network/navigate.html)).
- Zoom-aware interaction: a node ring with flag buttons pops up on hover when zoomed out, because flags are "too tiny to click" ([nodes](https://www.sidefx.com/docs/houdini/network/nodes.html); [options](https://www.sidefx.com/docs/houdini/network/options.html)).
- Status lives in badges (error, warning, message, comment, time dependent, locked) that can be small (under the name), large (next to the node) or hidden, plus optional extra text such as a node's "descriptive parameter" ([options](https://www.sidefx.com/docs/houdini/network/options.html)).
- Houdini 22 ships a new UI skin; the theme is derived from three colours (Base, Accent, Highlight) in an OkLCH model, with a "secondary chroma" default of 0.2 for buttons ([H22 UI notes](https://www.sidefx.com/docs/houdini/news/22/viewport.html); [Theme Editor](https://www.sidefx.com/docs/houdini/ref/windows/theme_editor.html)).

**Looks dated / weak:**
- Custom node shapes (bone, bulge, tilted and more) make dense networks noisy; Houdini itself offers a "simplified rectangle shape" option to speed up very dense networks ([organize](https://www.sidefx.com/docs/houdini/network/organize.html)).
- Light themes are "currently experimental" ([Theme Editor](https://www.sidefx.com/docs/houdini/ref/windows/theme_editor.html)).

**Numbers:**

| property | value | source |
|---|---|---|
| Wire styles | Straight (default), Rounded, Metro | [options](https://www.sidefx.com/docs/houdini/network/options.html), quoted |
| Flag colours (SOP) | bypass yellow, lock red, template maroon plus ring, display blue plus ring, render purple | [flags](https://www.sidefx.com/docs/houdini/network/flags.html), quoted (names only, no hex) |
| Default node colour | "gray by default" | [flags](https://www.sidefx.com/docs/houdini/network/flags.html), quoted |
| Grid spacing unit | 1 unit = roughly one node width (X) / one node height (Y) | [options](https://www.sidefx.com/docs/houdini/network/options.html), quoted |
| Theme secondary chroma | 0.2 | [Theme Editor](https://www.sidefx.com/docs/houdini/ref/windows/theme_editor.html), quoted |
| Light theme threshold | background lightness >= 60 is experimental | [Theme Editor](https://www.sidefx.com/docs/houdini/ref/windows/theme_editor.html), quoted |
| Overview | bottom left, default "when needed" | [navigate](https://www.sidefx.com/docs/houdini/network/navigate.html), quoted |
| Pixel sizes for nodes, wires, fonts | not published | not verified |

**Steal for Flow:**
- Offer an orthogonal "Rounded" wire mode next to bezier; it suits a CAD audience and draws as lines plus quarter arcs.
- Fade the middle of long wires and show the minimap only when the flow does not fit the view.
- Generate the Flow palette from Studio's base grey, accent #E9AB4C and a highlight colour in OkLCH, like Houdini 22, so light and dark themes stay consistent.

---

### Grasshopper 2 (Rhino 9 BETA, beta thread 2026-07-30; developer guide updated 2026-10-06)

**Looks modern because:**
- Wire stroke encodes data structure: "Dashed lines carry no data whatsoever, single solid lines carry a single data item, double solid lines carry a collection of at least two items, and double dashed lines carry at least two separate collections" ([GH2 glossary: Wire](https://www.rhino3d.com/docs/grasshopper2/terms/wire.html)).
- Errors and warnings are "colour-coded along their top edges", a thin strip rather than a repaint ([Errors](https://www.rhino3d.com/docs/grasshopper2/terms/errors.html); [Warnings](https://www.rhino3d.com/docs/grasshopper2/terms/warnings.html)).
- Colour is semantic: icon authors pick a role (Input, Output, Analysis) and GH2 picks the colour per theme; vector icons "stay sharp at any size, and they follow the light and dark themes"; component drawing must take colours from a Skin, "Do not hard-code them" ([developer guide](https://developer.rhino3d.com/guides/grasshopper2/getting-started/)).
- Zoomable UI that "reveals more detail as you get closer", in-canvas widgets, light and dark modes ([beta announcement](https://discourse.mcneel.com/t/rhino-beta-feature-grasshopper-2-beta/221336)).
- Thirteen data modifiers live on the parameter; each active one puts "a small circular icon next to the parameter name", which removes whole helper components from the canvas ([Data Modifiers](https://www.rhino3d.com/docs/grasshopper2/topics/DataModifiers.html)).

**Looks dated / weak:**
- A beta user: "The sparkles when connecting wires ... completely unnecessary visual noise", "the circular fade effect when hovering over a menu tab is extremely distracting", and the interface "feels more like a kids' playground" (third party opinion, [post #10, 2026-08-04](https://discourse.mcneel.com/t/rhino-beta-feature-grasshopper-2-beta/221336/10)).
- Same post: components dragged in dark mode appear in light mode until dropped ([post #10](https://discourse.mcneel.com/t/rhino-beta-feature-grasshopper-2-beta/221336/10)).
- No pixel numbers are published; McNeel's own pages describe features, not visuals ([About GH2](https://www.rhino3d.com/stories/grasshopper-2/); [Rhino 9 new](https://www.rhino3d.com/9/new/)).

**Numbers:**

| property | value | source |
|---|---|---|
| Wire: no data | dashed single line | [Wire](https://www.rhino3d.com/docs/grasshopper2/terms/wire.html), quoted |
| Wire: one item | single solid line | same, quoted |
| Wire: list (2 or more items) | double solid line | same, quoted |
| Wire: tree (2 or more lists) | double dashed line | same, quoted |
| Error / warning marker | colour along top edge | [Errors](https://www.rhino3d.com/docs/grasshopper2/terms/errors.html), quoted |
| Modifiers per parameter | 13, shown as small circular icons | [Data Modifiers](https://www.rhino3d.com/docs/grasshopper2/topics/DataModifiers.html), quoted |
| Icon colour roles | Input, Output, Analysis (examples) | [developer guide](https://developer.rhino3d.com/guides/grasshopper2/getting-started/), quoted |
| Canvas home | lower right quadrant emphasised | [Canvas](https://www.rhino3d.com/docs/grasshopper2/terms/canvas.html), quoted |
| Corner radius, wire width, fonts | not published | not verified |

**Steal for Flow:**
- Take this wire grammar almost directly for Flow's one item / list / list of lists, and use a dash for lazy or empty outputs. It is just `StrokeDashArray` plus a second parallel stroke.
- Error and warning as a 2 to 3 px coloured strip on the node's top edge, plus a Tabler alert icon in the header.
- Define colours as roles (source, command, value, error) resolved by theme, never RGB in node code.

---

### TouchDesigner (Official build 2025.33230 of 2026-09-01; wiki pages dated 2021 to 2026)

**Looks modern because:**
- Nodes can show a live viewer inside the tile instead of a three-letter icon; the Viewer flag sits top left, Viewer Active bottom right ([Node Viewer, 2022](https://docs.derivative.ca/Node_Viewer); [operator anatomy lesson](https://learn.derivative.ca/courses/100-fundamentals/lessons/101-navigating-the-environment/topic/reading-operator-anatomy/)).
- Wires "display animated dashed lines" to show which nodes are cooking; links between families are grey dashed lines that can be hidden with "x" ([Wire, 2022](https://docs.derivative.ca/Wire); [network anatomy lesson](https://learn.derivative.ca/courses/100-fundamentals/lessons/101-navigating-the-environment/topic/reading-network-anatomy/)).
- Colour by family, with shade for role: "Generators (types with no inputs) are shown using a darker shade, and Filters are the lighter shade of the OP color" ([OP Create Dialog](https://docs.derivative.ca/OP_Create_Dialog); [Operator Family, 2026](https://docs.derivative.ca/Operator_Family)).
- Zoomable UI: zoom into a component to enter its network; preferences set min, max and preferred text sizes as you zoom ([Network Editor, 2023](https://docs.derivative.ca/Network_Editor); [Preferences](https://docs.derivative.ca/Preferences)).
- Annotate COMP gives comments, network boxes and annotates; "smaller boxes are in front of larger boxes" and they sit behind the grid by default ([Annotate COMP](https://docs.derivative.ca/Annotate_COMP)).

**Looks dated / weak:**
- Family colours are not documented as values anywhere in the wiki; the colours class page lists none ([Colors Class, 2022](https://docs.derivative.ca/Colors_Class); [Operator Family](https://docs.derivative.ca/Operator_Family)).
- Spline and straight are the only wire modes ([Wire](https://docs.derivative.ca/Wire)); the core Node page is from 2021 ([Node](https://docs.derivative.ca/Node)).

**Numbers:**

| property | value | source |
|---|---|---|
| Wire modes | spline curves or straight lines, toggle "s" | [Wire](https://docs.derivative.ca/Wire), quoted |
| Wire hover | highlights yellow | [Wire](https://docs.derivative.ca/Wire), quoted |
| Cooking indicator | animated dashed wire | [Wire](https://docs.derivative.ca/Wire), quoted |
| Link style | grey dashed (wiki) or dotted (lesson) | [Wire](https://docs.derivative.ca/Wire), [lesson](https://learn.derivative.ca/courses/100-fundamentals/lessons/101-navigating-the-environment/topic/reading-network-anatomy/), quoted |
| Grid snap | Off, Coarse or Fine; on by default | [Preferences](https://docs.derivative.ca/Preferences), [Network Editor](https://docs.derivative.ca/Network_Editor), quoted |
| Overview | toggled with "o" | [Network Editor](https://docs.derivative.ca/Network_Editor), quoted |
| Family colours as hex | not published | not verified |

**Steal for Flow:**
- Use darker vs lighter shade of the same role colour to split sources (no inputs) from commands (filters).
- Animated dash on wires that are currently computing, static otherwise; cheap with a dash offset.
- Layer groups by size (small in front of large) and draw group fills under the grid lines.

---

### Dynamo (Dynamo 4.4 dev, master commit 1a3eec9 of 2026-10-27; visual refresh in 2.13, zoom states in 2.14)

**Looks modern because:**
- The 2.13 "Visual Refresh" brought "A brand new node design, dark themed", node icons "anchoring the node header", and ports with a "vertical blue band" when satisfied and "vertical red band" when unsatisfied ([Dynamo 2.13 post, 2021-12-17](https://dynamobim.org/dynamo-core-2-13-release-part-1-3)). In code: a 6 x 29 px marker, blue #6AC0E7 / red #EB5555 / grey #999999 ([Ports.xaml L180-L187](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/UI/Themes/Modern/Ports.xaml#L180-L187); [InPortViewModel.cs L30-L32](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/ViewModels/Core/InPortViewModel.cs#L30-L32)).
- Zoom states (2.14): when zoomed out, only the most dominant state shows as a colour overlay and glyph: red error, yellow warning, blue info, then frozen and preview off ([Dynamo 2.14 post, 2022-04-25](https://dynamobim.org/?p=53338)). In code the overlay is 50% opacity, glyphs are 64 px, and the switch is at zoom 0.4 ([NodeView.xaml.cs L866-L878, L949-L956](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/Views/Core/NodeView.xaml.cs#L866-L878); [Configurations.cs L152](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCore/Configuration/Configurations.cs#L142-L152)).
- A 12 px status bar along the node bottom carries error / warning / info colour ([NodeView.xaml.cs L1031-L1038](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/Views/Core/NodeView.xaml.cs#L1031-L1038); [NodeViewModel.cs L1407-L1416](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/ViewModels/Core/NodeViewModel.cs#L1407-L1416)).
- Group colours have names: four default group styles Actions #B9F9E1, Inputs #FFB8D8, Outputs #FFC999, Review #A4E1FF ([GroupStyleItem.cs L18-L24](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCore/Configuration/GroupStyleItem.cs#L18-L24); [Resources.resx L848-L868](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCore/Properties/Resources.resx#L848-L868); [2.14 post](https://dynamobim.org/?p=53338)).
- The canvas tint tells you where you are: home workspace #F9F9F9, custom node (sub-graph) editing #FFFFDC ([DynamoColorsAndBrushes.xaml L71-L72](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/UI/Themes/Modern/DynamoColorsAndBrushes.xaml#L69-L76); [DynamoView.xaml L800-L813](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/Views/Core/DynamoView.xaml#L800-L813)).
- Built in C# with WPF and the node is assembled in code from Grid, Border and Rectangle, which maps one to one onto Avalonia controls or a custom draw ([NodeView.xaml.cs L255-L297](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/Views/Core/NodeView.xaml.cs#L255-L297)).

**Looks dated / weak:**
- Dark #3C3C3C nodes sit on a near-white #F9F9F9 canvas with #444 wires, a high-contrast mix that makes every node a dark hole ([DynamoColorsAndBrushes.xaml](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/UI/Themes/Modern/DynamoColorsAndBrushes.xaml#L10-L76); [DynamoConverters.xaml L34-L39](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/UI/Themes/Modern/DynamoConverters.xaml#L34-L39)).
- State glyphs are 64 px bitmaps (`frozen-64px.png`, `transient-64px.png`) rather than vector icons ([NodeView.xaml.cs L206-L215](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/Views/Core/NodeView.xaml.cs#L206-L215)).
- Big type: 16 px node titles and 36 px default group titles take space ([NodeView.xaml.cs L376-L387](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/Views/Core/NodeView.xaml.cs#L367-L387); [AnnotationModel.cs L284](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCore/Graph/Annotations/AnnotationModel.cs#L284)).

**Numbers:**

| property | value | source |
|---|---|---|
| Header height / top corner radius | 46 px / 8 px top corners only | [NodeView.xaml.cs L265-L297](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/Views/Core/NodeView.xaml.cs#L265-L297), quoted |
| Header icon | 34 x 34 px, header content margin 6 px | [NodeView.xaml.cs L356-L371](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/Views/Core/NodeView.xaml.cs#L356-L371), quoted |
| Title | Artifakt Element, 16 px, Medium, #DCDCDC | [NodeView.xaml.cs L376-L387](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/Views/Core/NodeView.xaml.cs#L367-L387), quoted |
| Header / body / canvas | #535353 / #3C3C3C / #F9F9F9 (custom node #FFFFDC); app frame #232323 | [DynamoColorsAndBrushes.xaml L16-L72](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/UI/Themes/Modern/DynamoColorsAndBrushes.xaml#L10-L76), quoted |
| Port row | port height 34 px; port pill 29 px tall, 11 px radius on the inner side, 1 px border #A1A1A1, fill #3C3C3C; label 12 px Medium | [Configurations.cs L142](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCore/Configuration/Configurations.cs#L142-L152), [Ports.xaml L148-L158, L319-L326](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/UI/Themes/Modern/Ports.xaml#L148-L158), [PortViewModel.cs L35-L37](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/ViewModels/Core/PortViewModel.cs#L35-L37), quoted |
| Input value marker | 6 x 29 px; #6AC0E7 connected or default, #EB5555 missing, #999999 none | [Ports.xaml L180-L187](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/UI/Themes/Modern/Ports.xaml#L180-L187), [InPortViewModel.cs L30-L32](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/ViewModels/Core/InPortViewModel.cs#L30-L32), quoted |
| Node border / selection | 1 px / 4 px #6AC0E7, 3 px outside, radius 10 px top | [NodeView.xaml.cs L751-L777](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/Views/Core/NodeView.xaml.cs#L751-L777), quoted |
| Drop-into-group hover | 6 px border #CCCCCC | [NodeView.xaml.cs L793-L805](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/Views/Core/NodeView.xaml.cs#L793-L805), quoted |
| Status colours | error #EB5555, warning #FAA21B, info #6AC0E7, frozen #BCD3EE, transient #D5BCF7, package #32BCAD | [NodeViewModel.cs L1407-L1416](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/ViewModels/Core/NodeViewModel.cs#L1407-L1416), quoted |
| Status bar | 12 px tall, bottom of node | [NodeView.xaml.cs L1031-L1038](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/Views/Core/NodeView.xaml.cs#L1031-L1038), quoted |
| Zoom-state LOD | below zoom 0.4: 50% state overlay plus 64 px glyph | [Configurations.cs L152](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCore/Configuration/Configurations.cs#L142-L152), [NodeView.xaml.cs L866-L956](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/Views/Core/NodeView.xaml.cs#L866-L878), quoted (a code comment says 60%, the constant says 0.4) |
| Wire | bezier, 3 px, grows when zoomed out: max(3, 3 x (1/zoom) x 2); end dots 11 px | [Configurations.cs L74-L79](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCore/Configuration/Configurations.cs#L74-L79), [Connectors.xaml L118-L131](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/UI/Themes/Modern/Connectors.xaml#L118-L131), quoted |
| Wire colours | normal #444, hover #808080, selected #6AC0E7, running preview #F2930C, transient #D5BCF7 | [DynamoConverters.xaml L34-L39](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/UI/Themes/Modern/DynamoConverters.xaml#L34-L39), quoted |
| Wire dash states | dash 2 while connecting; dash 2 plus 50% opacity when frozen; hidden wire ghosted at 40% when an end node is selected | [Connectors.xaml L43-L75](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/UI/Themes/Modern/Connectors.xaml#L43-L75), quoted |
| Grid | lines every 100 units, 5 minor divisions, major #7F7F7F, minor #C3C3C3, 1 px; major spacing kept between 50 and 250 px | [InfiniteGridView.xaml.cs L15-L34](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/Controls/InfiniteGridView.xaml.cs#L15-L34), quoted |
| Groups | top corners 10 px; default title 36 px; sizes 14 to 96; default fill #C1D676 | [AnnotationView.xaml.cs L108](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/Views/Core/AnnotationView.xaml.cs#L108), [AnnotationModel.cs L49, L284](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCore/Graph/Annotations/AnnotationModel.cs#L49), [PreferenceSettings.cs L1268-L1283](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCore/Configuration/PreferenceSettings.cs#L1268-L1283), quoted |
| Preview bubble | #3C3C3C, radius 2 px; compact view shows label and item count in Source Code Pro | [PreviewControl.xaml L76-L79](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/Views/Preview/PreviewControl.xaml#L76-L79), [PreviewCompactView.xaml L24-L39](https://github.com/DynamoDS/Dynamo/blob/1a3eec9d69211fbc038cab531a6dcce211cb70c5/src/DynamoCoreWpf/Views/Preview/PreviewCompactView.xaml#L24-L39), quoted |

**Steal for Flow:**
- Zoom states: below a threshold, replace node detail with one dominant state colour plus one large Tabler icon (error, warning, paused, disabled). This is the best LOD answer for "1,000 nodes, which ones are broken?".
- The thin input marker (satisfied / missing / default) at the port edge; Flow can use 3 px instead of 6 px.
- Named group colours (Inputs, Process, Outputs, Review) and a canvas tint when editing a sub-flow.
