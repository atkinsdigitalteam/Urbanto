# R20A notes: parametric objects in the drawing, and window designers for them

Agent R20A, report C20. All pages read on 2026-11-01. "Third party" means not the vendor or author. "Forum" means user posts, not vendor statements.
Pages that failed or need login are listed at the end under "Not verified".

---

## Part A. Rhino and Grasshopper

### Human UI (Grasshopper plug-in, 0.8.10 for Rhino 8, looked at 2026-11-01)
**How it works:**
- A WPF window that lives outside the Grasshopper canvas. The README calls it "a new interface paradigm for Grasshopper" and says it "is experimental software and may contain bugs and incomplete features" ([GitHub README](https://github.com/andrewheumann/humanui)).
- The window is built from canvas components. In the source there are separate "Create" components per control (Create Slider, Create Button, Create Pull Down...), main components (Launch Window, Add Elements, Value Listener, Hide Show) and "Set" components to push values back (Set Slider, Set Data Table...). Measured from the repo file list (method in Numbers) via [jsDelivr flat listing](https://data.jsdelivr.com/v1/package/gh/andrewheumann/humanui@master/flat).
- So every control needs wiring: a Create component, a Value Listener on the created element (not the original slider), and often a Set component. The author tells users to "connect it to the Create Slider component, not the original sliders" ([forum, Andrew Heumann, 2021](https://discourse.mcneel.com/t/human-ui-value-listener-live-update/)).
- Origin: built at NBBJ over about 10 months in 2015 to 2016, open source since January 2016 ([grasshopper3d group page](https://www.grasshopper3d.com/group/human-ui), [README](https://github.com/andrewheumann/humanui)).
- Maintenance: no upstream commit between Feb 14, 2022 and May 2026. A contributor PR modernised it for Rhino 8 / .NET 7, merged Jun 9, 2026 ([commits](https://github.com/andrewheumann/humanui/commits/master), [PR #9](https://github.com/andrewheumann/humanui/pull/9)). The author published 0.8.10 "for Windows only" and said he no longer has a Windows machine ([PR #9](https://github.com/andrewheumann/humanui/pull/9)). A separate Eto rewrite (0.9.43) is alpha ([forum thread, May 2026](https://discourse.mcneel.com/t/new-humanui-for-rhino-8-wip-for-testing/219339)).

**Good to use because:**
- No code needed; tabs, sliders, pull-downs, checkboxes, 3D viewports, browsers and data tables are available ([README](https://github.com/andrewheumann/humanui)).
- Large install base: 80,207 downloads on the package server ([Yak human-ui](https://yak.rhino3d.com/packages/human-ui)).
- A co-author reports performance "on par with WPF" when the window is a fixed set of elements updated through Value Listeners ([forum, marcsyp, Nov 2023](https://discourse.mcneel.com/t/how-efficient-is-human-ui/)).

**Bad to use because:**
- Broke in Rhino 8 under .NET Core; users had to switch Rhino to .NET Framework with SetDotNetRuntime, and Human UI conflicted with UI+ ([forum thread, 2024 to 2025](https://discourse.mcneel.com/t/grashopper-player-human-ui-not-working-rhino-8/)). Forum, third party.
- The 2026 update shipped regressions through auto-update: collapsed Stack elements could not reopen, value listeners stopped updating, "Object expired during a solution" errors; one user said it "had broken widely used scripts in her office" ([forum thread, Jun to Aug 2026](https://discourse.mcneel.com/t/new-humanui-for-rhino-8-wip-for-testing/219339)). Forum.
- Lifecycle bugs fixed only in 2026: closing a window destroyed it, re-launch threw null reference, windows opened off-screen, a static list caused "cross-talk" between instances, slider drags caused "solve storms" ([PR #9](https://github.com/andrewheumann/humanui/pull/9)).
- Slow updates: hidden secondary windows still recompute and "take multiple seconds to execute"; another user: "Human UI is very slow in response, and it drags the whole GH workflow down significantly" ([forum, 2021 to 2024](https://discourse.mcneel.com/t/un-used-windows-slow-the-definition-down/)). Forum.
- The UI lives in the same graph as the logic: "made the script a bit messy with all the added components" ([forum, May 2023](https://discourse.mcneel.com/t/human-ui-vs-ui-your-thoughts-and-experiences-on-which-to-use/)). Forum.
- Depends on abandoned libraries: MetroChart and Markdown.Xaml are "both abandoned upstream", MahApps.Metro 1.x was "pulled from NuGet" ([PR #9](https://github.com/andrewheumann/humanui/pull/9)).
- Windows only (WPF) ([README](https://github.com/andrewheumann/humanui)).

**Numbers:**
| property | value | source |
|---|---|---|
| Component source files under /Components | 84 (31 UI Elements, 9 UI Containers, 5 UI Graphs, 16 UI Main, 22 UI Output, 1 testing) | measured: Python count of `.cs` paths containing `/Components/` in [jsDelivr flat listing](https://data.jsdelivr.com/v1/package/gh/andrewheumann/humanui@master/flat). Files, not exact component count (one is a template). |
| Downloads | 80,207 (0.8.10, updated 2026-06-09) | [Yak](https://yak.rhino3d.com/packages/human-ui) |
| GitHub stars / forks / commits | 50 / 30 / 239 | [GitHub](https://github.com/andrewheumann/humanui) |
| Gap in upstream commits | Feb 14, 2022 to May 16, 2026 | [commits](https://github.com/andrewheumann/humanui/commits/master) |
| Debounce added to stop solve storms | 50 ms | [PR #9](https://github.com/andrewheumann/humanui/pull/9) |
| Test cases added in 2026 | 418 theory cases (reflection sweep) | [PR #9](https://github.com/andrewheumann/humanui/pull/9) |
| Forum category activity | e.g. "Button on/off staying on": 29 replies, 6,324 views | [forum category](https://discourse.mcneel.com/c/grasshopper/human-ui/81) |

**Take for Studio:**
- Never make the form a graph of "create, listen, set" nodes. The form must be a separate, declarative document bound to flow inputs by id.
- Debounce and coalesce re-solves during slider drags from day one (Human UI needed a 50 ms debounce added a decade later).
- Ship the form designer in-box, versioned with Studio, not as a third-party UI stack that breaks on runtime changes.

### Synapse, UI+, DKUI and other Grasshopper window plug-ins (looked at 2026-11-01)
**How it works:**
- Synapse builds Eto.Forms windows from Grasshopper components; one user calls it "ETO based, so all the advantages of ETO but with HumanUI style of GUI building" ([forum thread, May 2025](https://discourse.mcneel.com/t/the-future-of-grasshopper-user-interfaces/204466)). Forum.
- Synapse 0.5.0 by Will Wang is the only version on the package server ([Yak Synapse](https://yak.rhino3d.com/packages/synapse)).
- The same thread lists the field: native sliders, Remote Control Panel, Human UI, Eto, Synapse, UI+, WebUI, DKUI, Tkinter, OSC hardware and even Google Sheets as an "interface" ([forum thread](https://discourse.mcneel.com/t/the-future-of-grasshopper-user-interfaces/204466)).
- Writing custom component UI in code is seen as hard in Grasshopper 1: "is this really such an ungrateful task in GH1?" ([forum, Nov 2025](https://discourse.mcneel.com/t/custom-components-gui-easier-in-gh2/211958)).

**Good to use because:**
- Eto runs on Windows and Mac, unlike Human UI's WPF ([forum thread](https://discourse.mcneel.com/t/the-future-of-grasshopper-user-interfaces/204466)).

**Bad to use because:**
- Synapse is "Not so easy to build with or understand as HumanUI" (kiteboardshaper); WebUI had "no development in last 4 years"; UI+ last updated March 2024 ([forum thread, May 2025](https://discourse.mcneel.com/t/the-future-of-grasshopper-user-interfaces/204466)). Forum.
- Eto is "severally lacking in online teaching resources"; WPF needs "at least 6 month of daily work" ([same thread](https://discourse.mcneel.com/t/the-future-of-grasshopper-user-interfaces/204466)). Forum.
- UI+ sliders cannot take typed values ([forum, Nov 2025](https://discourse.mcneel.com/t/human-ui-vs-ui-your-thoughts-and-experiences-on-which-to-use/)). Forum.

**Numbers:**
| property | value | source |
|---|---|---|
| Synapse downloads | 2,539 (v0.5.0, updated 2026-01-07) | [Yak](https://yak.rhino3d.com/packages/synapse) |
| UI options users list for Grasshopper | 13 rows in the thread's own list (native, RCP, Human UI, Eto, Synapse, UI+, WebUI, other C#/Python GUIs, DKUI, OSC, Google Sheets, GrasshopperGold) | [forum thread](https://discourse.mcneel.com/t/the-future-of-grasshopper-user-interfaces/204466) |

**Take for Studio:**
- Fragmentation is the evidence: when the host has no good form designer, users scatter over a dozen half-maintained options. Studio should own one.

### Grasshopper Remote Control Panel (RCP) (Rhino 8, looked at 2026-11-01)
**How it works:**
- A Rhino panel that shows published canvas controls so users can drive a definition without the canvas; users publish sliders, toggles, buttons and panels by right-click, and can group and collapse them ([RCP wishes thread, 2017 onward](https://discourse.mcneel.com/t/remote-control-panel-rcp-wishes-and-feedback/51545)).
- Feedback was logged to David Rutten as RH-43102 in December 2017 ([same thread](https://discourse.mcneel.com/t/remote-control-panel-rcp-wishes-and-feedback/51545)).
- In Sep 2026 a forum reply from Japhy said the comments were added to "the existing Feature youtrack that David created a while ago" and "there isn't anything available to test" ([forum, Sep 2026](https://discourse.mcneel.com/t/future-plans-for-a-more-robust-remote-control-panel-in-grasshopper-2/220904)).

**Good to use because:**
- Zero setup; a user calls it their go-to "because it is easy to set up" ([forum, May 2025](https://discourse.mcneel.com/t/the-future-of-grasshopper-user-interfaces/204466)). Forum.

**Bad to use because:**
- "the native RCP really does feel like the perhaps hardest dropped ball in Grasshopper history" (AndersDeleuran) ([forum, May 2025](https://discourse.mcneel.com/t/the-future-of-grasshopper-user-interfaces/204466)). Forum.
- "is stuck in like version 0.1 since the beginning" (2021); no typed slider values; no mousewheel scroll; light grey styling makes controls "look disabled" ([RCP wishes thread](https://discourse.mcneel.com/t/remote-control-panel-rcp-wishes-and-feedback/51545)). Forum; posts from 2017 to 2023, the oldest are over 5 years old.
- Rhino 8 beta: panel cannot scroll, and docked buttons "stop working" ([forum, Sep 2023](https://discourse.mcneel.com/t/new-ui-grasshopper-remote-control-panel-issues/165026)). Forum.
- A button that launches a script UI locks the canvas, "a known issue for over 10 years" ([forum, May 2025](https://discourse.mcneel.com/t/the-future-of-grasshopper-user-interfaces/204466)). Forum.

**Numbers:**
| property | value | source |
|---|---|---|
| Control types | sliders, toggles, buttons, panels (4) | [RCP wishes thread](https://discourse.mcneel.com/t/remote-control-panel-rcp-wishes-and-feedback/51545) |
| Wishes thread size | 57 replies, last activity Oct 3, 2026 | [listed in GH2 thread](https://discourse.mcneel.com/t/future-plans-for-a-more-robust-remote-control-panel-in-grasshopper-2/220904) |
| Age of first logged feedback | Dec 14, 2017 (RH-43102) | [RCP wishes thread](https://discourse.mcneel.com/t/remote-control-panel-rcp-wishes-and-feedback/51545) |

**Take for Studio:**
- "Publish a control" from the graph is a good shortcut, but it needs typed entry, scrolling, clear enabled/disabled styling and a real layout model. Studio's form already has sections; keep "publish from node" as a fast path into that form.

### Grasshopper Player and Get components (Rhino 8, looked at 2026-11-01)
**How it works:**
- GrasshopperPlayer "allows to load and execute a grasshopper definition (*.gh, *.ghx) without showing the Grasshopper window"; the scripted form takes a file path ([Rhino 8 help](https://docs.mcneel.com/rhino/8/help/en-us/commands/grasshopper.htm)).
- Inputs come from "Get" components in Params > Util; each becomes a command-line prompt; Minimum, Maximum and Presets "only used in the Grasshopper Player" ([Hops component guide](https://developer.rhino3d.com/guides/compute/hops-component/)).
- Outputs go into the model with Context Bake or print with Context Print ([forum reply, Dec 2021](https://discourse.mcneel.com/t/grasshopper-definition-to-toolbar-button/135082/2), [Hops guide](https://developer.rhino3d.com/guides/compute/hops-component/)).
- McNeel markets it as a way for people without Grasshopper experience to run shared definitions ([Rhino features page](https://www.rhino3d.com/features/grasshopper/player/)).

**Good to use because:**
- One definition serves as a Rhino command; the same Get components define Hops/Compute inputs ([Hops guide](https://developer.rhino3d.com/guides/compute/hops-component/)).

**Bad to use because:**
- Only sequential command-line prompts; no form, no live preview of all inputs at once. Users ask for basics such as Enter to keep a default and an Undo option on Get Integer ([wish list thread, 2020 to 2021](https://discourse.mcneel.com/t/grasshopper-player-custom-tools-wish-list/114844)). Forum, about 5 years old (Dec 2020).
- The definition re-solves between prompts: "each of seven Get Number prompts took 2-3 seconds", and "the script runs 5 times and successfully bakes the curve 2 times" ([forum, Jan 2022](https://discourse.mcneel.com/t/bake-with-attributes-via-gh-player/135996)). Forum, older than 2026 but still Player behaviour.
- The result is baked geometry (Context Bake, see [Hops guide](https://developer.rhino3d.com/guides/compute/hops-component/)). None of the Player pages read describes re-opening a result to change its inputs ([Rhino help](https://docs.mcneel.com/rhino/8/help/en-us/commands/grasshopper.htm), [features page](https://www.rhino3d.com/features/grasshopper/player/)); users ask to "delete input geometry after" a run, which suggests each run is one-shot ([wish list](https://discourse.mcneel.com/t/grasshopper-player-custom-tools-wish-list/114844)).
- No form for Player: in April 2020, asked whether the RCP would integrate with GrasshopperPlayer, Steve Baer replied (paraphrased by the fetch tool) that definitions may be able to request an RCP-style UI when run as a command, not yet announced ([RCP wishes thread](https://discourse.mcneel.com/t/remote-control-panel-rcp-wishes-and-feedback/51545)). Forum.

**Numbers:**
| property | value | source |
|---|---|---|
| Time per Get prompt in one user's definition | 2-3 s each, 7 prompts | [forum, Jan 2022](https://discourse.mcneel.com/t/bake-with-attributes-via-gh-player/135996) |
| Hops recursion default | 10 nested levels | [Hops guide](https://developer.rhino3d.com/guides/compute/hops-component/) |
| Get "At Most" default | 1 (item access) | [Hops guide](https://developer.rhino3d.com/guides/compute/hops-component/) |

**Take for Studio:**
- Studio's Player already runs a flow from a form. Keep the form live (all inputs visible, preview while editing) and make "place as parametric object" the default end state, with "bake" as an explicit second step.

### Rhino.Compute, Hops and ShapeDiver configurators (looked at 2026-11-01)
**How it works:**
- Compute is "a stateless REST API running on Windows and Linux Servers" for the Rhino and Grasshopper SDKs ([Compute guides](https://developer.rhino3d.com/guides/compute/)).
- Hops reads a definition's Get components as inputs and Context Bake/Print as outputs; it can run async, cache in memory or on server, and parallelise per data-tree branch ([Hops guide](https://developer.rhino3d.com/guides/compute/hops-component/)).
- ShapeDiver turns Number Slider, Value List, Boolean Toggle, Color Swatch/Picker, Direct Text Input and Import components into web parameters. The component name becomes the label, "Canvas position sets parameter order", and native groups become accordion sections; groups named "hide..." hide inputs and "ignore..." drop them ([ShapeDiver inputs and outputs](https://help.shapediver.com/doc/inputs-and-outputs)).
- The ShapeDiver web panel has undo/redo for parameter changes, "Reload default values", and an optional validation mode where changes are pending until "Apply" ([ShapeDiver parameters](https://help.shapediver.com/doc/parameters)).
- App Builder layouts are also built from Grasshopper components: App, Container, Tab, Widget, Element; containers must be named "left", "right", "top" or "bottom" ([Build apps in Grasshopper](https://help.shapediver.com/doc/build-apps-in-grasshopper)). Visibility can depend on input and output values ([App Builder](https://help.shapediver.com/doc/shapediver-app-builder)).

**Good to use because:**
- Validation mode (batch edits, then Apply) is a good answer to slow solves ([ShapeDiver parameters](https://help.shapediver.com/doc/parameters)).
- Parameter undo/redo and reset-to-defaults in the panel ([same page](https://help.shapediver.com/doc/parameters)).

**Bad to use because:**
- Layout by naming convention and canvas position, not by a designer ([inputs and outputs](https://help.shapediver.com/doc/inputs-and-outputs)).
- App Builder has one template whose rules "will evolve frequently"; only parameter and export elements; theme editing is a manual workaround ([Build apps in Grasshopper](https://help.shapediver.com/doc/build-apps-in-grasshopper)).
- Hard compute caps: free plan 30 s (was 10 s) ([ShapeDiver blog, Jul 2025](https://shapediver.com/blog/what-we-got-wrong-about-shapediver-s-free-planand-how-we-fixed-it)).
- Compute bills uptime, not use ([core-hour billing](https://developer.rhino3d.com/guides/compute/core-hour-billing/)).

**Numbers:**
| property | value | source |
|---|---|---|
| ShapeDiver free plan max computation | 30 s (legacy 10 s) | [blog, Jul 23, 2025](https://shapediver.com/blog/what-we-got-wrong-about-shapediver-s-free-planand-how-we-fixed-it) |
| ShapeDiver free model size / export size | 10 MB / 10 MB (legacy 5 MB / none) | [same](https://shapediver.com/blog/what-we-got-wrong-about-shapediver-s-free-planand-how-we-fixed-it) |
| ShapeDiver credits | free under 10 s; "1 per complete 10-second chunk" | [credits](https://help.shapediver.com/doc/credits) |
| App Builder container names | 4 (left, right, top, bottom) | [Build apps](https://help.shapediver.com/doc/build-apps-in-grasshopper) |
| Rhino.Compute price | $0.10 per core per hour; 32 cores for 1 hour = $3.20 | [core-hour billing](https://developer.rhino3d.com/guides/compute/core-hour-billing/) |

**Take for Studio:**
- Copy the "Apply" (validation) mode and parameter-level undo/redo with "reset to defaults".
- Do not derive order or grouping from node position or group names; the form designer owns order.

### Rhino 8 Model Objects, blocks, Content Cache, and VisualARQ Grasshopper styles (looked at 2026-11-01)
**How it works:**
- Rhino 8 lets Grasshopper "Create block definitions and instances", keep object attributes, and "Update existing Rhino objects from Grasshopper" with Content Cache ([What's new in Rhino 8](https://www.rhino3d.com/8/new/), [Blocks](https://www.rhino3d.com/features/grasshopper/blocks/)).
- Content Cache exists because baking added copies each time and users "had to maintain copies" and delete before rebaking ([Content Cache page](https://www.rhino3d.com/features/grasshopper/content-cache/)).
- None of these pages says the baked block stays linked to its definition ([Blocks](https://www.rhino3d.com/features/grasshopper/blocks/), [blocks guide](https://www.rhino3d.com/docs/guides/grasshopper/blocks/)).
- The wish for a definition bound to a Rhino object, with parameters in a properties panel and "Grasshopper should not have to be opened", dates to 2017 ([forum, Mar 2017](https://discourse.mcneel.com/t/grasshopper-objects/42624)). Old (2017), forum.
- VisualARQ (third party plug-in) does this: a definition becomes an object style; each input is "Editable by" Definition (hidden), Object (per element, shown in Rhino's Properties panel) or Style ("changes will apply to all elements with that style"); outputs become blocks per representation (Model, Plan, Preview) ([VisualARQ tutorial, staging site](https://stg.visualarq.com/tutorial/grasshopper-styles/get-started)). Third party, staging URL.

**Good to use because:**
- Content Cache gives a push/pull link instead of delete and rebake; a user is "loving the egg crate Content Cache component" ([forum, Jul 2024](https://discourse.mcneel.com/t/egg-crate-makes-me-irate/181135?page=4)). Forum.
- VisualARQ's three-level "Editable by" split (definition, style, object) is a clean model for shared vs per-instance values ([VisualARQ tutorial](https://stg.visualarq.com/tutorial/grasshopper-styles/get-started)).

**Bad to use because:**
- With Model Objects, "more than a few elements" gives a "performance drop and everything slows down quite a bit"; Scott Davidson (scottd) replies "Performance is always an issue to consider" and that adding objects to a document has long been slow ([forum, Jul 2024](https://discourse.mcneel.com/t/egg-crate-makes-me-irate/181135?page=4)). Forum.
- Users felt "a bit lost" without documentation ([same thread](https://discourse.mcneel.com/t/egg-crate-makes-me-irate/181135?page=4)). Forum.
- Native Rhino still has no parametric object type driven by a definition; the closest is a third-party BIM plug-in ([forum, 2017](https://discourse.mcneel.com/t/grasshopper-objects/42624)).

**Numbers:**
| property | value | source |
|---|---|---|
| Age of "GH definition as Rhino object" request | Mar 29, 2017 | [forum](https://discourse.mcneel.com/t/grasshopper-objects/42624) |
| VisualARQ "Editable by" levels | 3 (Definition, Style, Object) | [VisualARQ tutorial](https://stg.visualarq.com/tutorial/grasshopper-styles/get-started) |
| VisualARQ representations per output block | 3 (Model, Plan, Preview) | [same](https://stg.visualarq.com/tutorial/grasshopper-styles/get-started) |

**Take for Studio:**
- Give every exposed input a scope: hidden, per style (shared definition), or per object. Show only per-object inputs on the selected object; show style inputs read-only with an "edit style" action.
- Keep the object linked; offer "Bake to plain shapes" as a separate, explicit command.

### Why the Grasshopper approach is weak for end users (synthesis, with evidence)
- **The UI is not a first-class object.** Windows are made from canvas components that share the logic graph ("made the script a bit messy") ([forum](https://discourse.mcneel.com/t/human-ui-vs-ui-your-thoughts-and-experiences-on-which-to-use/)); each control needs create, listen and set wiring ([Human UI source list](https://data.jsdelivr.com/v1/package/gh/andrewheumann/humanui@master/flat), [author advice](https://discourse.mcneel.com/t/human-ui-value-listener-live-update/)).
- **The native option stalled.** The RCP was called "the hardest dropped ball in Grasshopper history" and "stuck in like version 0.1" ([forum 2025](https://discourse.mcneel.com/t/the-future-of-grasshopper-user-interfaces/204466), [forum 2021](https://discourse.mcneel.com/t/remote-control-panel-rcp-wishes-and-feedback/51545)); in Sep 2026 "there isn't anything available to test" ([forum](https://discourse.mcneel.com/t/future-plans-for-a-more-robust-remote-control-panel-in-grasshopper-2/220904)).
- **Third-party UI breaks with the host.** Human UI failed under Rhino 8's .NET Core and later regressed through auto-update ([forum 2024](https://discourse.mcneel.com/t/grashopper-player-human-ui-not-working-rhino-8/), [forum 2026](https://discourse.mcneel.com/t/new-humanui-for-rhino-8-wip-for-testing/219339)).
- **No object in the drawing.** Player and bake produce dead geometry; the 2017 wish for definition-bound objects is still answered by third-party BIM plug-ins ([forum 2017](https://discourse.mcneel.com/t/grasshopper-objects/42624), [VisualARQ](https://stg.visualarq.com/tutorial/grasshopper-styles/get-started)).
- **Slow feedback.** Seconds of delay in Human UI and Player prompts ([forum](https://discourse.mcneel.com/t/un-used-windows-slow-the-definition-down/), [forum](https://discourse.mcneel.com/t/bake-with-attributes-via-gh-player/135996)).
- **Layout by convention.** Web configurators order inputs by canvas position and group names ([ShapeDiver](https://help.shapediver.com/doc/inputs-and-outputs)).

---

## Part B. Houdini

### Houdini Digital Assets and the Type Properties parameter editor (Houdini docs current, looked at 2026-11-01)
**How it works:**
- An asset is a custom node built from a network, stored in an `.hda` library; you can "put down multiple instances of the node" ([Intro to assets](https://www.sidefx.com/docs/houdini/assets/intro.html)).
- Instances are locked to the definition. Edits to the definition "affect every instance"; "Other instances of the same asset will get the same changes"; "Allow editing of contents" unlocks, "Match current definition" relocks ([Editing assets](https://www.sidefx.com/docs/houdini/assets/edit.html)).
- The interface is built by promoting parameters: drag a parameter or a whole node into the Type Properties parameter list, or use "Export Parameter to Type Properties" ([Asset UI](https://www.sidefx.com/docs/houdini/assets/asset_ui.html)). The editor has a "Create parameters" pane (From Nodes, By Type), an "Existing parameters" tree, and a "Parameter Description" pane ([Edit Parameter Interface](https://www.sidefx.com/docs/houdini/ref/windows/edit_parameter_interface.html)).
- Folders: Collapsible, Simple (boxed), Tabs, Radio buttons, Import Block, and Multiparm Block in List, Scrolling or Tabs style; "Disable when" and "Hide when" take rules like `{ type == 1 count > 10 } { tolerance < 0.1 }` (AND inside braces, OR between braces, 8 operators, spaces required) ([Type Properties window](https://www.sidefx.com/docs/houdini/ref/windows/optype.html)).
- Per parameter: tooltip ("Help"), range with lock icons, "Join to next", "Invisible", menus (static or script), callbacks, and tags such as `sidefx::slider` ([Type Properties window](https://www.sidefx.com/docs/houdini/ref/windows/optype.html), [Asset UI](https://www.sidefx.com/docs/houdini/assets/asset_ui.html)). The Help tab takes HTML or a wiki format "that looks like the native Houdini help" ([Type Properties](https://www.sidefx.com/docs/houdini/ref/windows/optype.html)).
- Presets: gear menu "Save Preset", per node type; bold values mark changes from defaults; "Revert to Defaults" per parameter or node ([Parameters](https://www.sidefx.com/docs/houdini/network/parms.html)).

**Good to use because:**
- One definition, many instances, central update ([Editing assets](https://www.sidefx.com/docs/houdini/assets/edit.html), [Intro](https://www.sidefx.com/docs/houdini/assets/intro.html)).
- Very complete form model: folders, multiparm lists, conditionals, ranges, tooltips, help page, presets in one place ([Type Properties](https://www.sidefx.com/docs/houdini/ref/windows/optype.html)).
- Bold "changed from default" plus per-field revert is a good, quiet pattern ([Parameters](https://www.sidefx.com/docs/houdini/network/parms.html)).

**Bad to use because:**
- Conditionals are a text mini-language with a whitespace trap: "You must put spaces around the comparison operator, otherwise Houdini will not accept the rule" ([Type Properties](https://www.sidefx.com/docs/houdini/ref/windows/optype.html)).
- The editor is dense; a SideFX developer said adding one more field to the "already rather full Type Properties Parameter page is liable to make things more intimidating and confusing" ([SideFX forum, Jun 2008](https://www.sidefx.com/forum/topic/11489/)). Old (2008).
- Layout is a tree list with property sheets, not a visual canvas; side-by-side needs a "Horizontally join to next parameter" checkbox ([Asset UI](https://www.sidefx.com/docs/houdini/assets/asset_ui.html)).

**Numbers:**
| property | value | source |
|---|---|---|
| Conditional comparison operators | 8 (`== != < > >= <= =~ !~`) | [Type Properties](https://www.sidefx.com/docs/houdini/ref/windows/optype.html) |
| Folder types | 5 plus Multiparm Block in 3 styles | [Type Properties](https://www.sidefx.com/docs/houdini/ref/windows/optype.html) |
| Type Properties tabs | 10 (Basic, Parameters, Node, Input/Output, Help, Code, Scripts, Interactive, Extra Files, Save) | [Type Properties](https://www.sidefx.com/docs/houdini/ref/windows/optype.html) |

**Take for Studio:**
- Copy the model (folders, list blocks, conditionals, help, presets, changed-from-default marking), not the editor. Build conditions with pickers (field, operator, value), shown as plain-language chips, and keep the text form as an advanced view.

### Houdini handles and viewer states bound to parameters (looked at 2026-11-01)
**How it works:**
- Handles are exported to the asset ("Export handle to digital asset") or created in the Handles tab; under Bindings each handle part maps to a promoted parameter ([Asset UI](https://www.sidefx.com/docs/houdini/assets/asset_ui.html)).
- Python viewer states can bind handles statically, e.g. `bindHandleStatic("xform", "start_handle", [("startx","tx"),...])`, or dynamically with callbacks `onHandleToState` and `onStateToHandle` ([State handles](https://www.sidefx.com/docs/houdini/hom/state_handles.html)).
- `onBeginHandleToState` / `onEndHandleToState` "are a natural place to open and close an undo block" ([State handles](https://www.sidefx.com/docs/houdini/hom/state_handles.html)).
- An asset names a default viewer state that the Handles tool uses; the code can be embedded in the asset ([Python states](https://www.sidefx.com/docs/houdini/hom/python_states.html)).
- Handle types include xform, boundingbox, distance, translate, pivot, circle, hudslider; settings include `hidewhen` ([State handles](https://www.sidefx.com/docs/houdini/hom/state_handles.html)).

**Good to use because:**
- Handles are data bound to parameters, so the form and the viewport edit the same value both ways ([State handles](https://www.sidefx.com/docs/houdini/hom/state_handles.html)).
- One drag is one undo step when wrapped in begin/end ([same](https://www.sidefx.com/docs/houdini/hom/state_handles.html)).

**Bad to use because:**
- Handles and HUD sliders show only with the Handles tool unless "Persistent" is turned on ([Asset UI](https://www.sidefx.com/docs/houdini/assets/asset_ui.html)).
- "Handles cannot be bound to nodeless states" and a state accepts one selection type at a time ([Python states](https://www.sidefx.com/docs/houdini/hom/python_states.html)).
- Dynamic handle values start at 0 and the state must seed them ([State handles](https://www.sidefx.com/docs/houdini/hom/state_handles.html)).

**Numbers:**
| property | value | source |
|---|---|---|
| Built-in handle types listed (sample) | xform, boundingbox, distance, translate, pivot, circle, sidefx_transform2d, hudslider, hudintslider and more | [State handles](https://www.sidefx.com/docs/houdini/hom/state_handles.html) |

**Take for Studio:**
- Let the object author bind grips to inputs (point, distance, angle, transform) with a static binding table; treat one grip drag as one undo step.

### Houdini Engine inside Maya, 3ds Max, Unreal and Unity (looked at 2026-11-01)
**How it works:**
- Engine is a plug-in for Maya, 3ds Max, Unity and Unreal; "Changes made to the core asset, even deep into production, will update all instantiations of the asset" ([Houdini Engine product page](https://www.sidefx.com/products/houdini-engine/)).
- Unreal: importing an HDA makes a HoudiniAsset whose `.uasset` "stores a copy of its binary contents"; dragging it into the level makes a HoudiniAssetActor; "Rebuild All Instances" updates every placed instance ([Unreal assets](https://www.sidefx.com/docs/houdini/unreal/assets.html)).
- Unreal parameters show in the Details panel; folders, ramps, multiparms (as arrays), Disable When, Hide When and Join to Next are supported; with "OnParameterChange" every change recooks ([Unreal parameters](https://www.sidefx.com/docs/houdini/unreal/parameters.html)).
- Maya: parameters become attributes on a `houdiniAsset` node; folders become collapsible frames; "Disable When and Hide When are not supported"; Radio folders and nested multiparms are not supported ([Maya parameters](https://www.sidefx.com/docs/maya/parameters.html)).
- Unity: Inspector shows parameters, float ramps become Animation Curves, colour ramps become Gradients, auto-cook optional ([Unity parameters](https://www.sidefx.com/docs/unity/parameters.html)).
- Baking: Unreal bakes outputs to "standalone Static Meshes" ([Unreal outputs](https://www.sidefx.com/docs/houdini/unreal/outputs.html)); Maya bake "disconnects all the outputs of an asset and unparents the child nodes" ([Maya bake](https://www.sidefx.com/docs/maya/bake.html)).

**Good to use because:**
- One asset authored once, shown in four hosts' native property panels ([product page](https://www.sidefx.com/products/houdini-engine/)).
- Repeated geometry becomes instanced static mesh components automatically when a packed primitive is copied more than once ([Unreal instancing](https://www.sidefx.com/docs/houdini/unreal/instancing.html)).

**Bad to use because:**
- Each host drops part of the authored UI silently: Maya ignores Disable/Hide When ([Maya parameters](https://www.sidefx.com/docs/maya/parameters.html)); Unreal supports only Transform and Bounds handles ([Unreal handles](https://www.sidefx.com/docs/houdini/unreal/handles.html)); Unity supports only Transformer handles ([Unity handles](https://www.sidefx.com/docs/unity/handles.html)).
- Menu scripts cannot generate items; mini menu and multi-select menus unsupported in Unreal and Maya ([Unreal parameters](https://www.sidefx.com/docs/houdini/unreal/parameters.html), [Maya parameters](https://www.sidefx.com/docs/maya/parameters.html)).
- "When you recook an asset, the HDA processes and updates whether you made changes or not" ([Unreal intro](https://www.sidefx.com/docs/houdini/unreal/intro.html)).

**Numbers:**
| property | value | source |
|---|---|---|
| Free Engine licences for Unreal/Unity | up to 10 per studio | [product page](https://www.sidefx.com/products/houdini-engine/) |
| Free Engine Indie | up to 3 computers | [product page](https://www.sidefx.com/products/houdini-engine/) |
| Unreal versions with binaries | UE5.8 and UE5.7 | [Unreal intro](https://www.sidefx.com/docs/houdini/unreal/intro.html) |
| Default numeric range if unset (Unreal) | 0 to 10 | [Unreal parameters](https://www.sidefx.com/docs/houdini/unreal/parameters.html) |
| Handle types supported: Unreal / Unity | 2 / 1 | [Unreal handles](https://www.sidefx.com/docs/houdini/unreal/handles.html), [Unity handles](https://www.sidefx.com/docs/unity/handles.html) |
| Foliage attachment search distance default | 1000 | [Unreal instancing](https://www.sidefx.com/docs/houdini/unreal/instancing.html) |

**Take for Studio:**
- Studio is the only host, so the object panel must render 100% of the form features (sections, show-when, lists, grips). No silent drops.
- Embed the definition in the drawing (like the `.uasset` copy) so files open without the library, with an explicit "update from library" action.

---

## Part C. Blender

### Geometry Nodes modifier panel and node group interface (Blender 5.2 LTS manual, looked at 2026-11-01)
**How it works:**
- A Geometry Nodes modifier points at a node group. Its inputs "can have unique values even if the group is shared among multiple modifiers" ([GN modifier](https://docs.blender.org/manual/en/latest/modeling/modifiers/geometry_nodes.html)).
- For a field input the modifier shows a toggle "between using a single value for the input or using an attribute on the input geometry"; output attributes can be named in the panel; node warnings appear in the panel ([GN modifier](https://docs.blender.org/manual/en/latest/modeling/modifiers/geometry_nodes.html)).
- The author edits the interface in the Group Sockets panel: inputs, outputs, panels (nestable, "Closed by Default"), panel toggles, per-socket Description (tooltip), Default, Min/Max, Subtype (Distance, Angle, Percentage...), Hide Value, "Hide in Modifier", expanded menus ([Node Groups](https://docs.blender.org/manual/en/latest/interface/controls/nodes/groups.html)).
- Visibility is inferred from the graph: Blender 4.4 "Input values that don't affect the output are grayed out"; Blender 4.5 added "Auto-hide inputs when their usage depends on a menu input" and panel toggles ([4.4 UI notes](https://developer.blender.org/docs/release_notes/4.4/user_interface/), [4.5 UI notes](https://developer.blender.org/docs/release_notes/4.5/user_interface/)). Menus come from the Menu Switch node (4.1) ([4.1 notes](https://developer.blender.org/docs/release_notes/4.1/nodes_physics/)).
- The same group can be a node-based tool; its inputs show in the Adjust Last Operation panel ([Node tools](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/tools.html)).

**Good to use because:**
- No separate rule language: unused inputs grey out and menu-dependent inputs hide automatically ([4.4](https://developer.blender.org/docs/release_notes/4.4/user_interface/), [4.5](https://developer.blender.org/docs/release_notes/4.5/user_interface/)).
- Units come from subtypes and scene units ([Node Groups](https://docs.blender.org/manual/en/latest/interface/controls/nodes/groups.html)).
- Single value or per-element attribute is one toggle ([GN modifier](https://docs.blender.org/manual/en/latest/modeling/modifiers/geometry_nodes.html)).

**Bad to use because:**
- "Min, Max ... This does not clamp the actual data flowing through the socket" ([Node Groups](https://docs.blender.org/manual/en/latest/interface/controls/nodes/groups.html)).
- "A panel toggle does not automatically disable or gray out its sockets" ([Node Groups](https://docs.blender.org/manual/en/latest/interface/controls/nodes/groups.html)).
- No free layout: order is the interface list; no columns, images or custom widgets ([Node Groups](https://docs.blender.org/manual/en/latest/interface/controls/nodes/groups.html)).
- Scripts could not read which modifier inputs were hidden until 5.2 (`is_input_visible`, `is_input_used`); recreating the panel elsewhere "still takes some adjustments and compromises" ([BlenderArtists, 2025 to 2026](https://blenderartists.org/t/how-can-i-detect-that-a-gn-modifier-input-is-hidden-due-to-a-menu-switch-inside/1615122)). Forum.

**Numbers:**
| property | value | source |
|---|---|---|
| Vector socket dimensions | 2, 3 or 4 | [Node Groups](https://docs.blender.org/manual/en/latest/interface/controls/nodes/groups.html) |
| Version that greys unused inputs | 4.4 | [4.4 UI notes](https://developer.blender.org/docs/release_notes/4.4/user_interface/) |
| Version that auto-hides menu-dependent inputs, adds panel toggles | 4.5 | [4.5 UI notes](https://developer.blender.org/docs/release_notes/4.5/user_interface/) |

**Take for Studio:**
- Studio's flow knows lineage. Use it: grey out inputs that cannot reach any output, and hide inputs behind an unchosen choice, automatically. Keep hand-written show-when rules for the rest.
- Make Min/Max a real clamp (or say clearly when it is only a slider range, like Unreal's UIMin vs ClampMin).

### Blender node-group gizmos (Blender 4.3+, looked at 2026-11-01)
**How it works:**
- Three gizmo nodes: Linear ("a scalar value with a linear movement"), Dial, and Transform ("a transform matrix value") ([4.3 notes](https://developer.blender.org/docs/release_notes/4.3/geometry_nodes/)).
- Gizmos attach to existing inputs; the author makes the gizmo position depend on the value so it works both ways ([Gizmos manual](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/gizmos.html)).
- Gizmos propagate through math nodes to group inputs and up to the modifier; then they "always show when the modifier is active" ([Gizmos manual](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/gizmos.html)).

**Good to use because:**
- Built from the same graph; one gizmo can drive several values at once ([Gizmos manual](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/gizmos.html)).

**Bad to use because:**
- "The main aspect that makes gizmos unintuitive at first is that there is a bidirectional dependency"; a naive setup "always jumps back to the origin" ([Gizmos manual](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/gizmos.html)).
- "Built-in nodes do not have their own gizmos yet" ([Gizmos manual](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/gizmos.html)).

**Numbers:**
| property | value | source |
|---|---|---|
| Gizmo node types | 3 (Linear, Dial, Transform) | [4.3 notes](https://developer.blender.org/docs/release_notes/4.3/geometry_nodes/) |

**Take for Studio:**
- Offer grips as a binding (grip type, anchor, bound input) rather than a node the author must wire in a loop; Studio computes the grip position from the value.

### Blender assets, Apply (bake), and instances (looked at 2026-11-01)
**How it works:**
- "Geometry nodes can also be dragged onto objects to add a Geometry Nodes Modifier" from the Asset Browser ([Asset Browser](https://docs.blender.org/manual/en/latest/editors/asset_browser.html)).
- Import method: Link (read-only, "Later changes to the asset file will be reflected in all files that link it"), Append (independent copy), or Pack ([Asset Browser](https://docs.blender.org/manual/en/latest/editors/asset_browser.html)).
- "Apply" makes the modifier "real" and deletes it; objects sharing data must first become single user ([Modifiers intro](https://docs.blender.org/manual/en/latest/modeling/modifiers/introduction.html)).
- Bake nodes and simulation bakes store intermediate geometry; the file must be saved first ([Baking](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/baking.html)).
- Instances are processed once per unique geometry, so a Subdivision node at the end subdivides "three meshes, rather than each instance" ([Instances](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/instances.html)).

**Good to use because:**
- Drag a tool from a library onto an object: a short path from library to parametric object ([Asset Browser](https://docs.blender.org/manual/en/latest/editors/asset_browser.html)).
- Link vs Append is an explicit choice of shared definition vs copy ([Asset Browser](https://docs.blender.org/manual/en/latest/editors/asset_browser.html)).

**Bad to use because:**
- "Only eight levels of nested instancing are supported for rendering and viewing in the viewport" ([Instances](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/instances.html)).
- Heavy scatter setups make the viewport "basically unusably slow"; one 3000 x 500 m plane caused about a minute of unresponsiveness and about 16.5 GB RAM ([BlenderArtists, 2022](https://blenderartists.org/t/geometry-nodes-slowing-down-blender/1377460)). Forum.
- Baked data across versions: "It's not guaranteed that data written with one Blender version can be read by another" ([Baking](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/baking.html)).

**Numbers:**
| property | value | source |
|---|---|---|
| Nested instancing depth for display | 8 levels | [Instances](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/instances.html) |
| One user's slow case | about 1 minute, about 16.5 GB vs 0.5 s for a 300 x 50 m plane | [BlenderArtists, 2022](https://blenderartists.org/t/geometry-nodes-slowing-down-blender/1377460) |
| Node speedups (examples) | Triangulate "30-100x" (4.4); Scale Elements "4-10x" (4.2) | [4.4 notes](https://developer.blender.org/docs/release_notes/4.4/geometry_nodes/), [4.2 notes](https://developer.blender.org/docs/release_notes/4.2/geometry_nodes/) |

**Take for Studio:**
- Library drag-and-drop should create a linked parametric object; "Make independent copy" and "Bake to plain shapes" are separate commands.
- Evaluate shared definitions once per unique input set, and let thousands of identical objects reuse one result.

---

## Part D. Unreal Engine

### Details panel, property metadata and customization (UE 5.x docs, looked at 2026-11-01)
**How it works:**
- Properties appear in the Details panel of the selected actor. Metadata shapes the UI: ClampMin/ClampMax ("may be entered"), EditCondition ("Names a boolean property... whether editing of this property is disabled"), InlineEditConditionToggle, DisplayName, DisplayPriority, MakeEditWidget ("exposed in the viewport as a movable widget") ([Metadata specifiers](https://dev.epicgames.com/documentation/en-us/unreal-engine/metadata-specifiers-in-unreal-engine)).
- A third-party reference adds UIMin (slider range, typing beyond is allowed), Units ("100f" converts in a Celsius field), EditConditionHides ("the property is hidden"), Category with "|" for nested folders, AdvancedDisplay, ToolTip, GetOptions for dynamic dropdowns ([Unreal Garden UPROPERTY](https://unreal-garden.com/docs/uproperty/)). Third party.
- Full customization is C++: `IDetailCustomization` with `CustomizeDetails`, `EditCategory`, `AddCustomRow` with Slate widgets, registered in an editor module; code order overrides header order ([Epic quickstart](https://dev.epicgames.com/documentation/unreal-engine/details-panel-quickstart-guide-for-unreal-engine), [community wiki](https://unrealcommunity.wiki/customizing-detail-panels-g529msrd)).

**Good to use because:**
- Declarative metadata on each field gives categories, ranges, units, conditions and tooltips with no UI code ([Metadata specifiers](https://dev.epicgames.com/documentation/en-us/unreal-engine/metadata-specifiers-in-unreal-engine), [Unreal Garden](https://unreal-garden.com/docs/uproperty/)).
- Two ranges: ClampMin (hard) and UIMin (slider only) ([Unreal Garden](https://unreal-garden.com/docs/uproperty/)).

**Bad to use because:**
- Metadata sprawl: 157 documented specifiers in 20 groups on one community page (measured below) ([Unreal Garden](https://unreal-garden.com/docs/uproperty/)).
- Anything beyond metadata needs C++ and Slate in an editor module ([Epic quickstart](https://dev.epicgames.com/documentation/unreal-engine/details-panel-quickstart-guide-for-unreal-engine)). The community wiki says there was "no current official documentation for this by Epic" ([community wiki, about 5 years old, legacy](https://unrealcommunity.wiki/customizing-detail-panels-g529msrd)). Old, third party.

**Numbers:**
| property | value | source |
|---|---|---|
| UPROPERTY specifier entries on Unreal Garden page | 157 entries (h3 headings) in 20 groups (h2), page dated 2024-11-24 | measured: curl the page, count `<h3 id=...>` and `<h2 id=...>` ([Unreal Garden](https://unreal-garden.com/docs/uproperty/)) |
| DisplayPriority top value | 1 | [Metadata specifiers](https://dev.epicgames.com/documentation/en-us/unreal-engine/metadata-specifiers-in-unreal-engine) |

**Take for Studio:**
- Keep a small, typed set of field properties (label, unit, hard range, slider range, step, tooltip, section, advanced, show-when, grip). A curated 15 beats 157 strings.

### Editor Utility Widgets and the UMG designer (looked at 2026-11-01)
**How it works:**
- Editor Utility Widgets are UMG Widget Blueprints that become custom editor tabs; run by right-click "Run Editor Utility Widget"; listed in the Tools menu ([Editor Utility Widgets](https://dev.epicgames.com/documentation/en-us/unreal-engine/editor-utility-widgets-in-unreal-engine)).
- The designer has Palette ("widgets, that you can drag into the Visual Designer"), Hierarchy, Visual Designer (opens at 1:1, Ctrl+wheel zoom), Details, Animations, and a Graph mode for logic ([Widget Blueprints](https://dev.epicgames.com/documentation/en-us/unreal-engine/widget-blueprints-in-umg-for-unreal-engine)).

**Good to use because:**
- This is the standard drag-and-drop designer layout (palette, tree, canvas, details) that users already know ([Widget Blueprints](https://dev.epicgames.com/documentation/en-us/unreal-engine/widget-blueprints-in-umg-for-unreal-engine)).

**Bad to use because:**
- Marked Beta: "use caution when shipping with it"; "The tab is only dockable with Level Editor tabs" ([Editor Utility Widgets](https://dev.epicgames.com/documentation/en-us/unreal-engine/editor-utility-widgets-in-unreal-engine)).
- It is a general UI builder: the author must wire every widget to data in the Graph tab, unlike the automatic Details panel ([Widget Blueprints](https://dev.epicgames.com/documentation/en-us/unreal-engine/widget-blueprints-in-umg-for-unreal-engine)).

**Numbers:**
| property | value | source |
|---|---|---|
| Designer panels | 5 (Palette, Hierarchy, Visual Designer, Details, Animations) | [Widget Blueprints](https://dev.epicgames.com/documentation/en-us/unreal-engine/widget-blueprints-in-umg-for-unreal-engine) |

**Take for Studio:**
- Use the four-pane designer layout (palette, outline, canvas, properties), but palette items should be "flow inputs" already bound to data, so placing one needs no wiring.

### Blueprint construction scripts as parametric actors (looked at 2026-11-01)
**How it works:**
- The Construction Script "runs following the Components list when an instance of a Blueprint Class is created"; examples: a fence that traces outward to find its length ([Construction Script](https://dev.epicgames.com/documentation/en-us/unreal-engine/construction-script-in-unreal-engine)).
- With "Run Construction Script on Drag" on, the script "Can execute dozens of times per second while dragging"; with it off, there is no live preview: "There is no middle ground" ([UE forum feature request, Jul 2026](https://forums.unrealengine.com/t/feature-request-configurable-construction-script-preview-update-rate-throttling/2739648)). Forum.
- Exposed variables can show a 3D widget in the viewport (MakeEditWidget) ([Metadata specifiers](https://dev.epicgames.com/documentation/en-us/unreal-engine/metadata-specifiers-in-unreal-engine)).

**Good to use because:**
- A placed actor is the parametric object; its exposed variables show in the Details panel; one Blueprint class is the shared definition ([Construction Script](https://dev.epicgames.com/documentation/en-us/unreal-engine/construction-script-in-unreal-engine)).

**Bad to use because:**
- No throttle; the request proposes caps of 60, 30, 15, 10 or 5 Hz and "Skip intermediate updates while a Construction Script is already running" ([UE forum, 2026](https://forums.unrealengine.com/t/feature-request-configurable-construction-script-preview-update-rate-throttling/2739648)). Forum.
- Dragging a 3D widget ignores the on-drag setting and "the construction script runs every frame"; some scripts "take several seconds" (Epic logged UE-27383) ([UE forum, Feb 2016](https://forums.unrealengine.com/t/348530)). Old (2016), forum.

**Numbers:**
| property | value | source |
|---|---|---|
| Re-runs while dragging | "dozens of times per second" | [UE forum, 2026](https://forums.unrealengine.com/t/feature-request-configurable-construction-script-preview-update-rate-throttling/2739648) |
| Suggested preview interval | 100 to 250 ms (5 to 10 updates/s) | [same](https://forums.unrealengine.com/t/feature-request-configurable-construction-script-preview-update-rate-throttling/2739648) |

**Take for Studio:**
- Re-solve on drag with a frame budget: skip intermediate values when a solve is running, always solve the final value on release, and show a light preview while dragging.

### PCG components (UE 5.x, looked at 2026-11-01)
**How it works:**
- A PCG component on an actor runs a PCG graph; trigger is GenerateOnLoad, GenerateOnDemand ("e.g. via Blueprint") or GenerateAtRuntime ([PCGComponentGenerationTrigger](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/PCGComponentGenerationTrigger)).
- "Is Partitioned" "Will partition the component in a grid, dispatching the generation to multiple local components"; `ClearPCGLink` moves generated resources to a new actor, "clearing all link to this PCG component" (the bake step) ([UPCGComponent API](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Plugins/PCG/UPCGComponent)).
- PCG Editor Mode (experimental) offers Draw Spline, Draw Spline Surface, Paint and Volume tools; "All the graph parameters that are exposed on the graph are available" under Parameter Overrides; if nothing is selected "an actor is created to perform the operation" ([PCG Editor Mode](https://dev.epicgames.com/documentation/en-us/unreal-engine/pcg-editor-mode-in-unreal-engine)).

**Good to use because:**
- Drawing tools that create a parametric actor from a gesture (spline, area, paint) are close to urban design work ([PCG Editor Mode](https://dev.epicgames.com/documentation/en-us/unreal-engine/pcg-editor-mode-in-unreal-engine)).
- Explicit generation triggers and an explicit "clear link" bake ([API](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Plugins/PCG/UPCGComponent)).

**Bad to use because:**
- Editor Mode is Experimental ([PCG Editor Mode](https://dev.epicgames.com/documentation/en-us/unreal-engine/pcg-editor-mode-in-unreal-engine)).
- Overview pages give little detail; most behaviour is only in API pages ([PCG framework page](https://dev.epicgames.com/documentation/en-us/unreal-engine/procedural-content-generation-framework-in-unreal-engine)).

**Numbers:**
| property | value | source |
|---|---|---|
| Generation triggers | 3 | [PCGComponentGenerationTrigger](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/PCGComponentGenerationTrigger) |
| Editor Mode tools | 4 (Draw Spline, Draw Spline Surface, Paint, Volume) | [PCG Editor Mode](https://dev.epicgames.com/documentation/en-us/unreal-engine/pcg-editor-mode-in-unreal-engine) |

**Take for Studio:**
- Let a library flow declare its "placement gesture" (click point, draw polyline, draw closed area, pick existing shapes). The Player then becomes a drawing tool that leaves a parametric object.

---

## Part E. Vectorworks Marionette

### Marionette objects in the drawing (Vectorworks 2026 help, looked at 2026-11-01)
**How it works:**
- Wrap a network, then "Convert to Object Node"; the object node "take[s] the form of the product of their executed script" ([Using object nodes 2026](https://app-help.vectorworks.net/2026/eng/VW2026_Guide/Marionette/Using%20object_nodes.htm), [Create a Marionette Object 2017](https://app-help.vectorworks.net/2017/eng/VW2017_Guide/Marionette/Step_5_Create_a_Marionette_Object.htm)).
- Parameters: "Named input nodes appear as fields on the Object Info palette"; "Prefix an input node name with a number to make it appear in a desired order"; "The prefixed number does not display" ([Marionette Networks 2017](https://app-help.vectorworks.net/2017/eng/VW2017_Guide/Marionette/Marionette_Networks.htm)). Old (2017).
- Grips: add Control Point 2D/3D nodes before conversion; then drag handles in plan and 3D ([Using object nodes 2026](https://app-help.vectorworks.net/2026/eng/VW2026_Guide/Marionette/Using%20object_nodes.htm)).
- Re-run: "Reset On Move" re-runs on every move; when off it re-runs only on parameter change, "which saves time with complex objects"; "Update" refreshes objects tied to worksheets or lists ([Using object nodes 2026](https://app-help.vectorworks.net/2026/eng/VW2026_Guide/Marionette/Using%20object_nodes.htm)).
- Shared definition: styles; "Editing a style changes all instances in the file that use the style"; by-instance parameters editable in the Object Info palette, by-style shown read-only, "Hide style parameters" option ([Editing Marionette objects 2026](https://app-help.vectorworks.net/2026/eng/VW2026_Guide/Marionette/Editing_Marionette_objects.htm), [object properties 2023](https://app-help.vectorworks.net/2023/eng/VW2023_Guide/Marionette/Marionette_object_properties.htm)).

**Good to use because:**
- The object is a normal drawing object with its parameters in the standard property palette; this is the shape Studio wants ([Editing Marionette objects](https://app-help.vectorworks.net/2026/eng/VW2026_Guide/Marionette/Editing_Marionette_objects.htm)).
- Style vs instance split, like VisualARQ ([same](https://app-help.vectorworks.net/2026/eng/VW2026_Guide/Marionette/Editing_Marionette_objects.htm)).
- A user article: values change "without rebuilding the model", and a saved object is reusable in other files ([AECbytes, Jul 2017](https://aecbytes.com/tipsandtricks/2017/issue78-marionette.html)). Old, third party.

**Bad to use because:**
- No form designer: order by number prefixes in node names, label equals node name ([Marionette Networks 2017](https://app-help.vectorworks.net/2017/eng/VW2017_Guide/Marionette/Marionette_Networks.htm)).
- Grips must be planned before conversion ([Using object nodes](https://app-help.vectorworks.net/2026/eng/VW2026_Guide/Marionette/Using%20object_nodes.htm)).
- Styled objects "can be edited only from the Plug-in Object Style dialog box" ([object properties 2023](https://app-help.vectorworks.net/2023/eng/VW2023_Guide/Marionette/Marionette_object_properties.htm)).
- Names over 32 characters are truncated ([Using object nodes](https://app-help.vectorworks.net/2026/eng/VW2026_Guide/Marionette/Using%20object_nodes.htm)).

**Numbers:**
| property | value | source |
|---|---|---|
| Object name limit | 32 characters | [Using object nodes 2026](https://app-help.vectorworks.net/2026/eng/VW2026_Guide/Marionette/Using%20object_nodes.htm) |
| Ways to set parameter order | 1 (number prefix in node name) | [Marionette Networks 2017](https://app-help.vectorworks.net/2017/eng/VW2017_Guide/Marionette/Marionette_Networks.htm) |

**Take for Studio:**
- Copy the end state (object in drawing, parameters in the normal property panel, style vs instance, "re-run on move" switch) but replace naming tricks with a real form designer.

---

## Part F. Cross-tool view: how the object lives in the drawing

| Tool | Selection shows params in | Grips / handles | Re-run on edit | Undo | Shared definition vs copies | Bake | Performance notes |
|---|---|---|---|---|---|---|---|
| Grasshopper Player | no object; prompts only ([Rhino help](https://docs.mcneel.com/rhino/8/help/en-us/commands/grasshopper.htm)) | none | per prompt ([forum](https://discourse.mcneel.com/t/bake-with-attributes-via-gh-player/135996)) | not documented in pages read | definition file on disk ([Rhino help](https://docs.mcneel.com/rhino/8/help/en-us/commands/grasshopper.htm)) | Context Bake only ([Hops guide](https://developer.rhino3d.com/guides/compute/hops-component/)) | 2-3 s per prompt in one case |
| Rhino 8 Content Cache | objects in model, logic in GH ([page](https://www.rhino3d.com/features/grasshopper/content-cache/)) | none native | push from GH | not documented | GH definition | objects are already baked | slow with "more than a few elements" ([forum](https://discourse.mcneel.com/t/egg-crate-makes-me-irate/181135?page=4)) |
| VisualARQ GH styles (3rd party) | Rhino Properties panel ([tutorial](https://stg.visualarq.com/tutorial/grasshopper-styles/get-started)) | insert point/path | on parameter edit | not documented | style shared, object values per element | outputs are blocks | not documented |
| Houdini HDA | parameter editor ([edit](https://www.sidefx.com/docs/houdini/assets/edit.html)) | bound handles ([asset UI](https://www.sidefx.com/docs/houdini/assets/asset_ui.html)) | on change | begin/end undo blocks ([handles](https://www.sidefx.com/docs/houdini/hom/state_handles.html)) | .hda definition, locked instances | n/a in Houdini | |
| Houdini Engine Unreal | Details panel ([params](https://www.sidefx.com/docs/houdini/unreal/parameters.html)) | Transform, Bounds only ([handles](https://www.sidefx.com/docs/houdini/unreal/handles.html)) | OnParameterChange | not documented | `.uasset` copy + Rebuild All Instances ([assets](https://www.sidefx.com/docs/houdini/unreal/assets.html)) | to standalone Static Meshes ([outputs](https://www.sidefx.com/docs/houdini/unreal/outputs.html)) | instancers when copied more than once ([instancing](https://www.sidefx.com/docs/houdini/unreal/instancing.html)) |
| Blender GN modifier | modifier panel ([modifier](https://docs.blender.org/manual/en/latest/modeling/modifiers/geometry_nodes.html)) | gizmo nodes ([gizmos](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/gizmos.html)) | live | "Bake caches are no longer lost after undo" (4.1) ([4.1 notes](https://developer.blender.org/docs/release_notes/4.1/nodes_physics/)) | node group shared, inputs per modifier; Link vs Append ([assets](https://docs.blender.org/manual/en/latest/editors/asset_browser.html)) | Apply ([modifiers](https://docs.blender.org/manual/en/latest/modeling/modifiers/introduction.html)) | 8 nesting levels ([instances](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/instances.html)) |
| Unreal Blueprint actor | Details panel | MakeEditWidget ([metadata](https://dev.epicgames.com/documentation/en-us/unreal-engine/metadata-specifiers-in-unreal-engine)) | Construction Script, on drag optional | not documented in pages read | Blueprint class | n/a | dozens of runs/s on drag ([forum](https://forums.unrealengine.com/t/feature-request-configurable-construction-script-preview-update-rate-throttling/2739648)) |
| Unreal PCG | Details / Tool settings ([editor mode](https://dev.epicgames.com/documentation/en-us/unreal-engine/pcg-editor-mode-in-unreal-engine)) | spline/volume tools | per trigger ([enum](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/PCGComponentGenerationTrigger)) | not documented | PCG graph asset | ClearPCGLink ([API](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Plugins/PCG/UPCGComponent)) | partitioned grid |
| Marionette object | Object Info palette ([edit](https://app-help.vectorworks.net/2026/eng/VW2026_Guide/Marionette/Editing_Marionette_objects.htm)) | Control Point nodes ([object nodes](https://app-help.vectorworks.net/2026/eng/VW2026_Guide/Marionette/Using%20object_nodes.htm)) | on parameter change; optional on move | not documented | styles | not documented in pages read | Reset On Move off "saves time" |

## Part G. Patterns worth copying into Studio (summary)
- **One object, one definition, three scopes**: hidden / per style / per object (VisualARQ, Marionette styles) ([VisualARQ](https://stg.visualarq.com/tutorial/grasshopper-styles/get-started), [Marionette](https://app-help.vectorworks.net/2026/eng/VW2026_Guide/Marionette/Editing_Marionette_objects.htm)).
- **Definition embedded in the drawing with explicit update from the library** (Houdini Engine `.uasset` copy and "Rebuild All Instances") ([Unreal assets](https://www.sidefx.com/docs/houdini/unreal/assets.html)); Blender's Link vs Append choice ([Asset Browser](https://docs.blender.org/manual/en/latest/editors/asset_browser.html)).
- **Inferred visibility** from the graph (Blender 4.4/4.5) plus authored show-when rules (Houdini) ([4.4](https://developer.blender.org/docs/release_notes/4.4/user_interface/), [4.5](https://developer.blender.org/docs/release_notes/4.5/user_interface/), [Houdini](https://www.sidefx.com/docs/houdini/ref/windows/optype.html)).
- **Grips as bindings to inputs**, one drag = one undo step ([Houdini handles](https://www.sidefx.com/docs/houdini/hom/state_handles.html)).
- **Changed-from-default marking, per-field revert, presets** ([Houdini parms](https://www.sidefx.com/docs/houdini/network/parms.html)); **Apply mode** for slow flows ([ShapeDiver](https://help.shapediver.com/doc/parameters)).
- **Throttled live re-solve** on drag; final solve on release ([UE forum](https://forums.unrealengine.com/t/feature-request-configurable-construction-script-preview-update-rate-throttling/2739648), [Human UI 50 ms debounce](https://github.com/andrewheumann/humanui/pull/9)).
- **Bake is explicit and separate** (Blender Apply, PCG ClearPCGLink, Maya bake) ([Blender](https://docs.blender.org/manual/en/latest/modeling/modifiers/introduction.html), [PCG](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Plugins/PCG/UPCGComponent), [Maya](https://www.sidefx.com/docs/maya/bake.html)).
- **Drag from library onto the drawing** creates the parametric object (Blender) ([Asset Browser](https://docs.blender.org/manual/en/latest/editors/asset_browser.html)); **placement gestures** (PCG Editor Mode) ([PCG](https://dev.epicgames.com/documentation/en-us/unreal-engine/pcg-editor-mode-in-unreal-engine)).

## Not verified (blocked or empty)
- food4rhino.com app pages for Human UI and Synapse: HTTP 405. www2.food4rhino.com: DNS blocked in this session.
- forum.vectorworks.net and developer.vectorworks.net: HTTP 403. The 2026 Marionette "Naming nodes" page: HTTP 403 (used the 2017 page instead).
- dev.epicgames.com pages that rendered empty: Details panel customization, UPROPERTY specifiers, AActor::OnConstruction, bRunConstructionScriptOnDrag, UMG UI designer user guide, PCG overview body. Epic's JSON API returned a Cloudflare challenge (HTTP 403).
- issues.unrealengine.com UE-294736 (PCG overrides lost on copy): HTTP 403. Not used.
- Unreal Answers thread on Blueprint-only detail customization: only seen in a search summary, not opened. Treat as unverified.
- developer.rhino3d.com Grasshopper Player guide: HTTP 404. rhino3d.com model-objects feature page: HTTP 404. ShapeDiver model-limits page: HTTP 404.
- visualarq.com live tutorial and news pages: HTTP 404; used the staging copy (stg.visualarq.com).
- codeload.github.com and the GitHub API for the Human UI repo: HTTP 403 (used jsDelivr instead).
- No official source found on whether Blender evaluates identical Geometry Nodes modifiers once or once per object.
