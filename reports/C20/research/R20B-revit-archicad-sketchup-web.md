# R20B notes: parametric objects and window designers (read 2026-11-01)

Scope: how parametric objects define and show their parameters, what end users see, how authors add or remove parameters and controllers, and what a drag-and-drop "window designer" for those parameters can learn from form builders. Pages behind 403 or login are listed at the end as "not verified" and are not used as evidence.

---

### Revit families, type vs instance parameters, Family Editor (Revit 2023 to 2026 help)
**How it works:**
- Everything in Revit is a family. System families are built in, loadable families live in external RFA files, and in-place families are one-off elements: "each in-place family contains only a single type" ([Revit 2023 help, Families](https://help.autodesk.com/cloudhelp/2023/ENU/Revit-GetStarted/files/GUID-7AEC5D66-C2E0-40E2-9504-3CC13781B87A.htm); [Revit 2016 help, kinds of families](https://help.autodesk.com/cloudhelp/2016/ENU/Revit-Model/files/GUID-403FFEAE-BFF6-464D-BAC2-85BF3DAB3BA2.htm), older page). Type catalogs let a project "load only the types that you need" (same 2016 page).
- Instances share a type: "Changes made to type properties affect all instances of the family created from that type", while instance changes "affect only that instance" ([Revit 2023 help](https://help.autodesk.com/cloudhelp/2023/ENU/Revit-GetStarted/files/GUID-7AEC5D66-C2E0-40E2-9504-3CC13781B87A.htm)).
- Authors add parameters in the Family Types dialog: Add, name, discipline, type, group, optional tooltip, then pick Instance or Type. Group decides "which group header the parameter displays under on the Properties palette". New parameters sort alphabetically, but Move Up / Move Down sets an order that "will be maintained in the Properties palette" ([Revit 2024 help, Create Family Parameters](https://help.autodesk.com/cloudhelp/2024/ENU/Revit-Customize/files/GUID-921F7A15-D191-4F75-8243-4989C482E253.htm)).
- Geometry is driven indirectly: draw reference planes, dimension them, label the dimension with a parameter, align and lock the geometry to the planes ([Revit 2024 help, Create Instance Parameters](https://help.autodesk.com/cloudhelp/2024/ENU/Revit-Customize/files/GUID-24CB6E69-9C0F-4222-B079-6D98B9B78627.htm)). Formulas go in the Formula column of the same dialog ([Revit 2014 help, Using Formulas](https://help.autodesk.com/cloudhelp/2014/ENU/Revit/files/GUID-EEC4A03D-1EE8-49C0-8390-91C0BF649AE4.htm), old page).
- On-canvas controllers: shape handles appear on reference planes that are dimensioned with an instance parameter, and "If you require shape handles in 3D views, use reference lines instead of reference planes" ([Revit 2024 help, Shape Handles](https://help.autodesk.com/cloudhelp/2024/ENU/Revit-Customize/files/GUID-C30A7EFC-3030-4E9D-A305-C66B50E1DF75.htm)). Flip controls come in four kinds: single arrows "rotate the family instance 180 degrees", double arrows mirror it ([Revit 2024 help, Flip Control](https://help.autodesk.com/cloudhelp/2024/ENU/Revit-Customize/files/GUID-4AF18AA1-E16F-46A6-81B9-3CA1E8094F46.htm)).
- Shared parameters are definitions kept in a separate file so many families and projects can use the same parameter. A parameter must be shared to appear in a tag or a multi-category schedule ([Revit 2023 help, Shared Parameters](https://help.autodesk.com/cloudhelp/2023/ENU/Revit-Model/files/GUID-E7D12B71-C50D-46D8-886B-8E0C2B285988.htm)).

**Good to use because:**
- The type vs instance split is clear and documented in one sentence each, which makes "edit one" vs "edit all of this kind" easy to teach ([Revit 2023 help](https://help.autodesk.com/cloudhelp/2023/ENU/Revit-GetStarted/files/GUID-7AEC5D66-C2E0-40E2-9504-3CC13781B87A.htm)).
- Authors can test ("flex") the family inside the editor by typing values and pressing Apply: "Flexing early and often as you create families ensures the stability of the families" ([Revit 2025 help, Flex the Family Framework](https://help.autodesk.com/cloudhelp/2025/ENU/Revit-Customize/files/GUID-18097131-E15B-4AAD-9414-505656EF8D7C.htm)).
- Authors control order and grouping, and each parameter can carry a tooltip ([Revit 2024 help](https://help.autodesk.com/cloudhelp/2024/ENU/Revit-Customize/files/GUID-921F7A15-D191-4F75-8243-4989C482E253.htm)).
- Handles and flip arrows bind straight to parameters, so end users edit in the drawing, not only in a palette ([shape handles](https://help.autodesk.com/cloudhelp/2024/ENU/Revit-Customize/files/GUID-C30A7EFC-3030-4E9D-A305-C66B50E1DF75.htm)).

**Bad to use because:**
- The indirection is heavy: plane, dimension, label, align, lock. A vendor tip (third party) says to "Constrain geometry to reference planes, not to edges of solids" to avoid "Can't make type" errors ([NOVEDGE, 2026](https://novedge.com/blogs/design-news/revit-tip-revit-reference-plane-best-practices)). Flexing exists because families break when values change ([Revit 2025 help](https://help.autodesk.com/cloudhelp/2025/ENU/Revit-Customize/files/GUID-18097131-E15B-4AAD-9414-505656EF8D7C.htm)).
- Shared parameters copy the definition only: data "is not automatically applied to another family or project using the same shared parameter" ([Revit 2023 help](https://help.autodesk.com/cloudhelp/2023/ENU/Revit-Model/files/GUID-E7D12B71-C50D-46D8-886B-8E0C2B285988.htm)). Users must manage a separate file just to tag a value.
- Shape handles show only in 2D unless the author rebuilds with reference lines ([Revit 2024 help](https://help.autodesk.com/cloudhelp/2024/ENU/Revit-Customize/files/GUID-C30A7EFC-3030-4E9D-A305-C66B50E1DF75.htm)).
- User complaints on the Revit Ideas board (formula editor too small, no suggestions) could not be opened (403). Not verified.

**Numbers:**
| property | value | source |
|---|---|---|
| Parameter tooltip length | up to 250 characters | [Revit 2024 help](https://help.autodesk.com/cloudhelp/2024/ENU/Revit-Customize/files/GUID-921F7A15-D191-4F75-8243-4989C482E253.htm) |
| Types per in-place family | 1 | [Revit 2023 help](https://help.autodesk.com/cloudhelp/2023/ENU/Revit-GetStarted/files/GUID-7AEC5D66-C2E0-40E2-9504-3CC13781B87A.htm) |
| Flip control kinds | 4 (single/double, vertical/horizontal) | [Revit 2024 help](https://help.autodesk.com/cloudhelp/2024/ENU/Revit-Customize/files/GUID-4AF18AA1-E16F-46A6-81B9-3CA1E8094F46.htm) |
| Default new parameter order | alphabetical, ascending | [Revit 2024 help](https://help.autodesk.com/cloudhelp/2024/ENU/Revit-Customize/files/GUID-921F7A15-D191-4F75-8243-4989C482E253.htm) |

**Take for Studio:**
- Keep the type vs instance split, but show it on every field (a small "shared by N objects" marker), so the user knows an edit fans out.
- Bind handles straight to parameters, without a hidden layer of planes and locks. Ship a built-in "flex" test that runs a few values and reports what broke.
- Let authors set order and tooltip per parameter, and default to author order, not alphabetical.

---

### Dynamo Player (Revit 2023+, Alias docs, Dynamo forum 2017 to 2026)
**How it works:**
- Player runs a graph "without requiring Dynamo experience"; some graphs just need Play, others ask for values or a model selection first. Opened from Manage tab ([Revit 2026 help, Dynamo Player](https://help.autodesk.com/cloudhelp/2026/ENU/Revit-HaveYouTried/files/GUID-E8205058-9CA4-4CFF-95F5-A6AA1CDA7346.htm)).
- Authors mark nodes "Is Input" and Watch nodes "Is Output". Inputs appear in Player, selection inputs switch to a pick mode with "Confirm selection", outputs show after Run ([Dynamo Primer, Player](https://primer2.dynamobim.org/dynamo-in-forma-beta/run-graphs-in-dynamo-player)).
- Input order comes from the graph: "Input nodes display in Dynamo Player in the order they appear in Dynamo starting from the top to bottom", groups organise them, and "Ungrouped nodes always appear at the top" ([Alias 2022 help, Customize scripts for Dynamo Player](https://help.autodesk.com/cloudhelp/2022/ENU/Alias-NURBS-Modeling/files/Generate-designs-with-Dynamo/Alias-Dynamo-Player/GUID-7C9864A5-5738-44F2-A455-F989863043F9.html); Alias host, not Revit).
- An Autodesk staff reply (2024) says Player has a display preference to sort inputs alphabetically; otherwise they come "in the order that they were inserted into the graph" ([Dynamo forum, 2024](https://forum.dynamobim.com/t/input-order-for-dynamo-player-2024-civil-3d/99923)).

**Good to use because:**
- Clear author/runner split: one person builds, many run, with no graph shown ([Revit 2026 help](https://help.autodesk.com/cloudhelp/2026/ENU/Revit-HaveYouTried/files/GUID-E8205058-9CA4-4CFF-95F5-A6AA1CDA7346.htm)).
- Selection inputs are first-class: pick in the model, confirm, return to the form ([Dynamo Primer](https://primer2.dynamobim.org/dynamo-in-forma-beta/run-graphs-in-dynamo-player)).

**Bad to use because:**
- Ordering has been a complaint for years. 2017: inputs "are listed in the order they are created" ([forum, 2017](https://forum.dynamobim.com/t/dynamo-player-input-order/13471)). 2020: a user copies, pastes and relinks nodes to reorder, and editing the file in Notepad++ "doesn't help" ([forum, 2020](https://forum.dynamobim.com/t/dynamo-player-order-of-inputs/49118)). 2024: a user prefixes names with "1 -", "2 -" to force order ([forum, 2024](https://forum.dynamobim.com/t/input-order-for-dynamo-player-2024-civil-3d/99923)). All third party user posts.
- No dynamic choice lists: "The only core node for custom inputs requires you to define the values in the node", so people install the Data-Shapes package for real dialogs ([forum, 2024](https://forum.dynamobim.com/t/selecting-excel-worksheet-to-use-in-dynamo-player/102362)).
- Inputs silently go missing across versions ([forum, 2023](https://forum.dynamobim.com/t/revit-2024-2-dynamo-2-19-inputs-not-showing-in-player/95556)), and new users cannot tell if a script needs inputs ([forum, 2023](https://forum.dynamobim.com/t/dynamo-player-in-revit-2023-show-necessity-of-input/88689)).

**Numbers:**
| property | value | source |
|---|---|---|
| Views on the 2017 "input order" thread | 4,085 (measured from forum JSON, 2026-11-01) | [forum](https://forum.dynamobim.com/t/dynamo-player-input-order/13471) |
| Years the order complaint recurs | threads from 2017, 2017, 2019, 2020, 2024 (measured from forum search API) | [forum search API](https://forum.dynamobim.com/search.json?q=dynamo%20player%20input%20order) |

**Take for Studio:**
- Order must be explicit and editable in the designer (drag in the form), never derived from node position or creation time.
- Choice lists must be able to take their options from data at run time.
- The Player should show up front "this tool needs N inputs" before Run.

---

### Archicad GDL objects: parameter list, parameter script, interface script (GDL Reference Guide, current online)
**How it works:**
- A GDL object has a parameter list plus scripts. The parameter script adds logic: VALUES limits values (lists, ranges, steps, CUSTOM), LOCK greys a field out but keeps it visible, HIDEPARAMETER removes it from the list, PARAMETERS writes a value back ([GDL Basics, Parameter logic](https://gdl.graphisoft.com/gdl-basics/parameter-logic/)).
- GLOB_MODPAR_NAME holds "the name of the parameter the user changed last", so two linked parameters can both be editable (edit tread count, height follows; edit height, count follows) ([GDL Basics, Parameter logic](https://gdl.graphisoft.com/gdl-basics/parameter-logic/)).
- The parameter script runs on dialog open, on any change, on hotspot edits, on stretch, on placement; Archicad stops accidental loops automatically ([same page](https://gdl.graphisoft.com/gdl-basics/parameter-logic/)).
- The interface script builds a custom settings page with UI_DIALOG, UI_PAGE (with parent ids for a page tree), UI_INFIELD (methods 1 to 9: list view, popup, icon radio, push buttons, checkbox and more), UI_PICT, UI_BUTTON, UI_GROUPBOX, UI_SEPARATOR, UI_TOOLTIP, UI_SLIDER. "Sizes and coordinate values are measured in pixels", origin top left ([GDL Reference, User Interface Script](https://gdl.graphisoft.com/reference-guide/the-user-interface-script)).
- Tabs: automatic hierarchical paging via UI_PAGE index, parent, title, icon plus a gs_ui_current_page parameter; or scripted paging with a popup and buttons ([GDL Basics, Graphical UI](https://gdl.graphisoft.com/gdl-basics/graphical-ui/)).

**Good to use because:**
- Rich controls: picture popups, icon radio rows, sliders, tooltips, page trees ([GDL Reference](https://gdl.graphisoft.com/reference-guide/the-user-interface-script)).
- Clear advice: "always hide or lock unnecessary/dormant parameters" ([GDL Basics](https://gdl.graphisoft.com/gdl-basics/graphical-ui/)).
- A Preview button checks the custom page for overlaps and items outside the page bounds ([GDL Basics](https://gdl.graphisoft.com/gdl-basics/graphical-ui/)).
- "Last changed parameter" logic gives two-way parameter links without a solver ([GDL Basics](https://gdl.graphisoft.com/gdl-basics/parameter-logic/)).

**Bad to use because:**
- The page is a fixed pixel canvas. The reference says 444 x 296 px and size_x, size_y "are not used" ([GDL Reference](https://gdl.graphisoft.com/reference-guide/the-user-interface-script)); the GDL Basics guide says 444 x 266 px ([GDL Basics](https://gdl.graphisoft.com/gdl-basics/graphical-ui/)). Even Graphisoft's two pages disagree.
- Every control is placed by hand with absolute x, y numbers in code ([GDL Reference](https://gdl.graphisoft.com/reference-guide/the-user-interface-script)). No layout engine.
- Scripted paging "does only support continuous page numbering"; automatic paging is not supported in Curtain Wall, Label or Zone objects; pictures stretch if the scripted size differs ([GDL Basics](https://gdl.graphisoft.com/gdl-basics/graphical-ui/)).
- A GDL specialist (third party, about 2011, old) says "GDL can be very overwhelming" ([Shoegnome, 2011](https://shoegnome.com/2011/08/28/adventures-in-gdl)). Newer complaints on community.graphisoft.com could not be opened (403). Not verified.

**Numbers:**
| property | value | source |
|---|---|---|
| Custom page size | 444 x 296 px (reference) | [GDL Reference](https://gdl.graphisoft.com/reference-guide/the-user-interface-script) |
| Custom page size | 444 x 266 px (basics guide) | [GDL Basics](https://gdl.graphisoft.com/gdl-basics/graphical-ui/) |
| UI_DIALOG per script | 1 | [GDL Reference](https://gdl.graphisoft.com/reference-guide/the-user-interface-script) |
| Default button size | 60 x 20 px | [GDL Reference](https://gdl.graphisoft.com/reference-guide/the-user-interface-script) |
| UI_INFIELD display methods | 9 | [GDL Reference](https://gdl.graphisoft.com/reference-guide/the-user-interface-script) |
| Model View Options page width | 600 px | [GDL Basics](https://gdl.graphisoft.com/gdl-basics/graphical-ui/) |

**Take for Studio:**
- Copy the control palette (picture choices, icon radios, sliders, groups, tooltips, page tree) and the LOCK vs HIDE distinction.
- Do not copy the fixed pixel canvas. Use a layout grid that grows, and generate the code-free definition from the designer.
- Copy "last changed parameter" as a value the object's flow can read, so two-way links are easy.

---

### Archicad hotspots (graphical editing handles bound to parameters)
**How it works:**
- HOTSPOT2 x, y, unID, paramReference, flags, displayParam, customDescription. If a script has at least one hotspot, Archicad stops making its own bounding box hotspots ([GDL Basics, Hotspots](https://gdl.graphisoft.com/gdl-basics/hotspots-graphical-editing)).
- A length handle needs three hotspots: base (flag 1), moving (2), hidden reference (3) that sets the positive direction. Angle handles use base 4, moving 5, centre 6, plus 7 for a 3D axis ([GDL Basics, Hotspots](https://gdl.graphisoft.com/gdl-basics/hotspots-graphical-editing)).
- Modifier flags: +128 hide, +256 editable base, +512 reverse angle, +1024 paper-space units. displayParam shows another value in the tracker during the drag ([same page](https://gdl.graphisoft.com/gdl-basics/hotspots-graphical-editing)).
- unIDs must be unique and stable, or associative dimensions stop following the right corner ([same page](https://gdl.graphisoft.com/gdl-basics/hotspots-graphical-editing)).

**Good to use because:**
- Handles edit real parameters and run the parameter script, so limits and links still apply during a drag ([GDL Basics, Parameter logic](https://gdl.graphisoft.com/gdl-basics/parameter-logic/)).
- The tracker can show a friendlier derived value than the raw parameter (displayParam) ([GDL Basics, Hotspots](https://gdl.graphisoft.com/gdl-basics/hotspots-graphical-editing)).

**Bad to use because:**
- Three or four coordinated calls per editable value, with numeric role flags; when parameters are combined the base and reference points must move too ([GDL Basics, Hotspots](https://gdl.graphisoft.com/gdl-basics/hotspots-graphical-editing)). Forum threads on broken hotspots were blocked (403), not verified.

**Numbers:**
| property | value | source |
|---|---|---|
| Hotspots per length parameter | 3 | [GDL Basics](https://gdl.graphisoft.com/gdl-basics/hotspots-graphical-editing) |
| Hotspots per angle parameter | 3 (2D), 4 (3D) | [GDL Basics](https://gdl.graphisoft.com/gdl-basics/hotspots-graphical-editing) |

**Take for Studio:**
- A handle should be one object in the designer: "this parameter, along this axis, from this anchor", and Studio derives the base and direction.
- Show a live readout during drag, and let the author pick a display value different from the stored one.

---

### Archicad PARAM-O and Library Part Maker (Archicad 25 to 29)
**How it works:**
- PARAM-O is "a node-based environment" for parametric objects, saved as normal GDL objects that "work in every ARCHICAD - even if PARAM-O is not installed". Available to SSA/Forward customers only ([Archicad 27 help, PARAM-O](https://help.graphisoft.com/AC/27/INT/_AC27_Help/065_PARAM-O/065_PARAM-O-1.htm)).
- Editor: node tree left, canvas middle, 3D preview right; automatic or manual preview update ([PARAM-O Editor](https://help.graphisoft.com/AC/27/INT/_AC27_Help/065_PARAM-O/065_PARAM-O-5.htm)).
- To expose a value, set "Create Parameter" to true on an input node; the node name "will be visible in the Object Settings Dialog". "You can use as many parameters as you wish" ([Making an Object Parametric](https://help.graphisoft.com/AC/27/INT/_AC27_Help/065_PARAM-O/065_PARAM-O-7.htm)).
- Library Part Maker builds GDL parts from 2D and 3D model elements, "without GDL programming knowledge", for objects, windows, doors, skylights, lamps and MEP parts ([Archicad 29 help, LPM](https://help.graphisoft.com/AC/29/INT/_AC29_Help/046_LibraryPartMaker/046_LibraryPartMaker-1.htm)).
- PARAM-O shipped on Windows and macOS in March 2021 after a July 2020 preview ([Graphisoft press release, 2021](https://www.mynewsdesk.com/graphisoft/pressreleases/architects-and-engineers-can-now-create-building-component-libraries-parametrically-with-new-built-in-parametric-object-design-tool-for-archicad-dot-dot-dot-3083614)).

**Good to use because:**
- One flag on a node turns a value into a user parameter, the same idea as Studio's exposed inputs ([PARAM-O help](https://help.graphisoft.com/AC/27/INT/_AC27_Help/065_PARAM-O/065_PARAM-O-7.htm)).
- Output runs without the authoring tool installed ([PARAM-O help](https://help.graphisoft.com/AC/27/INT/_AC27_Help/065_PARAM-O/065_PARAM-O-1.htm)).

**Bad to use because:**
- PARAM-O's help says nothing about ordering, grouping, value lists or custom settings pages ([Making an Object Parametric](https://help.graphisoft.com/AC/27/INT/_AC27_Help/065_PARAM-O/065_PARAM-O-7.htm)). The custom UI gap stays with hand-written GDL.
- Preview limits: "No texture handling", "No edge rendering", "every number value is in meters" ([PARAM-O Editor](https://help.graphisoft.com/AC/27/INT/_AC27_Help/065_PARAM-O/065_PARAM-O-5.htm)).
- Paid tier only (same page). Graphisoft wishlist threads asking for easier object creation were blocked (403), not verified.

**Numbers:**
| property | value | source |
|---|---|---|
| Parameter count limit | none stated | [PARAM-O help](https://help.graphisoft.com/AC/27/INT/_AC27_Help/065_PARAM-O/065_PARAM-O-7.htm) |
| LPM part types | 6 (object, window, door, skylight, lamp, MEP) | [LPM help](https://help.graphisoft.com/AC/29/INT/_AC29_Help/046_LibraryPartMaker/046_LibraryPartMaker-1.htm) |

**Take for Studio:**
- Exposing a node as a parameter must also open the door to the window designer (order, group, control type), or authors fall back to code.

---

### SketchUp Dynamic Components (help pages updated Sep 2026; forum 2015 to 2025)
**How it works:**
- Authors open Component Attributes, press the plus icon, pick a predefined attribute or type a custom name ("must start with a letter and cannot contain any spaces"), remove with the minus icon ([SketchUp help, Adding Attributes](https://help.sketchup.com/en/sketchup/adding-attributes)).
- The Details arrow sets display rules: users cannot see it, or see it as a text box, or pick from a list the author defines ([SketchUp help, Defining Attribute Values](https://help.sketchup.com/hu/sketchup/defining-attribute-values)).
- End users see the Component Options window with "preset options built into the component", and the Interact tool runs click behaviours ([SketchUp help, Interacting](https://help.sketchup.com/en/sketchup/interacting-dynamic-components)).
- Formulas: spreadsheet style, CHOOSE(OPTIONINDEX("Material"),...), NEAREST, LARGEST, SMALLEST, CURRENT("LenX") to validate a Scale tool action ([SketchUp help, functions](https://help.sketchup.com/en/sketchup/dynamic-components-sketchup-function-examples)). "All lengths are in inches and angles in degrees" ([Defining Attribute Values](https://help.sketchup.com/hu/sketchup/defining-attribute-values)).
- Scaling: a constrained length shows in black and the Scale tool cannot change it; unconstrained values show light grey ([SketchUp help, Constraining](https://help.sketchup.com/en/sketchup/constraining-attributes-dynamic-component)). The Scale tool attribute hides chosen handles, "a Pro only feature" ([SketchUp help, hiding scale handles](https://help.sketchup.com/sketchup/hiding-scale-handles-dynamic-component)).

**Good to use because:**
- Two dialogs, two audiences: Attributes for authors, Options for users ([Adding Attributes](https://help.sketchup.com/en/sketchup/adding-attributes); [Interacting](https://help.sketchup.com/en/sketchup/interacting-dynamic-components)).
- Direct manipulation still works and the object can snap or clamp the result (NEAREST, LARGEST) ([functions](https://help.sketchup.com/en/sketchup/dynamic-components-sketchup-function-examples)).
- Black vs grey shows at a glance which sizes are locked ([Constraining](https://help.sketchup.com/en/sketchup/constraining-attributes-dynamic-component)).

**Bad to use because:**
- Units leak: formulas run in inches; a forum user calls units "just weird", only cm or inches, "cannot be changed later without having to change all formulas" ([forum, 2017](https://forums.sketchup.com/t/errors-referencing-custom-atributes/53067), third party). Turning off "Display units format" makes metric DCs revert to inches "with the formulas running awry" ([forum, 2021](https://forums.sketchup.com/t/dynamic-component-error-automatic-re-scaling/122582), third party).
- Slow and fragile: 20 to 30 second lag after a formula edit, and a "merging multiple items might be slow" warning when selecting 60+ components ([forum, 2019](https://forums.sketchup.com/t/30-second-lag-when-updating-a-formula-in-a-dc-why/100838)). Random rescaling of nested groups ([forum, 2020](https://forums.sketchup.com/t/dynamic-component-error-automatic-re-scaling/122582)).
- Stalled: users say DCs still have "many, perhaps most of the bugs they had when originally introduced" and are still a Ruby extension ([forum, 2022](https://forums.sketchup.com/t/live-components-news-updates/175309)); "neither has received substantial updates since release" about DCs and Live Components ([forum, 2025](https://forums.sketchup.com/t/is-trimble-creator-active/317454)). Trimble's FAQ says only that DCs "will continue to function" while new work goes to Live Components, which need an internet connection to author ([Live Components FAQ](https://help.sketchup.com/en/sketchup-live-components/frequently-asked-questions)).

**Numbers:**
| property | value | source |
|---|---|---|
| Internal formula length unit | inches | [Defining Attribute Values](https://help.sketchup.com/hu/sketchup/defining-attribute-values) |
| Formula update lag reported | 20 to 30+ s | [forum, 2019](https://forums.sketchup.com/t/30-second-lag-when-updating-a-formula-in-a-dc-why/100838) |
| Selection size that triggers merge warning | 60+ components (user report) | [forum, 2019](https://forums.sketchup.com/t/30-second-lag-when-updating-a-formula-in-a-dc-why/100838) |
| Display rules per attribute | 4 (hidden, view, text box, list) | [Defining Attribute Values](https://help.sketchup.com/hu/sketchup/defining-attribute-values) |

**Take for Studio:**
- Keep "author view vs user view" as two modes of one window, and the per-field rule "hidden / read only / editable / choose from list".
- Let a drag (scale) go through the object's own rules (snap to list, clamp), and show which sizes are locked.
- Store and show values in project units only.

---

### Fusion parameters and configurations (Fusion help, current)
**How it works:**
- Model parameters are made automatically with each feature; user parameters are added in the Parameters dialog with name, unit, expression and comment ([Fusion help, Parameters](https://help.autodesk.com/cloudhelp/ENU/Fusion-Model/files/SLD-MODIFY-PARAMETERS.htm); [Create or edit parameters](https://help.autodesk.com/cloudhelp/ENU/Fusion-Model/files/SLD-MODIFY-CHANGE-PARAMETERS.htm)).
- Favourites float to the top of the table; naming a dimension while modelling adds it to Favourites "so that it is easy to find". Filters show only Favourites or only User parameters; columns sort; "Sort in Timeline Order" exists ([Fusion help, Parameters](https://help.autodesk.com/cloudhelp/ENU/Fusion-Model/files/SLD-MODIFY-PARAMETERS.htm)).
- Any value field accepts a parameter name with suggestions as you type, on the canvas and in dialogs ([same page](https://help.autodesk.com/cloudhelp/ENU/Fusion-Model/files/SLD-MODIFY-PARAMETERS.htm)).
- Configurations: a table where each row is a variant and each configured parameter, feature, visibility, suppression or theme is a column. "The first row represents the Default Configuration. It cannot be deleted or moved" ([Fusion help, Configuration Table](https://help.autodesk.com/cloudhelp/ENU/Fusion-Configurations/files/CFG-CONFIGURATIONS.htm)). A variant can be inserted into another design as a configured component ([Configurations overview](https://help.autodesk.com/cloudhelp/ENU/Fusion-Configurations/files/CFG-OVERVIEW.htm)).

**Good to use because:**
- Naming a value marks it important automatically (auto-favourite), so the short list builds itself ([Fusion help](https://help.autodesk.com/cloudhelp/ENU/Fusion-Model/files/SLD-MODIFY-PARAMETERS.htm)).
- Table-driven variants are easy to scan and compare, and a variant is chosen at insert time ([Configuration Table](https://help.autodesk.com/cloudhelp/ENU/Fusion-Configurations/files/CFG-CONFIGURATIONS.htm)).
- Automatic Compute can be turned off to batch edits on big models ([Fusion help](https://help.autodesk.com/cloudhelp/ENU/Fusion-Model/files/SLD-MODIFY-PARAMETERS.htm)).

**Bad to use because:**
- The Parameters dialog is a flat table; no custom layout, groups or controls beyond sort and filter ([Fusion help](https://help.autodesk.com/cloudhelp/ENU/Fusion-Model/files/SLD-MODIFY-PARAMETERS.htm)). Forum ideas asking to reorder user parameters were blocked (403), not verified.
- Configurations on the free personal plan: only a third party forum claim, not verified.

**Numbers:**
| property | value | source |
|---|---|---|
| Sortable columns | 5 (Name, Unit, Expression, Value, Comment) | [Fusion help](https://help.autodesk.com/cloudhelp/ENU/Fusion-Model/files/SLD-MODIFY-PARAMETERS.htm) |
| Max configurations | none stated | [Configuration Table](https://help.autodesk.com/cloudhelp/ENU/Fusion-Configurations/files/CFG-CONFIGURATIONS.htm) |

**Take for Studio:**
- Presets as a table (rows = presets, columns = exposed inputs) is a good second view next to the form.
- Auto-favourite any input the author names; offer a "favourites only" filter in the object's panel.

---

### Figma component properties (help article, current)
**How it works:**
- Four property types: boolean (layer visibility), instance swap (with "preferred instances"), text, variant ([Figma help, component properties](https://help.figma.com/hc/en-us/articles/5579474826519-Explore-component-properties)).
- Authors create a property from the right sidebar or straight from a nested layer; delete with right-click or Delete; "Hover over a property to reveal handles. Click and drag to reorder" ([same page](https://help.figma.com/hc/en-us/articles/5579474826519-Explore-component-properties)).
- Users of an instance see "a single set of consolidated controls in the right panel", and authors can "Expose specific nested instances" so inner properties show next to the outer ones ([same page](https://help.figma.com/hc/en-us/articles/5579474826519-Explore-component-properties)).

**Good to use because:**
- Small fixed set of property kinds, each with an obvious control ([Figma help](https://help.figma.com/hc/en-us/articles/5579474826519-Explore-component-properties)).
- Curated swap lists (preferred instances) keep choices short ([Figma help](https://help.figma.com/hc/en-us/articles/5579474826519-Explore-component-properties)).
- Nested exposure flattens a deep object into one panel ([Figma help](https://help.figma.com/hc/en-us/articles/5579474826519-Explore-component-properties)).

**Bad to use because:**
- Kind beats author order: "Variant properties are designed to always sit at the top of the Properties panel"; a boolean between two variants "isn't currently supported" (Figma support answer, [forum, Apr 2026](https://forum.figma.com/ask-the-community-7/unable-to-reorder-boolean-and-variant-properties-49701)).
- "boolean properties only support layer visibility"; text properties have no rich text ([Figma help](https://help.figma.com/hc/en-us/articles/5579474826519-Explore-component-properties)).

**Numbers:**
| property | value | source |
|---|---|---|
| Property kinds | 4 | [Figma help](https://help.figma.com/hc/en-us/articles/5579474826519-Explore-component-properties) |
| Max properties | none stated | [Figma help](https://help.figma.com/hc/en-us/articles/5579474826519-Explore-component-properties) |

**Take for Studio:**
- Drag-to-reorder by handle on hover, applied on release.
- Let a sub-object's inputs be "exposed" into the parent's panel by a toggle.
- Never force order by control type.

---

### ShapeDiver (help center and App Builder SDK releases, 2026)
**How it works:**
- Grasshopper inputs become web controls: Number Slider (keeps Min, Max, Rounding, Digits), Value List, Boolean Toggle, Colour; ShapeDiver components add text and file inputs. Other native inputs "will not translate into exposed controls" ([ShapeDiver, Defining inputs](https://help.shapediver.com/doc/inputs-and-outputs)).
- Label = Grasshopper component name; order and accordion groups come from canvas position and Grasshopper groups; groups named "hide..." start hidden, "ignore..." are skipped ([Defining inputs](https://help.shapediver.com/doc/inputs-and-outputs)).
- After upload, authors can rename, reorder by drag, and hide, but "the grouping is fixed after upload" ([ShapeDiver, Parameter settings](https://help.shapediver.com/doc/parameter-settings)).
- App Builder: components in Grasshopper define App, Containers, Tabs, Widgets; parameters can be hidden or shown "depending on the values of model inputs and outputs" ([App Builder](https://help.shapediver.com/doc/shapediver-app-builder); [Build Apps in Grasshopper](https://help.shapediver.com/doc/build-apps-in-grasshopper)).
- Recent releases add inline accept/reject buttons per parameter, reset values, slider marks, form and table widgets, and an interaction toolbar for selection, dragging and drawing ([AppBuilderSdk releases](https://github.com/shapediver/AppBuilderSdk/releases)).

**Good to use because:**
- Conditional UI is computed by the same model, so the UI and logic never disagree ([Build Apps in Grasshopper](https://help.shapediver.com/doc/build-apps-in-grasshopper)).
- Per-parameter "accept/reject" lets slow models wait for a confirm ([releases 1.12](https://github.com/shapediver/AppBuilderSdk/releases)).
- Embeddable in websites and other apps ([App Builder](https://help.shapediver.com/doc/shapediver-app-builder)).

**Bad to use because:**
- Ordering by canvas position was "unpredictable" in a ShapeDiver staff reply; reordering was "very boring and long" for a user ([McNeel forum, 2019](https://discourse.mcneel.com/t/shapediver-whats-the-logic-behind-sliders-order/84336), third party plus vendor).
- Grouping fixed after upload ([Parameter settings](https://help.shapediver.com/doc/parameter-settings)); the first App Builder template accepts only containers named "left", "right", "top", "bottom" ([Build Apps in Grasshopper](https://help.shapediver.com/doc/build-apps-in-grasshopper)).
- A forum comparison (third party) lists "can be overwhelming" as a con ([McNeel forum, 2024](https://discourse.mcneel.com/t/pros-cons-shapediver-speckle-packhunt-viktor/195738)).

**Numbers:**
| property | value | source |
|---|---|---|
| Native Grasshopper input kinds supported | 4 | [Defining inputs](https://help.shapediver.com/doc/inputs-and-outputs) |
| Grasshopper plugins supported | "over 50" (vendor post) | [McNeel forum, 2024](https://discourse.mcneel.com/t/pros-cons-shapediver-speckle-packhunt-viktor/195738) |
| App Builder latest release | 1.12 (20 Oct, year not shown) | [releases](https://github.com/shapediver/AppBuilderSdk/releases) |

**Take for Studio:**
- Let show-when rules read outputs as well as inputs.
- Offer an "apply" mode per form for slow flows.
- Allow regrouping at any time in the designer.

---

### Hypar functions with input schemas (hypar.json, read from GitHub and hypar.io schemas)
**How it works:**
- Each function ships a hypar.json with an input_schema in JSON Schema; the platform draws the form from it ([HyparSpace OpenOfficeLayout hypar.json](https://github.com/hypar-io/HyparSpace/blob/master/LayoutFunctions/OpenOfficeLayout/hypar.json)).
- UI hints live in "$hypar..." keywords next to standard minimum, maximum, multipleOf, enum, default, description: $hyparOrder, $hyparShowIf, $hyparStyle, $hyparUnitType, $hyparPreferredUnits, $hyparDisplayName, $hyparLock and more ([InputSchemaProperty.json](https://hypar.io/Schemas/InputSchemaProperty.json)).
- $hyparShowIf takes conditions with "equals" or "does not equal" and a type of "any" or "all" ([InputSchemaProperty.json](https://hypar.io/Schemas/InputSchemaProperty.json)).
- $hyparOrder: "Usually it is unnecessary to set this explicitly, it will be added when you publish." The example uses 0, 0.5, 1, 2 so a field can be slotted between others ([schema](https://hypar.io/Schemas/InputSchemaProperty.json); [example](https://github.com/hypar-io/HyparSpace/blob/master/LayoutFunctions/OpenOfficeLayout/hypar.json)).
- Overrides let users edit generated elements afterwards (add, remove, revert per element) ([Function.json](https://hypar.io/Schemas/Function.json)).

**Good to use because:**
- One declarative file defines type, range, step, unit, order, visibility and help text, so the UI needs no code (measured from [example](https://github.com/hypar-io/HyparSpace/blob/master/LayoutFunctions/OpenOfficeLayout/hypar.json)).
- Units are typed per field with preferred metric and imperial display ([example](https://github.com/hypar-io/HyparSpace/blob/master/LayoutFunctions/OpenOfficeLayout/hypar.json)).
- Overrides keep manual edits on top of generated output ([Function.json](https://hypar.io/Schemas/Function.json)).

**Bad to use because:**
- Layout is not designable: a field list with order numbers and a few styles ("row", "matrix", "number", "standard") ([schema](https://hypar.io/Schemas/InputSchemaProperty.json)).
- Show-if supports only equals / does not equal, no ranges ([schema](https://hypar.io/Schemas/InputSchemaProperty.json)).
- Hypar's home page now sells "Space Planning Software"; no current docs for the function SDK were found ([hypar.io](https://hypar.io/)). Status of the function platform unclear.

**Numbers:**
| property | value | source |
|---|---|---|
| Distinct $hypar UI keywords | 22 (measured: regex over schema file, 2026-11-01) | [InputSchemaProperty.json](https://hypar.io/Schemas/InputSchemaProperty.json) |
| Unit types | 13 (measured, enum length) | [InputSchemaProperty.json](https://hypar.io/Schemas/InputSchemaProperty.json) |
| Show-if comparison kinds | 2 | [InputSchemaProperty.json](https://hypar.io/Schemas/InputSchemaProperty.json) |
| Inputs in Open Office Layout | 7, 4 with explicit order (measured) | [hypar.json](https://github.com/hypar-io/HyparSpace/blob/master/LayoutFunctions/OpenOfficeLayout/hypar.json) |

**Take for Studio:**
- Save the designed window as a plain, versioned schema (type, range, step, unit, order, show-when, help) next to the flow. Easy to diff, AOT friendly (no reflection).
- Use fractional order keys so a drag inserts without renumbering.

---

### Vizcom (docs, 2026)
**How it works:**
- Users pick a render Style from a dropdown, then set an Influence slider: "High influence makes the style dominant; low influence keeps more of your original sketch characteristics" ([Vizcom docs, Styles](https://docs.vizcom.com/styles-overview)).
- The older "Drawing Influence" page is now marked Legacy ([Vizcom docs](https://docs.vizcom.com/drawing-influence)).

**Good to use because:**
- Very few controls: a preset plus one strength slider ([Vizcom docs](https://docs.vizcom.com/styles-overview)).

**Bad to use because:**
- No numeric range stated for the slider ([Vizcom docs](https://docs.vizcom.com/styles-overview)). It is an AI renderer, not a parametric object.

**Numbers:**
| property | value | source |
|---|---|---|
| Example styles listed | 3 essentials, 3 stylized, 2 industry | [Vizcom docs](https://docs.vizcom.com/styles-overview) |

**Take for Studio:**
- For end users, a preset picker plus one or two "strength" sliders often beats twenty raw inputs.

---

### Onshape configurations (extra product configurator, help current)
**How it works:**
- Inputs are lists, checkboxes and configuration variables; "Each configuration input is represented as a collapsible table"; one Configurations panel per studio ([Onshape help, Configurations](https://cad.onshape.com/help/Content/configurations.htm)).
- Visibility conditions: "Configuration inputs can only control the visibility of inputs that appear below them"; "Hidden inputs always have their default value"; conditions are additive; option rules hide single list options; broken conditions are "automatically repaired (removed)" with a warning ([Onshape help, Visibility conditions](https://cad.onshape.com/help/Content/PartStudio/visibility_conditions.htm)).

**Good to use because:**
- The "only control inputs below" rule makes forms read top to bottom and prevents loops ([Onshape help](https://cad.onshape.com/help/Content/PartStudio/visibility_conditions.htm)).
- Clear rule for hidden values (they use the default) ([same](https://cad.onshape.com/help/Content/PartStudio/visibility_conditions.htm)).
- Option-level rules shrink a list instead of hiding the whole field ([same](https://cad.onshape.com/help/Content/PartStudio/visibility_conditions.htm)).

**Bad to use because:**
- When an input is deleted, its conditions are removed automatically, with only a warning, so rules can vanish ([same](https://cad.onshape.com/help/Content/PartStudio/visibility_conditions.htm)).

**Numbers:**
| property | value | source |
|---|---|---|
| Configurations panels per studio | 1 | [Onshape help](https://cad.onshape.com/help/Content/configurations.htm) |

**Take for Studio:**
- Adopt "a show-when rule may only depend on fields above it", the "hidden means default" rule, and option-level rules for choice lists.

---

### Window and form builders (Retool, Qt Designer, Visual Studio XAML Designer, Figma auto layout)
**How it works:**
- Retool: "Canvas frames use a 12-column grid layout"; edges snap as you drag; frames grow by adding rows; the Inspector on the right holds settings grouped as Content, Interaction, Appearance; a Component tree lists everything ([Retool docs, Classic app IDE](https://docs.retool.com/classic-apps/concepts/ide)).
- Qt Designer: forms must be put into layouts (horizontal, vertical, grid, form, splitter) so widgets "will be resized correctly"; Ctrl+1 to Ctrl+6 apply layouts, Ctrl+0 breaks one ([Qt 6 docs, layouts](https://doc.qt.io/qt-6/designer-layouts.html)). Property Editor shows the selection and bolds changed properties; Ctrl+R previews ([Qt 6 docs, widget mode](https://doc.qt.io/qt-6/designer-widget-mode.html)).
- XAML Designer: snaplines, grid rails, margin adorners, Document Outline with hide and lock, a Properties window with search; each property has a marker that shows default, local resource, or "an orange box typically indicates a data binding" ([Microsoft Learn, XAML Designer, 2026](https://learn.microsoft.com/en-us/visualstudio/xaml-tools/creating-a-ui-by-using-xaml-designer-in-visual-studio)).
- Figma auto layout: direction, gap, padding, hug / fill / fixed sizing, wrap, min and max sizes ([Figma help, auto layout](https://help.figma.com/hc/en-us/articles/360040451373-Guide-to-auto-layout)).

**Good to use because:**
- Snap to a column grid plus auto-growing rows means no pixel maths ([Retool](https://docs.retool.com/classic-apps/concepts/ide)).
- Layout containers make forms resize correctly ([Qt](https://doc.qt.io/qt-6/designer-layouts.html)); hug and fill cover most cases with three words ([Figma](https://help.figma.com/hc/en-us/articles/360040451373-Guide-to-auto-layout)).
- One tree for structure, one inspector for the selection, one preview key ([Qt](https://doc.qt.io/qt-6/designer-widget-mode.html); [Retool](https://docs.retool.com/classic-apps/concepts/ide)).
- Property markers make binding state visible per field ([Microsoft Learn](https://learn.microsoft.com/en-us/visualstudio/xaml-tools/creating-a-ui-by-using-xaml-designer-in-visual-studio)).

**Bad to use because:**
- In Qt, once in a layout you cannot move or resize a widget by hand ([Qt](https://doc.qt.io/qt-6/designer-layouts.html)); free and laid-out modes are separate.
- Retool says "The AI app builder is the recommended way to build apps" and classic drag-drop gets less new work ([Retool docs, Layout and structure](https://docs.retool.com/classic-apps/guides/layout-structure/)).

**Numbers:**
| property | value | source |
|---|---|---|
| Retool grid | 12 columns; default max width 1200 px; desktop min 800 px; mobile below 600 px | [Retool IDE](https://docs.retool.com/classic-apps/concepts/ide) |
| Qt layout kinds | 6 (H, V, H split, V split, grid, form) | [Qt layouts](https://doc.qt.io/qt-6/designer-layouts.html) |
| XAML Designer zoom | 12.5% to 800% | [Microsoft Learn](https://learn.microsoft.com/en-us/visualstudio/xaml-tools/creating-a-ui-by-using-xaml-designer-in-visual-studio) |
| Figma sizing modes | 3 (hug, fill, fixed) | [Figma help](https://help.figma.com/hc/en-us/articles/360040451373-Guide-to-auto-layout) |

**Take for Studio:**
- Designer = palette (controls) + canvas on a snapping column grid inside auto-layout sections + outline tree + inspector + Preview toggle.
- Inspector shows a marker per property: default, set, bound to an input, or driven by a rule.
- Sections stack vertically and hug content; fields fill width by default.

---

### Cross-tool patterns (synthesis of the sections above)
**How it works:**
- Two audiences everywhere: author view vs user view (SketchUp Attributes vs Options, Dynamo vs Player, GDL editor vs settings page) ([SketchUp](https://help.sketchup.com/en/sketchup/adding-attributes); [Dynamo Player](https://help.autodesk.com/cloudhelp/2026/ENU/Revit-HaveYouTried/files/GUID-E8205058-9CA4-4CFF-95F5-A6AA1CDA7346.htm); [GDL](https://gdl.graphisoft.com/gdl-basics/graphical-ui/)).
- Ordering is the most common pain where it is implicit (Dynamo Player, ShapeDiver, Figma variants) ([Dynamo forum](https://forum.dynamobim.com/t/dynamo-player-input-order/13471); [McNeel forum](https://discourse.mcneel.com/t/shapediver-whats-the-logic-behind-sliders-order/84336); [Figma forum](https://forum.figma.com/ask-the-community-7/unable-to-reorder-boolean-and-variant-properties-49701)).
- Conditional visibility exists in GDL (HIDEPARAMETER), ShapeDiver, Hypar and Onshape, with very different rule power ([GDL](https://gdl.graphisoft.com/gdl-basics/parameter-logic/); [ShapeDiver](https://help.shapediver.com/doc/build-apps-in-grasshopper); [Hypar schema](https://hypar.io/Schemas/InputSchemaProperty.json); [Onshape](https://cad.onshape.com/help/Content/PartStudio/visibility_conditions.htm)).

**Good to use because:**
- Handles bound to parameters (Revit, GDL, SketchUp Scale tool) give the fastest edits in the drawing ([Revit](https://help.autodesk.com/cloudhelp/2024/ENU/Revit-Customize/files/GUID-C30A7EFC-3030-4E9D-A305-C66B50E1DF75.htm); [GDL](https://gdl.graphisoft.com/gdl-basics/hotspots-graphical-editing); [SketchUp](https://help.sketchup.com/en/sketchup/constraining-attributes-dynamic-component)).

**Bad to use because:**
- No tool studied offers a true drag-and-drop designer for a parametric object's settings page; GDL is code with pixel numbers, the rest are lists ([GDL Reference](https://gdl.graphisoft.com/reference-guide/the-user-interface-script); [Fusion](https://help.autodesk.com/cloudhelp/ENU/Fusion-Model/files/SLD-MODIFY-PARAMETERS.htm); [ShapeDiver](https://help.shapediver.com/doc/parameter-settings)).

**Numbers:**
| property | value | source |
|---|---|---|
| Tools with explicit drag reorder of parameters | Figma, ShapeDiver (after upload), Revit (Move Up/Down) | [Figma](https://help.figma.com/hc/en-us/articles/5579474826519-Explore-component-properties); [ShapeDiver](https://help.shapediver.com/doc/parameter-settings); [Revit](https://help.autodesk.com/cloudhelp/2024/ENU/Revit-Customize/files/GUID-921F7A15-D191-4F75-8243-4989C482E253.htm) |

**Take for Studio:**
- A drag-and-drop window designer for object parameters is an open gap in the CAD tools studied; doing it with a layout grid, explicit order and visible rules is a real differentiator.

---

## Not verified (blocked or not opened)
- forums.autodesk.com (Revit Ideas, Fusion ideas, Dynamo Player idea): HTTP 403.
- community.graphisoft.com (GDL hotspot threads, PARAM-O and "Easier Parametric Object Creation" wishes): HTTP 403.
- forums.augi.com and augi.com articles: HTTP 403.
- autodesk.com AEC and Fusion blogs (Dynamo Player inputs 2018, Fusion parameters, Configurations FAQ): HTTP 403.
- emea.support.arkance.world (Revit 2023 Player): HTTP 403.
- revit.miraheze.org: HTTP 403. reddit.com: not reachable.
- prod-aws-help.sketchup.com: host not allowed in this session.
- docs.appsmith.com: index returned "Page Not Found"; Appsmith not covered.
- Revit formula syntax page ("Valid Formula Syntax and Abbreviations"): not found, not used.
