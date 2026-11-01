# R21B notes: the code editor for a Python and C# script node (report C21)

Read on 2026-11-01. Studio context: Avalonia 12, .NET 10, Native AOT, Windows first.

How I measured (used in the Numbers tables as "measured M1" and so on):
- **M1**: NuGet search API, for example `https://azuresearch-usnc.nuget.org/query?q=packageid:Avalonia.AvaloniaEdit&prerelease=true`, field `totalDownloads` (all versions), on 2026-11-01.
- **M2**: NuGet registration API, for example `https://api.nuget.org/v3/registration5-gz-semver2/avalonia.avaloniaedit/index.json`, fields `published` and `licenseExpression`.
- **M3**: downloaded the `.nupkg` from `https://api.nuget.org/v3-flatcontainer/<id>/<ver>/<id>.<ver>.nupkg`, unzipped it, and byte-searched the `lib/net10.0` DLL for names (for example `IsAotCompatible`, `IsTrimmable`, `AutomationPeer`, `RectangleSelection`, `Minimap`). .NET 10 writes `IsAotCompatible` as assembly metadata ([Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/)), so absence means the author did not mark the library.
- **M4**: PyPI JSON API `https://pypi.org/pypi/<name>/json` for version, licence, upload date and Windows wheel size.
- **M5**: `https://pypistats.org/api/packages/<name>/recent` for downloads in the last month (third party).
- **M6**: npm registry `https://registry.npmjs.org/monaco-editor/latest`, plus the tarball unpacked and sized with `du -sh`.
- **M7**: grep of Roslyn's `PublicAPI.Shipped.txt` files on GitHub `main` (raw.githubusercontent.com).

---

## Part 1. What a script-node editor needs (how others do it)

### Rhino 8 ScriptEditor and the Grasshopper Script component (docs updated 2024-12-11 and 2026-09-29)
**How it works:**
- One editor for Python 3 and C#, with word completion, "signature completion" that tracks the current argument, optional snippet and word-based completion, a minimap (off by default), indentation guides and lint squiggles ([Editing Features](https://developer.rhino3d.com/guides/scripting/editor-editing/)).
- A Problems panel "lists the problems found in your script as you type", errors only by default, with toggles for warnings and info; run-time errors go to the Terminal instead ([Problems](https://developer.rhino3d.com/guides/scripting/editor-problems/)).
- The Terminal "shows printed output of last executed script", captured and shown at once by default, with a "Line by Line" toggle and auto-clear before each run ([Terminal](https://developer.rhino3d.com/guides/scripting/editor-terminal/)).
- In Grasshopper, an `out` output "captures anything that the script prints", one item per printed line, and can be removed for a small speed gain ([Grasshopper Scripting: Python](https://developer.rhino3d.com/guides/scripting/scripting-gh-python)).
- Inputs and outputs are named parameters with Type Hints; the generated `RunScript` signature "is going to include all the component inputs and outputs by their name and data type" ([same page](https://developer.rhino3d.com/guides/scripting/scripting-gh-python)).
- A real debugger for Python and C#: gutter breakpoints, step over/into/out, Variables panel with pinning, Call Stack, break on exceptions ([Debugging](https://developer.rhino3d.com/guides/scripting/editor-debug/), [Script Component](https://developer.rhino3d.com/guides/scripting/scripting-component/)).

**Good to use because:**
- Typed, named inputs make completion of the node's inputs possible, because the editor knows each name and type ([Grasshopper Scripting: Python](https://developer.rhino3d.com/guides/scripting/scripting-gh-python)).
- Print capture is a first-class output, so print debugging works inside a graph without a console ([same page](https://developer.rhino3d.com/guides/scripting/scripting-gh-python)).
- McNeel ships `.pyi` stubs of its .NET API on PyPI so outside editors can complete it ([mcneel/pythonstubs](https://github.com/mcneel/pythonstubs), [PyPI Rhino-stubs](https://pypi.org/pypi/Rhino-stubs/json)).

**Bad to use because:**
- Users report a slow first open: "on not-so-recent hardware the script editor is really slow to open", "It takes some-many whole seconds" (user post, Jan 2024, [McNeel forum](https://discourse.mcneel.com/t/rhino-8-grasshopper-script-editor-design-feedback/163513/113)).
- Completion stopped after a dot in SR13 (bug RH-84233, fixed in SR14), and `(` no longer commits a completion; only Tab does, "removed intentionally because it caused problems" (McNeel staff, Oct 2024, [forum](https://discourse.mcneel.com/t/bug-script-editor-autocomplete-woes/192771)).
- Missing return types and descriptions in completion lists and odd ranking ("m.close" returns "CollapseFa.." before "IsClosed") (user, Jan 2024, [forum](https://discourse.mcneel.com/t/rhino-8-grasshopper-script-editor-design-feedback/163513/113)).
- Python signature help came late; in Dec 2023 staff said "We have a ticket to get that fixed and provide method signature help" ([forum](https://discourse.mcneel.com/t/c-auto-complete-in-grasshopper-rhino-8/170455)).

**Numbers:**
| property | value | source |
|---|---|---|
| Minimap default | off | [Editing Features](https://developer.rhino3d.com/guides/scripting/editor-editing/) |
| Problems panel default | errors only | [Problems](https://developer.rhino3d.com/guides/scripting/editor-problems/) |
| Terminal default | cleared before each run | [Terminal](https://developer.rhino3d.com/guides/scripting/editor-terminal/) |
| Fix for "completion stops after dot" | Rhino 8 SR14 | [forum](https://discourse.mcneel.com/t/bug-script-editor-autocomplete-woes/192771) |
| Rhino-stubs on PyPI | 7.7.21140, uploaded 2021-05-24 (old, 5 years) | measured M4, [PyPI](https://pypi.org/pypi/Rhino-stubs/json) |

**Take for Studio:**
- Copy the contract: named, typed inputs and outputs, a print pane per node run, and an optional `out`-style output for printed lines.
- Make completion fast on first open (warm the language server in the background) and let users choose commit keys (Tab, Enter, `(`).

### Dynamo Python Script node editor (DynamoDS/Dynamo master, read 2026-11-01)
**How it works:**
- The editor is a WPF AvalonEdit `TextEditor` in a separate window with Run, zoom, undo and "convert tabs to spaces" buttons ([ScriptEditorWindow.xaml](https://raw.githubusercontent.com/DynamoDS/Dynamo/master/src/Libraries/PythonNodeModelsWpf/ScriptEditorWindow.xaml), [csproj](https://raw.githubusercontent.com/DynamoDS/Dynamo/master/src/Libraries/PythonNodeModelsWpf/PythonNodeModelsWpf.csproj)).
- Highlighting uses an `.xshd` file; folding uses a tab-based folding strategy; completion uses AvalonEdit's `CompletionWindow` ([ScriptEditorWindow.xaml.cs](https://raw.githubusercontent.com/DynamoDS/Dynamo/master/src/Libraries/PythonNodeModelsWpf/ScriptEditorWindow.xaml.cs)).
- The completion engine is found at run time by scanning every loaded assembly and calling `Activator.CreateInstance` on each provider type ([SharedCompletionProvider.cs](https://raw.githubusercontent.com/DynamoDS/Dynamo/master/src/Libraries/PythonNodeModelsWpf/SharedCompletionProvider.cs)).
- Inputs arrive as a positional `IN` array; the result is whatever you assign to `OUT`; you "Click Run then Save" ([Dynamo Primer, Python Nodes](https://primer2.dynamobim.org/8_coding_in_dynamo/8-3_python/1-python.md)).

**Good to use because:**
- Very simple mental model, and a Run button inside the editor gives on-demand runs ([Primer](https://primer2.dynamobim.org/8_coding_in_dynamo/8-3_python/1-python.md)).
- Proves AvalonEdit (the WPF parent of AvaloniaEdit) is enough for a shipping CAD script editor ([csproj](https://raw.githubusercontent.com/DynamoDS/Dynamo/master/src/Libraries/PythonNodeModelsWpf/PythonNodeModelsWpf.csproj)).

**Bad to use because:**
- Since Dynamo 2.13, IntelliSense "works only with the CPython engine and only if you execute the import code first", and module contents may be stale (forum, Jan 2023, [thread](https://forum.dynamobim.com/t/intellisense-for-python/85040)).
- No built-in debugger: Dynamo's own docs suggest "Implement a debugger, for example, using sys.settrace()" when line numbers are missing ([Primer, obstacles](https://primer2.dynamobim.org/1_developer_primer_intro/0-introduction/4-obstacles-and-workaround.md)); a user built a tool that extracts Python nodes to files for VS Code debugging (third party, Jun 2025, [forum](https://forum.dynamobim.com/t/simplify-debugging-python-nodes-in-dynamo/110955)).
- Untyped `IN[0]` gives the editor no name or type to complete ([Primer](https://primer2.dynamobim.org/8_coding_in_dynamo/8-3_python/1-python.md)).
- Users copy code between VS Code and Dynamo by hand; one found writing and debugging inside Dynamo slow (user posts, 2022 to 2023, [forum](https://forum.dynamobim.com/t/coding-python-nodes-for-dynamo-for-civil-3d-in-an-external-ide/77337)).

**Numbers:**
| property | value | source |
|---|---|---|
| Editor component | ICSharpCode.AvalonEdit (WPF) | [csproj](https://raw.githubusercontent.com/DynamoDS/Dynamo/master/src/Libraries/PythonNodeModelsWpf/PythonNodeModelsWpf.csproj) |
| AvalonEdit (WPF) latest | 6.3.1.120, 2025-04-13, MIT, 18,384,692 downloads | measured M1, M2 |
| Completion needs a prior run | yes (CPython engine, Dynamo 2.13+) | [forum](https://forum.dynamobim.com/t/intellisense-for-python/85040) |

**Take for Studio:**
- Do completion statically (stubs plus a language server), never only from a live interpreter after a run.
- Use named, typed inputs, not an `IN` array.

### Houdini code fields and wrangles (docs read 2026-11-01)
**How it works:**
- Code lives in a parameter's multi-line field; "press Ctrl + Enter to 'commit' the changes and update Houdini" ([VEX snippets](https://www.sidefx.com/docs/houdini/vex/snippets.html)).
- Alt + E opens the text in an external editor set by `$EDITOR` ([Parameters](https://www.sidefx.com/docs/houdini/network/parms.html)).
- A wrangle runs the snippet over every point, primitive or vertex, set by "Run Over" ([Attribute Wrangle](https://www.sidefx.com/docs/houdini/nodes/sop/attribwrangle.html)).

**Good to use because:**
- Explicit commit (Ctrl+Enter) avoids re-cooking on every keystroke ([VEX snippets](https://www.sidefx.com/docs/houdini/vex/snippets.html)).
- The code sits in the node itself, so it travels with the file ([Parameters](https://www.sidefx.com/docs/houdini/network/parms.html)).

**Bad to use because:**
- The official pages I read do not mention autocomplete, inline errors or find/replace for these fields ([Parameters](https://www.sidefx.com/docs/houdini/network/parms.html), [VEX snippets](https://www.sidefx.com/docs/houdini/vex/snippets.html)); not verified for other pages.
- Users pay for third-party editors that add autocomplete and "help and error messages as tooltips" (EVE, $19 per year or $30 perpetual, Dec 2025, [SideFX forum](https://www.sidefx.com/forum/topic/102715/lofi/), third party).
- The external-editor link is fragile: the hotkey only works with the mouse over the right label, and saves sometimes did not reach Houdini (user posts, 2021, [SideFX forum](https://www.sidefx.com/forum/topic/78429/)).

**Numbers:**
| property | value | source |
|---|---|---|
| Commit shortcut | Ctrl + Enter | [VEX snippets](https://www.sidefx.com/docs/houdini/vex/snippets.html) |
| External editor shortcut | Alt + E | [Parameters](https://www.sidefx.com/docs/houdini/network/parms.html) |
| Third-party EVE price | $19 / year or $30 perpetual | [forum](https://www.sidefx.com/forum/topic/102715/lofi/) |

**Take for Studio:**
- Offer an explicit "apply and run" key (Ctrl+Enter) next to optional live run.
- Do not rely on an external editor round trip; if offered, sync through a watched file with a clear status.

### VS Code editor conventions and accessibility (docs read 2026-11-01)
**How it works:**
- Multi-cursor with Alt+Click, Ctrl+Alt+Up/Down and Ctrl+D; column selection with Shift+Alt+drag; find with match case, whole word and regex, and replace with preserve case; fold with Ctrl+Shift+[; Format Document with Shift+Alt+F; `editor.formatOnSave` is off by default ([Basic Editing](https://code.visualstudio.com/docs/editing/codebasics)).
- Screen readers are tested with NVDA, JAWS, VoiceOver and Orca, using "a strategy based on text pagination"; F8 moves to the next problem and the reader announces it; Ctrl+M toggles whether Tab moves focus ([Accessibility](https://code.visualstudio.com/docs/configure/accessibility/accessibility)).
- Accessibility signals play sounds when the current line has "errors, warnings, breakpoints" ([Accessibility](https://code.visualstudio.com/docs/configure/accessibility/accessibility)).
- For code embedded in another document, a "virtual document" blanks out other content with whitespace so positions need no mapping ([Embedded Programming Languages](https://code.visualstudio.com/api/language-extensions/embedded-languages)).

**Good to use because:**
- These keys are what most script users already know ([Basic Editing](https://code.visualstudio.com/docs/editing/codebasics)).
- F8 plus Ctrl+M are a cheap, proven accessibility baseline for any editor ([Accessibility](https://code.visualstudio.com/docs/configure/accessibility/accessibility)).

**Bad to use because:**
- Copying all of VS Code (command palette, extensions) is far more than a node editor needs; Monaco itself does not run VS Code extensions ([monaco-editor](https://github.com/microsoft/monaco-editor)).

**Numbers:**
| property | value | source |
|---|---|---|
| Screen readers tested | NVDA, JAWS, VoiceOver, Orca | [Accessibility](https://code.visualstudio.com/docs/configure/accessibility/accessibility) |
| Zoom step | 20 percent | [Accessibility](https://code.visualstudio.com/docs/configure/accessibility/accessibility) |
| Format on save default | off | [Basic Editing](https://code.visualstudio.com/docs/editing/codebasics) |

**Take for Studio:**
- Use VS Code's default keys for multi-cursor, find, fold and format, and F8 / Shift+F8 for problems.
- Build the node's "prelude" (typed inputs) as a hidden virtual document in front of the user's code.

### Jupyter kernel protocol (messaging spec, read 2026-11-01)
**How it works:**
- Code runs on demand per cell; printed text comes back as `stream` messages named `stdout` or `stderr` ([Messaging](https://jupyter-client.readthedocs.io/en/latest/messaging.html)).
- Errors come back as an `error` message with name, value and traceback; results as `execute_result` with an `execution_count` ([Messaging](https://jupyter-client.readthedocs.io/en/latest/messaging.html)).
- Completion is asked of the running kernel (`complete_request` with `cursor_pos`; reply has `matches`, `cursor_start`, `cursor_end`) ([Messaging](https://jupyter-client.readthedocs.io/en/latest/messaging.html)).
- IPython's completer uses Jedi when installed and can also evaluate dotted names and call `dir()` on live objects ([IPython completer](https://ipython.readthedocs.io/en/stable/api/generated/IPython.core.completer.html)).

**Good to use because:**
- A clean, proven split of stdout, stderr, result and error, with a run counter ([Messaging](https://jupyter-client.readthedocs.io/en/latest/messaging.html)).

**Bad to use because:**
- Completion on live objects can execute code (attribute lookups) ([IPython completer](https://ipython.readthedocs.io/en/stable/api/generated/IPython.core.completer.html)).

**Numbers:**
| property | value | source |
|---|---|---|
| Output channels | stdout, stderr (stream), display_data, execute_result, error | [Messaging](https://jupyter-client.readthedocs.io/en/latest/messaging.html) |

**Take for Studio:**
- Shape the console pane like Jupyter: per run, show stdout, stderr and the error with traceback, stamped with a run number.

### Feature checklist for Studio's script-node editor (synthesis of the above)
**How it works (what the references ship):**
- Highlighting, completion of members, signature help, lint squiggles and a problems list ([Rhino Editing](https://developer.rhino3d.com/guides/scripting/editor-editing/), [Rhino Problems](https://developer.rhino3d.com/guides/scripting/editor-problems/)).
- A console that captures print per run ([Rhino Terminal](https://developer.rhino3d.com/guides/scripting/editor-terminal/), [Jupyter](https://jupyter-client.readthedocs.io/en/latest/messaging.html)).
- Find and replace with regex, multi-cursor, folding, format, minimap ([VS Code](https://code.visualstudio.com/docs/editing/codebasics), [Rhino](https://developer.rhino3d.com/guides/scripting/editor-editing/)).
- Run on demand (Run button, Ctrl+Enter) as well as recompute on input change ([Houdini](https://www.sidefx.com/docs/houdini/vex/snippets.html), [Dynamo](https://primer2.dynamobim.org/8_coding_in_dynamo/8-3_python/1-python.md)).
- Breakpoints and a variables view (Rhino only among the CAD tools) ([Rhino Debugging](https://developer.rhino3d.com/guides/scripting/editor-debug/)).

**Good to use because:**
- Each item is already expected by users of Rhino, Dynamo and VS Code (sources above).

**Bad to use because:**
- A full debugger is the most expensive item, and Dynamo ships without one ([Primer](https://primer2.dynamobim.org/1_developer_primer_intro/0-introduction/4-obstacles-and-workaround.md)).

**Numbers:**
| property | Rhino 8 | Dynamo | Houdini (built-in) | source |
|---|---|---|---|---|
| Member completion | yes | yes, after a run (CPython) | not found in docs | [Rhino](https://developer.rhino3d.com/guides/scripting/editor-editing/), [Dynamo forum](https://forum.dynamobim.com/t/intellisense-for-python/85040), [Houdini](https://www.sidefx.com/docs/houdini/network/parms.html) |
| Signature help | yes | not found | not found | same |
| Squiggles + problems list | yes | no list found | compile errors only | [Rhino](https://developer.rhino3d.com/guides/scripting/editor-problems/), [Houdini](https://www.sidefx.com/docs/houdini/vex/snippets.html) |
| Print capture | Terminal + `out` | not documented in Primer | not found | [Rhino](https://developer.rhino3d.com/guides/scripting/editor-terminal/) |
| Debugger | yes | no | no (built-in) | [Rhino](https://developer.rhino3d.com/guides/scripting/editor-debug/), [Dynamo](https://primer2.dynamobim.org/1_developer_primer_intro/0-introduction/4-obstacles-and-workaround.md) |

**Take for Studio:**
- Version 1: highlighting, completion of inputs and host API, signature help, squiggles plus a problems list, print pane, find/replace, Ctrl+Enter run. Version 2: format on save, multi-cursor beyond box selection, debugger.

---

## Part 2. Avalonia editor components

### AvaloniaEdit (Avalonia.AvaloniaEdit 12.0.0, released 2026-04-08)
**How it works:**
- A port of the WPF AvalonEdit to Avalonia; listed features include TextMate highlighting, folding, completion, line numbers, virtualization, "Multi-caret edition" and word wrap ([README](https://raw.githubusercontent.com/AvaloniaUI/AvaloniaEdit/master/README.md)).
- "Multi-caret" means rectangular selection: "multiple edition is available using the rectangular selection that can be done using alt + mouse" (collaborator, 2022, [discussion #279](https://github.com/AvaloniaUI/AvaloniaEdit/discussions/279)). The DLL has `RectangleSelection` and no `MultiCaret` type (measured M3).
- Search and replace with regex, match case and whole words exist in the DLL (`ReplaceAll`, `UseRegex`, `MatchCase`, `WholeWords`), plus `CompletionWindow`, `OverloadInsightWindow` (signature help popup) and `FoldingManager` (measured M3).
- No minimap and no text-marker (squiggle) service in the DLL; squiggles must be drawn with an `IBackgroundRenderer` (measured M3: 0 hits for `Minimap`, `TextMarker`, `Squiggle`).
- Targets net8.0 and net10.0, MIT ([csproj](https://raw.githubusercontent.com/AvaloniaUI/AvaloniaEdit/master/src/AvaloniaEdit/AvaloniaEdit.csproj), [Directory.Build.props](https://raw.githubusercontent.com/AvaloniaUI/AvaloniaEdit/master/src/Directory.Build.props)).

**Good to use because:**
- Official AvaloniaUI package, MIT, released in step with Avalonia 12 (measured M2).
- AOT work has been done: compiled bindings to "Make completion list trimming compatible" (2023, [PR #321](https://github.com/AvaloniaUI/AvaloniaEdit/pull/321)); a NativeAOT binding warning was fixed (2024, [issue #404](https://github.com/AvaloniaUI/AvaloniaEdit/issues/404)).
- It is the base of RoslynPad's Avalonia editor package and of Dynamo's WPF ancestor (see below).

**Bad to use because:**
- Not marked AOT-compatible: no `IsAotCompatible` or `IsTrimmable` metadata in the 12.0.0 DLL (measured M3), and the demo does not publish with AOT ([Demo csproj](https://raw.githubusercontent.com/AvaloniaUI/AvaloniaEdit/master/src/AvaloniaEdit.Demo/AvaloniaEdit.Demo.csproj)). Studio must test it under `PublishAot` itself.
- No screen reader support: issue "Screen Reader Can't access" (NVDA, Narrator, Orca) is open; maintainer: "no immediate plans" and a fix "still won't be complete without ITextRangeProvider or equivalent on the Avalonia side" (Oct 2025, [issue #541](https://github.com/AvaloniaUI/AvaloniaEdit/issues/541)). The DLL has 0 `AutomationPeer` hits (measured M3).
- No true multi-cursor and no minimap (see above).

**Numbers:**
| property | value | source |
|---|---|---|
| Version / date | 12.0.0, 2026-04-08 | measured M2 |
| Licence | MIT | measured M2 |
| Total downloads | 2,272,350 | measured M1 |
| DLL size (net10.0) | 644,096 bytes | measured M3 |
| Dependencies | Avalonia >= 12.0.0 only | measured M2 |
| GitHub stars | about 1.1k | [GitHub](https://github.com/AvaloniaUI/AvaloniaEdit) |
| IsAotCompatible metadata | absent | measured M3 |

**Take for Studio:**
- Best in-process editor for an AOT Avalonia app; plan to add a squiggle renderer, a gutter marker margin, and an automation peer.
- Run an AOT smoke test (open editor, completion window, search panel, folding) in CI before committing.

### AvaloniaEdit.TextMate 12.0.0, TextMateSharp 2.0.4, Onigwrap 1.0.11
**How it works:**
- TextMateSharp is "a port of microsoft/vscode-textmate", reads JSON grammars only, and wraps the Oniguruma regex engine through Onigwrap ([TextMateSharp](https://github.com/danipen/TextMateSharp)).
- AvaloniaEdit.TextMate plugs it into the editor; you can implement `IRegistryOptions` to supply your own grammars instead of the bundled set ([AvaloniaEdit README](https://raw.githubusercontent.com/AvaloniaUI/AvaloniaEdit/master/README.md)).
- Onigwrap ships native `libonigwrap` for win-x64, win-arm64, linux and macOS (measured M3).
- TextMateSharp merged "Trimming and NativeAOT compatible" (Feb 2023, [PR #42](https://github.com/danipen/TextMateSharp/pull/42)) and "Fix Json serialization AOT issue" (Jun 2023, [PR list](https://github.com/danipen/TextMateSharp/issues?q=AOT+OR+trim)).

**Good to use because:**
- Same grammars and themes as VS Code (Dark+, Light+, high contrast) ([TextMateSharp](https://github.com/danipen/TextMateSharp)).
- All MIT (measured M2).

**Bad to use because:**
- The bundled grammar DLL is large: 6,749,696 bytes for 51 grammar packages and 21 themes (measured M3); Studio needs only Python and C#.
- A native regex DLL must ship next to the AOT exe (measured M3).
- TextMate gives lexical colours only; it does not know types (no semantic colouring) ([TextMateSharp](https://github.com/danipen/TextMateSharp)).

**Numbers:**
| property | value | source |
|---|---|---|
| AvaloniaEdit.TextMate | 12.0.0, 2026-04-08, MIT, 772,611 downloads | measured M1, M2 |
| TextMateSharp | 2.0.4, 2026-06-04, MIT, 1,760,167 downloads | measured M1, M2 |
| TextMateSharp.Grammars | 2.0.4, 1,579,899 downloads, DLL 6,749,696 bytes | measured M1, M3 |
| Bundled grammars / themes | 51 / 21 | measured M3 (embedded resource names) |
| libonigwrap.dll win-x64 | 541,184 bytes | measured M3 |
| TextMateSharp stars | 170 | [GitHub](https://github.com/danipen/TextMateSharp) |

**Take for Studio:**
- Use AvaloniaEdit.TextMate with a custom `IRegistryOptions` that embeds only the Python and C# grammars and two themes mapped to Studio's slate palette.

### RoslynPad.Editor.Avalonia 5.0.0 (2026-05-21) and the new Morgania editor
**How it works:**
- "A Roslyn-powered code editor control for Avalonia, built on AvaloniaEdit" with completion, diagnostics, signature help, quick actions and folding ([package README in the nupkg](https://api.nuget.org/v3-flatcontainer/roslynpad.editor.avalonia/5.0.0/roslynpad.editor.avalonia.5.0.0.nupkg), measured M3).
- It depends on Microsoft.CodeAnalysis.CSharp, .Features, .Workspaces, .Scripting and System.Composition in the same process (measured M2).
- RoslynPad.Roslyn 5.0.0 contains `IgnoresAccessChecksToAttribute`, a trick to call Roslyn internals (measured M3).
- The RoslynPad app itself now uses "the Morgania editor, an Avalonia editor based on the vs-editor-api repo" ([README](https://raw.githubusercontent.com/roslynpad/roslynpad/main/README.md), [packages](https://raw.githubusercontent.com/roslynpad/roslynpad/main/docs/packages/README.md)); the Morgania packages were not found on nuget.org (measured M1, 2026-11-01).

**Good to use because:**
- MIT and a working reference for wiring Roslyn completion, signature help and diagnostics onto AvaloniaEdit ([GitHub](https://github.com/roslynpad/roslynpad)).

**Bad to use because:**
- Roslyn must run in the editor's process; Studio's AOT process cannot load or JIT-compile assemblies ("No dynamic loading", "No runtime code generation", [Native AOT](https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/)), and Roslyn DLLs are not AOT-marked (measured M3, see Roslyn section).
- Calling Roslyn internals ties each RoslynPad release to exact Roslyn versions (measured M3).
- Small user base: 16,737 downloads (measured M1).

**Numbers:**
| property | value | source |
|---|---|---|
| RoslynPad.Editor.Avalonia | 5.0.0, 2026-05-21, MIT, 16,737 downloads | measured M1, M2 |
| RoslynPad.Roslyn | 5.0.0, 193,733 downloads | measured M1 |
| RoslynPad stars | 2.8k | [GitHub](https://github.com/roslynpad/roslynpad) |
| Morgania on nuget.org | not found | measured M1 |

**Take for Studio:**
- Read RoslynPad's code for patterns, but do not reference it from the AOT exe. Put Roslyn in a helper process.

### Web view route: Avalonia.Controls.WebView 12.1.1 with Monaco 0.57.0
**How it works:**
- Avalonia's WebView went free and open source with Avalonia 12 (blog, 2026-03-11, [AvaloniaUI](https://avaloniaui.net/blog/the-avalonia-webview-is-going-open-source)); the 12.1.1 nuspec says MIT (measured M3, [GitHub](https://github.com/AvaloniaUI/Avalonia.Controls.WebView)).
- It uses the platform engine: WebView2 on Windows, WKWebView on macOS, WPE or WebKitGTK on Linux ([NativeWebView](https://docs.avaloniaui.net/accelerate/components/webview/nativewebview)); WebView2 is "Pre-installed on Windows 11" ([quickstart](https://docs.avaloniaui.net/accelerate/components/webview/quickstart)).
- The package is marked `IsAotCompatible` and `IsTrimmable` (measured M3).
- Monaco is "the fully featured code editor from VS Code", MIT; language services run in web workers, which cannot start from `file://` pages ([monaco-editor](https://github.com/microsoft/monaco-editor)).
- Monaco reads screen readers well: paging strategy, F8 to announce errors, suggestions announced, Ctrl+M tab trapping ([Accessibility Guide](https://github.com/microsoft/monaco-editor/wiki/Monaco-Editor-Accessibility-Guide)).

**Good to use because:**
- Gives multi-cursor, minimap, folding, find/replace and accessibility for free ([monaco-editor](https://github.com/microsoft/monaco-editor), [guide](https://github.com/microsoft/monaco-editor/wiki/Monaco-Editor-Accessibility-Guide)).
- The control is AOT-marked, so the host side is safe (measured M3).

**Bad to use because (why it may not suit an AOT desktop app):**
- WebView2 starts its own browser, renderer and GPU processes outside the app ([process model](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/process-model)); one per open editor is heavy for a node graph.
- Runtime dependency: Evergreen WebView2 must be present (a few Windows 10 devices lack it); the Fixed Version is "over 250 MB" ([distribution](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/distribution)).
- Airspace: "Native views always render on top of Avalonia content" and cannot be transparent or transformed (Avalonia Android guide, same NativeControlHost idea, [docs](https://docs.avaloniaui.net/docs/guides/platforms/android/embed-native-views)); Studio's popups, drag previews and zoom would fight it.
- Monaco adds about 25 MB of files (min build) and a JSON bridge for every completion, theme and key binding (measured M6).
- Mobile and embedded views are not a supported target for Monaco ("No" for mobile, [FAQ](https://github.com/microsoft/monaco-editor)).

**Numbers:**
| property | value | source |
|---|---|---|
| Avalonia.Controls.WebView | 12.1.1, 2026-10-12, MIT, 538,089 downloads | measured M1, M2 |
| WebView GitHub stars | 131 | [GitHub](https://github.com/AvaloniaUI/Avalonia.Controls.WebView) |
| monaco-editor | 0.57.0, 2026-09-24, MIT | measured M6 |
| Monaco weekly npm downloads | 13,116,355 (2026-10-23 to 10-29) | [npm API](https://api.npmjs.org/downloads/point/last-week/monaco-editor) |
| Monaco tarball / unpacked / min folder | 18.6 MB / 101.7 MB / 25 MB | measured M6 |
| WebView2 Fixed Version size | over 250 MB | [distribution](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/distribution) |
| Older Avalonia web views | WebView.Avalonia 11.0.0.1 (2023-07-12), CefGlue.Avalonia 120.6099.215, WebViewControl-Avalonia 3.120.14 (no licence field) | measured M1, M2 |

**Take for Studio:**
- Keep as plan B (or for a "pop out to big editor" window), not as the inline node editor.

### Scintilla ports
**How it works:**
- All Scintilla packages on NuGet are Windows Forms wrappers, for example "A Windows Forms control, wrapper, and bindings for the Scintilla text editor" (measured M1, search `q=scintilla`).
- A search for an Avalonia Scintilla port returned none (measured M1, searches `scintilla`, `avalonia code editor`).

**Good to use because:**
- Mature and MIT (Scintilla5.NET 7.1.1, 2026-10-19) (measured M2).

**Bad to use because:**
- WinForms only; hosting it in Avalonia would need a native child window, with the same airspace limits as a web view ([Avalonia docs](https://docs.avaloniaui.net/docs/guides/platforms/android/embed-native-views)).

**Numbers:**
| property | value | source |
|---|---|---|
| Scintilla5.NET | 7.1.1, 2026-10-19, MIT, 145,270 downloads | measured M1, M2 |
| jacobslusser.ScintillaNET | 3.6.3, 1,192,788 downloads | measured M1 |
| Avalonia port | none found | measured M1 |

**Take for Studio:**
- Rule out.

### Screen readers and Avalonia text editors (status 2026-11-01)
**How it works:**
- Avalonia uses automation peers, with UI Automation on Windows, NSAccessibility on macOS and AT-SPI2 on Linux; the page says nothing about text ranges for editing controls (updated 2026-04-02, [Avalonia accessibility](https://docs.avaloniaui.net/docs/app-development/accessibility)).
- A PR to "Implement UIA TextPattern for TextBox on Windows" was closed on 2026-08-19 in favour of a larger rework ([PR #21988](https://github.com/AvaloniaUI/Avalonia/pull/21988)).
- That rework is now the open proposal "Structured text input: a shared text contract for IME and accessibility" with all new API marked `[Unstable]` (opened 2026-09-07, [issue #22168](https://github.com/AvaloniaUI/Avalonia/issues/22168)).

**Good to use because:**
- Once it lands, a custom editor could expose text ranges through `IAccessibleText` ([issue #22168](https://github.com/AvaloniaUI/Avalonia/issues/22168)).

**Bad to use because:**
- Today neither Avalonia's TextPattern nor AvaloniaEdit's peer exists ([issue #541](https://github.com/AvaloniaUI/AvaloniaEdit/issues/541)).

**Numbers:**
| property | value | source |
|---|---|---|
| AvaloniaEdit screen reader issue | open since 2025-10-02 | [issue #541](https://github.com/AvaloniaUI/AvaloniaEdit/issues/541) |
| Avalonia text contract | proposal, open, target version not stated | [issue #22168](https://github.com/AvaloniaUI/Avalonia/issues/22168) |

**Take for Studio:**
- Ship a basic automation peer (name, value of current line, problems list as a normal list control) and F8 problem navigation now; adopt Avalonia's text contract when stable.

---

## Part 3. Completion and diagnostics engines

### Jedi 0.20.1, jedi-language-server 0.47.0, python-lsp-server 1.15.0
**How it works:**
- Jedi is "a static analysis tool for Python" focused on "autocompletion and goto" ([docs](https://jedi.readthedocs.io/en/latest/)).
- API: `Script.complete`, `Script.get_signatures`, `Script.get_syntax_errors`, `infer(prefer_stubs=...)`, and `Interpreter` for REPL namespaces ([API](https://jedi.readthedocs.io/en/latest/docs/api.html)).
- It "Understands stub files" ([features](https://jedi.readthedocs.io/en/latest/docs/features.html)).
- python-lsp-server (pylsp) uses Jedi for completion, hover, signature help; lint with pyflakes, pycodestyle (pylint off by default); format with autopep8 or YAPF; ruff via the python-lsp-ruff plugin ([GitHub](https://github.com/python-lsp/python-lsp-server)).

**Good to use because:**
- All MIT, pure Python, so they run on the same interpreter Studio ships (measured M4).
- jedi-language-server is a small LSP wrapper ("A language server for Jedi!") (measured M4).

**Bad to use because:**
- No type checking; Jedi "intentionally stops type inference" on complex code; "Jedi does not have a very good cache layer"; numpy and pandas load slowly the first time ([features](https://jedi.readthedocs.io/en/latest/docs/features.html)).
- pylsp documents only a WebSockets option in its README (stdio is the default for LSP servers but I did not verify it on that page) ([GitHub](https://github.com/python-lsp/python-lsp-server)).

**Numbers:**
| property | value | source |
|---|---|---|
| jedi | 0.20.1, 2026-10-12, MIT, Python >= 3.10, wheel 4.89 MB | measured M4 |
| jedi downloads last month | 95,925,426 | measured M5 |
| python-lsp-server | 1.15.0, 2026-07-27, MIT, 1,155,721 downloads last month, 2.6k stars | measured M4, M5, [GitHub](https://github.com/python-lsp/python-lsp-server) |
| jedi-language-server | 0.47.0, 2026-05-31, MIT, 121,802 last month | measured M4, M5 |

**Take for Studio:**
- Good light option if Studio already ships CPython: run jedi-language-server in a helper process for completion and signatures.

### Pyright 1.1.414, basedpyright 1.40.2, and Pylance
**How it works:**
- Pyright is "a full-featured, standards-based static type checker for Python" ([README](https://raw.githubusercontent.com/microsoft/pyright/main/README.md)); it needs Node.js (the PyPI `pyright` package "will automatically install node") ([installation](https://raw.githubusercontent.com/microsoft/pyright/main/docs/installation.md)).
- It resolves imports to `.pyi` stubs first; `stubPath` (default `./typings`) points at custom stubs ([type stubs](https://raw.githubusercontent.com/microsoft/pyright/main/docs/type-stubs.md), [configuration](https://raw.githubusercontent.com/microsoft/pyright/main/docs/configuration.md)).
- Pylance is closed source: "The Pylance codebase is not open-source" ([pylance-release](https://github.com/microsoft/pylance-release)).
- basedpyright is "a fork of pyright with various type checking improvements, pylance features" and "can be installed from PyPI without having to install NodeJS" ([docs](https://docs.basedpyright.com/latest/)); it ships `basedpyright-langserver` ([install doc](https://raw.githubusercontent.com/DetachHead/basedpyright/main/docs/installation/command-line-and-language-server.md)) and re-implements semantic highlighting, inlay hints and builtin docstrings ([Pylance features](https://docs.basedpyright.com/latest/benefits-over-pyright/pylance-features/)).

**Good to use because:**
- Best diagnostics and types for Python; MIT (measured M4, M6).

**Bad to use because:**
- Still a Node program: basedpyright's PyPI package depends on `nodejs-wheel-binaries`, whose Windows wheel is 42.4 MB (measured M4).
- Pylance cannot be redistributed (closed source; its licence page needs a browser login, not verified) ([pylance-release](https://github.com/microsoft/pylance-release)).

**Numbers:**
| property | value | source |
|---|---|---|
| pyright | 1.1.414, npm 2026-09-09, MIT, 1,218,203 npm downloads last week | measured M6 |
| basedpyright | 1.40.2, 2026-10-04, MIT, 13,847,743 last month | measured M4, M5 |
| basedpyright download on Windows | 13.69 MB wheel + 42.4 MB Node wheel | measured M4 |

**Take for Studio:**
- Use only if deep type checking matters more than install size; otherwise prefer ty or Jedi.

### Ruff 0.17.3 and ty 0.0.95 (Astral, Rust)
**How it works:**
- `ruff server` is the language server built into the ruff binary, written in Rust, giving diagnostics, quick fixes and formatting; it replaced ruff-lsp ([Editors](https://docs.astral.sh/ruff/editors/)).
- The formatter is "a drop-in replacement for Black"; on Django and Zulip "> 99.9% of lines are formatted identically" ([Formatter](https://docs.astral.sh/ruff/formatter/)).
- ty is "An extremely fast Python type checker and language server, written in Rust" with completions, hover, inlay hints and code actions ([ty docs](https://docs.astral.sh/ty/)); Ruff's docs point to ty for completion ([Editors](https://docs.astral.sh/ruff/editors/)).

**Good to use because:**
- Single native exe each, no Node and no Python needed to run them (measured M4, platform wheels).
- MIT (measured M4), heavily used (measured M5).

**Bad to use because:**
- ty is still 0.0.x and classified "Development Status :: 4 - Beta" (measured M4); its speed claim "10x - 100x faster than mypy and Pyright" is the vendor's ([ty docs](https://docs.astral.sh/ty/)).

**Numbers:**
| property | value | source |
|---|---|---|
| ruff | 0.17.3, 2026-10-27, MIT, Windows wheel 10.34 MB | measured M4 |
| ruff downloads last month | 304,029,216 | measured M5 |
| ty | 0.0.95, 2026-10-29, MIT classifier, Beta, Windows wheel 14.1 MB | measured M4 |
| ty downloads last month | 41,012,419 | measured M5 |

**Take for Studio:**
- Ship `ruff` for lint and format on save (small, native). Evaluate `ty server` for completion against Jedi.

### Language Server Protocol over stdio
**How it works:**
- Messages are JSON-RPC with a required `Content-Length` header ([LSP 3.17](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/)).
- Completion, signature help, publishDiagnostics and formatting are standard methods ([LSP 3.17](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/)).

**Good to use because:**
- One client in Studio can talk to ruff, ty, basedpyright or jedi-language-server ([Editors](https://docs.astral.sh/ruff/editors/), [basedpyright](https://raw.githubusercontent.com/DetachHead/basedpyright/main/docs/installation/command-line-and-language-server.md)).
- Out-of-process servers cannot crash Studio and need no AOT support.

**Bad to use because:**
- Studio must write an LSP client (no AOT-ready .NET client was checked here; not verified).

**Numbers:**
| property | value | source |
|---|---|---|
| Required header | Content-Length | [LSP 3.17](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/) |

**Take for Studio:**
- Write a small LSP client with `System.Text.Json` source generation (AOT-safe) and run one server process per language, shared by all script nodes.

### Roslyn APIs (Microsoft.CodeAnalysis 5.9.0, 2026-08-17) in a helper process
**How it works:**
- Public: `CompletionService.GetService(document)`, `GetCompletionsAsync`, `GetDescriptionAsync`, `GetChangeAsync`; `QuickInfoService.GetQuickInfoAsync`; `Formatter.FormatAsync`; `Classifier.GetClassifiedSpansAsync`; `AdhocWorkspace` (measured M7 on [Features PublicAPI](https://raw.githubusercontent.com/dotnet/roslyn/main/src/Features/Core/Portable/PublicAPI.Shipped.txt) and [Workspaces PublicAPI](https://raw.githubusercontent.com/dotnet/roslyn/main/src/Workspaces/Core/Portable/PublicAPI.Shipped.txt)).
- Signature help is internal: `internal interface ISignatureHelpProvider` ([source](https://raw.githubusercontent.com/dotnet/roslyn/main/src/Features/Core/Portable/SignatureHelp/ISignatureHelpProvider.cs)); 0 public API lines mention SignatureHelp (measured M7).
- Diagnostics come from the compilation (errors and warnings with spans) and API docs come from `MetadataReference.CreateFromFile(path, properties, documentation)` with a `DocumentationProvider` ([Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/api/microsoft.codeanalysis.metadatareference.createfromfile)).

**Good to use because:**
- MIT, the same engine as Visual Studio (measured M2).

**Bad to use because:**
- Not AOT-marked; Workspaces and Features use System.Composition (MEF) (measured M3). So it belongs in a normal JIT .NET helper process.
- Signature help needs either internal access (as RoslynPad does) or Studio's own code using `SemanticModel` symbol info ([source](https://raw.githubusercontent.com/dotnet/roslyn/main/src/Features/Core/Portable/SignatureHelp/ISignatureHelpProvider.cs)).

**Numbers:**
| property | value | source |
|---|---|---|
| Version / date | 5.9.0, 2026-08-17, MIT | measured M2 |
| Downloads | Features 131,931,992; CSharp.Features 128,631,069; Workspaces.Common 984,768,111 | measured M1 |
| DLL size, six main DLLs (net10.0) | 23.5 MB (3.10 + 7.08 + 4.32 + 0.97 + 5.69 + 2.37) | measured M3 |
| IsAotCompatible / IsTrimmable | absent in all six | measured M3 |

**Take for Studio:**
- A small `studio-csharp-ls` helper (JIT .NET 10) that holds an `AdhocWorkspace`, Studio's reference assemblies and the node prelude, and answers completion, quick info, diagnostics and format over LSP or a tiny JSON protocol. The same helper can compile and run C# nodes.

### OmniSharp, the Roslyn language server, and the C# Dev Kit licence
**How it works:**
- OmniSharp is MIT, built on Roslyn workspaces, with stdio and HTTP flavours ([GitHub](https://github.com/OmniSharp/omnisharp-roslyn)); latest v2.0.0 dated 18 Sep (2026 per assets) ([releases](https://github.com/OmniSharp/omnisharp-roslyn/releases)).
- The VS Code C# extension now uses Roslyn's own LSP server by default; OmniSharp is opt-in via `dotnet.server.useOmnisharp` ([vscode-csharp README](https://raw.githubusercontent.com/dotnet/vscode-csharp/main/README.md)).
- The extension's binaries: "You may only use the C# Extension for Visual Studio Code with Visual Studio Code, Visual Studio or Xamarin Studio software" ([runtime licence](https://raw.githubusercontent.com/dotnet/vscode-csharp/main/RuntimeLicenses/license.txt)); its source is MIT ([README](https://raw.githubusercontent.com/dotnet/vscode-csharp/main/README.md)).
- C# Dev Kit: free for personal, academic, open source, and commercial teams up to 5; "For 6+ developers, those users will need a Visual Studio Professional (or higher) subscription" (FAQ dated 2024-05-03, [VS Code](https://code.visualstudio.com/docs/csharp/cs-dev-kit-faq)).

**Good to use because:**
- OmniSharp and Roslyn's LSP server package are MIT (measured M2 for `Microsoft.CodeAnalysis.LanguageServer.win-x64`).

**Bad to use because:**
- Both are project-based (MSBuild): the Roslyn LSP package depends on Microsoft.Build (measured M2), which is heavy for a single script.
- Roslyn LSP on nuget.org has one prerelease from 2025-06-06 with 1,882 downloads (measured M1, M2).
- Dev Kit and the C# extension binaries cannot be shipped inside Studio ([runtime licence](https://raw.githubusercontent.com/dotnet/vscode-csharp/main/RuntimeLicenses/license.txt)).

**Numbers:**
| property | value | source |
|---|---|---|
| OmniSharp.Roslyn on NuGet | 1.39.13, 272,420 downloads | measured M1 |
| OmniSharp stars | 2.1k | [GitHub](https://github.com/OmniSharp/omnisharp-roslyn) |
| Roslyn LSP win-x64 package | 5.0.0-1.25277.114, 2025-06-06, MIT, 1,882 downloads | measured M1, M2 |
| C# Dev Kit free commercial seats | up to 5 | [FAQ](https://code.visualstudio.com/docs/csharp/cs-dev-kit-faq) |

**Take for Studio:**
- Write the thin Roslyn helper rather than hosting OmniSharp; never ship Dev Kit or C# extension binaries.

### Completion for Studio's own API: .pyi stubs and reference assemblies
**How it works:**
- Python: stubs are `.pyi` files whose bodies are `...`; docstrings in stubs "can improve certain IDE functionality, such as hover info"; `stubgen` and `pyright --createstub` make drafts ([typing guide](https://typing.python.org/en/latest/guides/writing_stubs.html)).
- Distribution: inline types with `py.typed`, stubs next to source, or a `foopkg-stubs` package (PEP 561, 2017, [PEP](https://peps.python.org/pep-0561/)); pyright reads `stubPath` ([configuration](https://raw.githubusercontent.com/microsoft/pyright/main/docs/configuration.md)).
- McNeel generates stubs for RhinoCommon, Eto and Grasshopper from its .NET assemblies ([pythonstubs](https://github.com/mcneel/pythonstubs)).
- C#: reference assemblies "contain only the minimum amount of metadata" for the public API, can be made with `ProduceReferenceAssembly`, and "can't be loaded for execution" ([Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/standard/assembly/reference-assemblies)); pair each with its XML doc file through a `DocumentationProvider` ([CreateFromFile](https://learn.microsoft.com/en-us/dotnet/api/microsoft.codeanalysis.metadatareference.createfromfile)).

**Good to use because:**
- Both are static, so completion works before the first run (unlike Dynamo, [forum](https://forum.dynamobim.com/t/intellisense-for-python/85040)).

**Bad to use because:**
- Stubs drift from the real API unless generated in the build ([typing guide](https://typing.python.org/en/latest/guides/writing_stubs.html)).

**Numbers:**
| property | value | source |
|---|---|---|
| Rhino stubs last on PyPI | 2021-05-24 (old) | measured M4 |

**Take for Studio:**
- Generate `studio.pyi` and `Studio.Api.ref.dll` + XML docs in Studio's build. Per node, generate a prelude: Python `x: float`, `curves: list[Curve]`; C# a wrapper class with typed parameters, so inputs and outputs complete.

---

## Part 4. Debugging

### debugpy 1.8.22 (DAP for Python)
**How it works:**
- "An implementation of the Debug Adapter Protocol for Python 3" with `debugpy.listen()`, `wait_for_client()` and `breakpoint()` ([GitHub](https://github.com/microsoft/debugpy)).
- `configure()` "must be called before calling connect() or listen()" ([API Reference](https://github.com/microsoft/debugpy/wiki/API-Reference)).
- In an embedded interpreter, `sys.executable` points at the host exe, so debugpy spawns the wrong process; maintainer: call `debugpy.configure(python=...)` (2022, still open as a docs issue, [issue #1097](https://github.com/microsoft/debugpy/issues/1097)).
- DAP: the tool talks to the adapter over stdin/stdout or a socket using a `Content-Length` header and JSON ([DAP overview](https://microsoft.github.io/debug-adapter-protocol/overview)).

**Good to use because:**
- MIT and widely used (measured M4, M5); any DAP UI can drive it ([DAP overview](https://microsoft.github.io/debug-adapter-protocol/overview)).

**Bad to use because:**
- Embedding pitfalls above; Studio must build a DAP client UI (breakpoints, stack, variables).

**Numbers:**
| property | value | source |
|---|---|---|
| Version / date | 1.8.22, 2026-09-15, MIT | measured M4 |
| Downloads last month | 78,662,693 | measured M5 |
| Windows wheel | about 5.4 MB | measured M4 |
| Stars | 2.5k | [GitHub](https://github.com/microsoft/debugpy) |

**Take for Studio:**
- Version 2 feature. If Python runs in a helper process with a real `python.exe`, debugpy works with no embedding fixes.

### netcoredbg 3.2.0 (Samsung) vs vsdbg
**How it works:**
- netcoredbg is a managed debugger for CoreCLR that "implements GDB/MI and VSCode Debug Adapter Protocol"; MIT ([GitHub](https://github.com/Samsung/netcoredbg)).
- vsdbg shows: "You may only use the Microsoft .NET Core Debugger (vsdbg) with Visual Studio Code, Visual Studio or Visual Studio for Mac software" (2019, old, [VSCodium #82](https://github.com/VSCodium/vscodium/issues/82)); the current C# extension licence has the same limit ([runtime licence](https://raw.githubusercontent.com/dotnet/vscode-csharp/main/RuntimeLicenses/license.txt)).
- A published Native AOT app is native: "The managed debugger won't work on them" ([AOT diagnostics](https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/diagnostics)).

**Good to use because:**
- The only redistributable DAP debugger for .NET found here ([GitHub](https://github.com/Samsung/netcoredbg)).

**Bad to use because:**
- C# node code can only be debugged in a JIT CoreCLR process (the helper), never inside the AOT exe ([AOT diagnostics](https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/diagnostics)).
- Release page shows "25 Jun" without a year for 3.2.0-1092 (year not verified) ([release](https://github.com/Samsung/netcoredbg/releases/tag/3.2.0-1092)).

**Numbers:**
| property | value | source |
|---|---|---|
| Latest release | 3.2.0-1092, "25 Jun" (year not shown) | [releases](https://github.com/Samsung/netcoredbg/releases) |
| Stars | 1.4k | [GitHub](https://github.com/Samsung/netcoredbg) |

**Take for Studio:**
- If a C# debugger is ever needed, use netcoredbg against the helper process; never vsdbg.

### Minimal alternative: print plus inspect values per run
**How it works:**
- Rhino: Terminal captures print per run; the Grasshopper `out` output carries print lines as data ([Terminal](https://developer.rhino3d.com/guides/scripting/editor-terminal/), [GH Python](https://developer.rhino3d.com/guides/scripting/scripting-gh-python)).
- Rhino's debugger shows "Run Script (2 of 11)", one run per item, and keeps the last Variables state after stopping ([Script Component](https://developer.rhino3d.com/guides/scripting/scripting-component/)).
- Dynamo: no debugger; docs suggest try/except with `traceback` and print ([Primer](https://primer2.dynamobim.org/1_developer_primer_intro/0-introduction/4-obstacles-and-workaround.md)).
- Jupyter: per-run stdout, stderr, error with traceback and an execution counter ([Messaging](https://jupyter-client.readthedocs.io/en/latest/messaging.html)).

**Good to use because:**
- Cheap: no DAP, no breakpoints, works the same for Python and C# and in AOT.

**Bad to use because:**
- No stepping; loops over many items flood the console (Rhino runs per item, [Script Component](https://developer.rhino3d.com/guides/scripting/scripting-component/)).

**Numbers:**
| property | value | source |
|---|---|---|
| Rhino terminal modes | all at once (default) or line by line | [Terminal](https://developer.rhino3d.com/guides/scripting/editor-terminal/) |

**Take for Studio:**
- Version 1: a console pane grouped by run and by item index (for-each), a clickable traceback that jumps to the line, and an "inspect" call (`studio.inspect(x)`) that records named values per run into a small table next to the console.
