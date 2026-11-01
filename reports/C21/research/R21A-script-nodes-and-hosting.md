# R21A notes: script node (Python and C#) for Studio Flow

Agent R21A, report C21. Read on 2026-11-01. Research only, no Studio code.

Scope: Part 1 looks at how other tools do script nodes. Part 2 looks at the options for a .NET 10 Native AOT host.

Method:
- Facts come from vendor docs, release notes, source and issue pages that I opened. Forum posts are user demand, and I flag them as third party.
- I did not measure call costs. Another agent (R21M) does that.
- I did measure download and install sizes and package versions, with the method shown in each table:
  - HTTP HEAD `Content-Length`.
  - Downloading a zip and summing `ZipInfo.file_size` with Python `zipfile`.
  - The NuGet search, registration and catalog APIs.
  - The PyPI JSON API.
- Version numbers are as of 2026-11-01.

---

## Part 1. How other tools do script nodes

### Rhino 8 ScriptEditor and Grasshopper Script component (Rhino 8 shipping, Rhino 9 BETA; docs read 2026-11-01)
**How it works:**
- There is one Script component for all languages. A button on the component picks the language. You zoom in to add or remove inputs and outputs, and you right-click an input to set its type hint ([Script Component guide](https://developer.rhino3d.com/guides/scripting/scripting-component/)).
- In Script-Mode, parameters become variables and you assign outputs by name. Each input has Item, List or Tree access.
  - Type hints convert data before the script runs. For example, a Line wired into a `float` hint becomes its length.
  - The "Required" input option exists "as of Rhino 8.14" ([Grasshopper Python guide](https://developer.rhino3d.com/guides/scripting/scripting-gh-python/)).
- SDK-Mode wraps the code in a class that subclasses `GH_ScriptInstance`. The class has `RunScript`, `BeforeRunScript` and `AfterRunScript`, plus the preview overrides `DrawViewportWires` and `DrawViewportMeshes` ([GH Python guide](https://developer.rhino3d.com/guides/scripting/scripting-gh-python/)). In C#, "All outputs are passed by reference using `ref` keyword" ([GH C# guide](https://developer.rhino3d.com/guides/scripting/scripting-gh-csharp/)).
- Packages are declared in the script source, so "it installs what it needs when someone else opens it":
  - Python 3: `#r: numpy`, `#requirements: numpy, requests`, or a PEP 723 block.
  - C#: `#r "nuget: RestSharp, 110.2.0"`.
  - Rhino packages: `#r "yak: ..."`.
  ([Script Package References](https://developer.rhino3d.com/guides/scripting/advanced-packages/), page tagged "New in 9").
- How each language runs ([Python guide](https://developer.rhino3d.com/guides/scripting/scripting-python/)):
  - Python 3 is CPython. It "reaches .NET, and therefore RhinoCommon, through Python.NET".
  - Python 2 is IronPython. IronPython "runs on .NET itself".
- Environments ([Python Package Environments](https://developer.rhino3d.com/guides/scripting/advanced-pyvenvs/)):
  - By default, all Python packages go into one shared `site-envs/default-<unique-id>` folder.
  - `#venv: name` gives a script its own package set.
  - All scripts still run in "the same process, same memory, and same python interpretter state".
- One debugger covers Python and C#: breakpoints, stepping, variables and call stack ([Editor Debugging](https://developer.rhino3d.com/guides/scripting/editor-debug/)).
- Scripts are compiled and cached. The cache expires when the script or its parameters change, and "Discard Cache" forces a rebuild ([GH C# guide](https://developer.rhino3d.com/guides/scripting/scripting-gh-csharp/)).

**Good to use because:**
- Scripts carry their own dependency list, so a shared file still runs on another machine ([Script Package References](https://developer.rhino3d.com/guides/scripting/advanced-packages/)).
- Two marshalling switches let users skip data conversion ([GH Python guide](https://developer.rhino3d.com/guides/scripting/scripting-gh-python/)):
  - "Avoid Marshalling Inputs" stops .NET lists being converted to Python lists.
  - "Avoid Marshalling Outputs" lets chained Python 3 components pass one Python list directly.
- The docs give one practical speed tip: switch off the `out` (console) output when it is not needed, because capturing stdout has a cost ([GH Python guide](https://developer.rhino3d.com/guides/scripting/scripting-gh-python/)).
- Python and C# share one editor and one debugger ([Editor Debugging](https://developer.rhino3d.com/guides/scripting/editor-debug/)).

**Bad to use because:**
- Package isolation is only on disk. In memory everything is shared ([Python Package Environments](https://developer.rhino3d.com/guides/scripting/advanced-pyvenvs/)):
  - Two scripts that load different versions of one package can cause runtime errors.
  - On Windows, pip cannot replace a loaded package until Rhino restarts.
  - Any pip error marks the environment "Invalid".
- CPython calls into .NET are slow:
  - One user found the Python 3 component "about 10x slower than the old python component" on Rhino 8.20 ([McNeel forum, Jan 2026, third party user](https://discourse.mcneel.com/t/python-3-about-10x-slower-than-old-python-component/215094)).
  - McNeel's own guide says that with IronPython "Pure RhinoCommon calls are faster since nothing sits in between" ([Python guide](https://developer.rhino3d.com/guides/scripting/scripting-python/)).
- Rhino is locked to one Python version per release ([McNeel forum, staff post by eirannejad, May 2025](https://discourse.mcneel.com/t/rhino-beta-feature-python-3-13/205209)):
  - Rhino 8 ships Python 3.9, "going to hit End-of-Life towards the end of 2025".
  - Rhino 9 moves to 3.13.
  - Packages "compiled against `python39.dll`" may fail to install.
  - In the same thread, users warn that removing IronPython would break "hundreds of existing plug-ins".
- Startup can be slow. One user reported "_RunPythonScript takes up to 20 seconds to react on first call" after a reboot ([McNeel forum, Mar 2024, third party user](https://discourse.mcneel.com/t/runpythonscript-first-call-is-slow/178716)).
- Type hints convert data silently, for example a Line wired to a float hint becomes its length ([GH Python guide](https://developer.rhino3d.com/guides/scripting/scripting-gh-python/)). This can hide a wrong wire.

**Numbers:**
| property | value | source |
|---|---|---|
| CPython in Rhino 8 | 3.9 ("Python 3.9 currently shipping with Rhino 8") | [forum staff post](https://discourse.mcneel.com/t/rhino-beta-feature-python-3-13/205209) |
| CPython in Rhino 9 | 3.13.x (3.13.3 at the start of the WIP), pythonnet 3.0.5 | [forum staff post](https://discourse.mcneel.com/t/rhino-beta-feature-python-3-13/205209) |
| Python 3 vs old IronPython component, same script | "about 10x slower" (user report) | [forum](https://discourse.mcneel.com/t/python-3-about-10x-slower-than-old-python-component/215094) |
| First Python call after reboot | "up to 20 seconds" (user report, Rhino 8 SR6) | [forum](https://discourse.mcneel.com/t/runpythonscript-first-call-is-slow/178716) |
| Runtime folder | `~/.rhinocode/py39-rh8`, `~/.rhinocode/py313-rh9` | [pyvenvs guide](https://developer.rhino3d.com/guides/scripting/advanced-pyvenvs/), [forum](https://discourse.mcneel.com/t/rhino-beta-feature-python-3-13/205209) |

**Take for Studio:**
- Copy:
  - One Script node with a language switch.
  - Inputs and outputs edited on the node, each with an access mode (item or list) and a type.
  - Packages declared in the script header: PEP 723 for Python, `#r "nuget:"` for C#.
  - A built-in debugger.
- Do not copy in-process CPython with one shared package folder. Give each script, or each library flow, its own locked environment.
- Make type conversion on inputs explicit and visible. Do not silently turn a shape into a number.

### Grasshopper Hops (Hops docs for Rhino 7.13+; ghhops-server 1.5.5)
**How it works:**
- Hops calls a function that lives in a separate Grasshopper file or behind an endpoint. "During calculation Hops solves the definition in a separate process, then returns the outputs" ([Hops guide](https://developer.rhino3d.com/guides/compute/hops-component/)).
- It works "in tandem with a local instance of a Rhino.compute server". Requests are JSON over REST and carry standard Grasshopper types ([Hops guide](https://developer.rhino3d.com/guides/compute/hops-component/)).
- Asynchronous mode does not block the UI. It has a "Max Concurrent requests" setting, caching in memory or on the server, and a parallel process per data-tree branch with a "Child Process Count" setting ([Hops guide](https://developer.rhino3d.com/guides/compute/hops-component/)).
- To serve Python functions to Hops, you run a CPython process with the `ghhops-server` package. It depends on `rhino3dm` ([PyPI JSON](https://pypi.org/pypi/ghhops-server/json), measured).

**Good to use because:**
- The separate process gives crash and dependency isolation by design ([Hops guide](https://developer.rhino3d.com/guides/compute/hops-component/)).
- Async solving, caching and a worker pool are built in ([Hops guide](https://developer.rhino3d.com/guides/compute/hops-component/)).

**Bad to use because:**
- Rhino.compute "doesn't run on macOS" ([Hops guide](https://developer.rhino3d.com/guides/compute/hops-component/)). This matters little, because Studio is Windows only.
- Every call is JSON over HTTP. The guide gives no latency figures ([Hops guide](https://developer.rhino3d.com/guides/compute/hops-component/)).
- The Python server package was last released in April 2023 ([PyPI JSON](https://pypi.org/pypi/ghhops-server/json), measured).

**Numbers:**
| property | value | source |
|---|---|---|
| ghhops-server version | 1.5.5, uploaded 2023-04-24 | measured: `https://pypi.org/pypi/ghhops-server/json` |
| Default parallelism | one parallel process per branch of a data-tree input | [Hops guide](https://developer.rhino3d.com/guides/compute/hops-component/) |

**Take for Studio:**
- An out-of-process script worker can borrow three ideas from Hops:
  - Async solving that never blocks the canvas.
  - A cache keyed by input values.
  - A worker-pool size setting.

### Dynamo Python Script node (Dynamo Core 4.0, released 2025-11-25)
**How it works:**
- You add inputs with "+". They arrive in the `IN` list (`IN[0]`, `IN[1]` ...), and you return results by assigning `OUT` ([Dynamo Primer](https://primer2.dynamobim.org/8_coding_in_dynamo/8-3_python/1-python)).
- Dynamo has had four Python engines ([Dynamo blog, Jan 2025](https://dynamobim.org/pythonnet3-a-new-dynamo-python-to-fix-everything/)):
  - IronPython 2: built in before 2.8, then moved to a package.
  - IronPython 3: an unofficial package.
  - CPython3: Python.NET 2.5 on Python 3.9, default since 2.8.
  - PythonNet3: Python.NET 3 on Python 3.11.
- Dynamo 4.0 changes ([Dynamo Core 4.0 release](https://dynamobim.org/dynamo-core-4-0-release/)):
  - "PythonNet 3 is now the default Python engine for all new Python nodes".
  - "Dynamo will automatically migrate CPython nodes to PythonNet 3".
  - IronPython packages are "no longer be maintained by the Dynamo team".
  - Dynamo moved to .NET 10.
- Packages are installed by hand ([DynamoDS wiki, edited Mar 2024](https://github.com/DynamoDS/Dynamo/wiki/Customizing-Dynamo's-Python-3-installation)):
  - The Python home lives under `%localappdata%`.
  - You download `get-pip.py` into it, then run `.\Scripts\pip install`.
  - "Virtual environments are not supported by the Python Embeddable Package".

**Good to use because:**
- The model is simple: a list comes in, a list goes out ([Primer](https://primer2.dynamobim.org/8_coding_in_dynamo/8-3_python/1-python)).
- PythonNet3 no longer copies .NET collections into Python lists. They behave as views, and the guide notes "collections are no longer copied" ([Dynamo blog guide by Cyril Poupin, Dec 2025](https://dynamobim.org/dynamo-pythonnet3-upgrade-a-practical-guide-to-migrating-your-dynamo-graphs/)).

**Bad to use because:**
- Engine churn has cost users a lot. The PythonNet3 move broke many graphs ([migration guide](https://dynamobim.org/dynamo-pythonnet3-upgrade-a-practical-guide-to-migrating-your-dynamo-graphs/)):
  - No automatic conversion of .NET collections to lists.
  - Enums are no longer integers.
  - Method signatures must match strictly.
  - `with` fails on `IDisposable`.
  - GAC Interop assemblies are gone.
- The older CPython3 engine had gaps ([Dynamo blog](https://dynamobim.org/pythonnet3-a-new-dynamo-python-to-fix-everything/)):
  - It "can't implement methods with `out` or `ref` parameters".
  - It converted enums to integers.
  - Overloaded operators were not usable.
- Installing packages needs manual pip bootstrapping into the app's Python, and there are no virtual environments ([wiki](https://github.com/DynamoDS/Dynamo/wiki/Customizing-Dynamo's-Python-3-installation)).

**Numbers:**
| property | value | source |
|---|---|---|
| Python engines shipped over time | 4 (IronPython 2, IronPython 3, CPython3, PythonNet3) | [Dynamo blog](https://dynamobim.org/pythonnet3-a-new-dynamo-python-to-fix-everything/) |
| CPython3 engine | Python 3.9, Python.NET 2.5 | [Dynamo blog](https://dynamobim.org/pythonnet3-a-new-dynamo-python-to-fix-everything/) |
| PythonNet3 engine | CPython 3.11, Python.NET 3 | [migration guide](https://dynamobim.org/dynamo-pythonnet3-upgrade-a-practical-guide-to-migrating-your-dynamo-graphs/) |
| Python in Dynamo 3.0 | 3.9.12 | [wiki](https://github.com/DynamoDS/Dynamo/wiki/Customizing-Dynamo's-Python-3-installation) |

**Take for Studio:**
- Pick one Python engine. Store the Python and package versions in each saved script, and plan one documented upgrade path.
- Expose host data as views or buffers, not deep copies.

### Houdini Python SOP and VEX wrangles (Houdini 22.0 docs)
**How it works:**
- In a Python SOP, `geo = hou.pwd().geometry()` returns the node's own geometry. "Houdini copies the input SOP's geometry into the Python SOP's geometry before running the Python code", and the code then edits it in place ([Python SOP docs](https://www.sidefx.com/docs/houdini/hom/pythonsop.html)).
- The fast path is bulk attribute access ([hou.Geometry](https://www.sidefx.com/docs/houdini/hom/hou/Geometry.html)):
  - `pointFloatAttribValues` is "faster than looping over all the points".
  - `pointFloatAttribValuesAsString` is faster again.
  - Setters accept "arrays from the array and numpy Python modules".
- A VEX wrangle runs a snippet once per element (point, primitive or voxel). Attributes are bound as `@P` or with typed prefixes `f@ v@ i@ s@`, and `@elemnum` and `@numelem` give the element index and count ([VEX snippets](https://www.sidefx.com/docs/houdini/vex/snippets.html)).
- VEX "automatically supports threading and parallel computation". Geometry-creating calls are queued and applied after the loop ([VEX snippets](https://www.sidefx.com/docs/houdini/vex/snippets.html)).

**Good to use because:**
- VEX speed is "close to compiled C/C++ code", and "VEX SOPs typically run 10 or more times faster than a point SOP" ([VEX overview](https://www.sidefx.com/docs/houdini/vex/index.html)).
- A per-element snippet needs no loop or indexing boilerplate ([VEX snippets](https://www.sidefx.com/docs/houdini/vex/snippets.html)).
- Flat-array bulk access maps well to numpy ([hou.Geometry](https://www.sidefx.com/docs/houdini/hom/hou/Geometry.html)).

**Bad to use because:**
- Long Python cooks must call `hou.updateProgressAndCheckForInterrupt()` themselves so the user can cancel ([Python SOP docs](https://www.sidefx.com/docs/houdini/hom/pythonsop.html)).
- Setting node parameters from a Python SOP "creates broken dependencies" ([Python SOP docs](https://www.sidefx.com/docs/houdini/hom/pythonsop.html)).
- The Python SOP docs give no speed comparison with VEX ([Python SOP docs](https://www.sidefx.com/docs/houdini/hom/pythonsop.html)).

**Numbers:**
| property | value | source |
|---|---|---|
| VEX vs compiled code | "performance close to compiled C/C++ code" | [VEX overview](https://www.sidefx.com/docs/houdini/vex/index.html) |
| VEX SOP vs Point SOP | "10 or more times faster" | [VEX overview](https://www.sidefx.com/docs/houdini/vex/index.html) |
| VEX COP vs Pixel Expression COP | "1000's of times faster" | [VEX overview](https://www.sidefx.com/docs/houdini/vex/index.html) |

**Take for Studio:**
- Offer two modes. A per-element mode works like a wrangle (Studio's Expression node already covers much of this). A whole-list mode hands the script bulk arrays.
- Make the fast path in Python flat numpy arrays (coordinates, radii, kinds, ids), not one Python object per shape.
- Give scripts a cheap "check cancel" call. The host should also be able to kill a runaway script.

### Blender Python (bpy) and Sverchok SNLite (Blender 5.2 API and manual)
**How it works:**
- `foreach_get` and `foreach_set` give "Fast access to a basic-type attribute within a collection", reading into or writing from a flat "sequence or buffer" ([bpy_prop_collection](https://docs.blender.org/api/current/bpy.types.bpy_prop_collection.html)).
- Auto-running scripts in .blend files is off by default, "since Python does not restrict what a script can do" ([Scripting and Security](https://docs.blender.org/manual/en/latest/advanced/scripting/security.html)).
  - The blocked items are registered text blocks and drivers.
  - Users can trust folders, for example "all paths except for the download directory".
- A Sverchok SNLite node declares its sockets in header lines: `in socketname type default=x nested=n` and `out socketname type` ([SNLite docs](https://github.com/nortikin/sverchok/blob/master/docs/nodes/script/script1_lite.rst)).
  - Socket types include vertices `v`, strings or lists `s`, matrices `m`, curves `C`, surfaces `S` and solids `So`.
  - `nested=0/1/2` picks how deep the input list is unwrapped.
  - Outputs are read "At the end of your code".

**Good to use because:**
- Declaring sockets in the script header keeps the node and the code in one text ([SNLite docs](https://github.com/nortikin/sverchok/blob/master/docs/nodes/script/script1_lite.rst)).
- The trust model prompts per file and supports trusted folders ([Blender manual](https://docs.blender.org/manual/en/latest/advanced/scripting/security.html)).

**Bad to use because:**
- SNLite is "intended for quick, non serious, experimentation" ([SNLite docs](https://github.com/nortikin/sverchok/blob/master/docs/nodes/script/script1_lite.rst)).
- There is no sandbox. Blender's only defence is not running scripts until the user trusts them ([Blender manual](https://docs.blender.org/manual/en/latest/advanced/scripting/security.html)).

**Numbers:**
| property | value | source |
|---|---|---|
| API version read | Blender 5.2 | [best practice page footer](https://docs.blender.org/api/current/info_best_practice.html) |
| Published speed figures | none found on the pages read | [best practice](https://docs.blender.org/api/current/info_best_practice.html) |

**Take for Studio:**
- Let the script header declare inputs and outputs. The node UI and the header should stay in sync in both directions.
- When a file or library flow contains scripts, ask the user to trust it, and allow trusted folders.

### pyRevit (v7.0.0, Oct 2026)
**How it works:**
- pyRevit is a "Rapid Application Development (RAD) Environment for Autodesk Revit®". Addons can be written in IronPython or CPython, and C# and VB.Net are also supported. It is GPL-3.0 ([README](https://github.com/pyrevitlabs/pyRevit)).
- In March 2024, pyRevit bundled "CPython 3.8", and maintainers kept only "ipy 2711 and cpy 385". In October 2024, a maintainer said WIP pyRevit 5 "should run CPython 3.12 just fine" without `pyrevit.forms` ([issue #2124](https://github.com/pyrevitlabs/pyRevit/issues/2124)).
- In 2023, a request for CPython 3.10 or 3.11 got the answer "Not possible at the moment". The maintainer suggested running code through `subprocess` instead ([issue #1937](https://github.com/pyrevitlabs/pyRevit/issues/1937)).
- v7.0.0 shares one session engine across startup scripts and adds an IronPython console ([releases](https://github.com/pyrevitlabs/pyRevit/releases)).

**Good to use because:**
- The maintainers' fallback for newer Python was a separate process, which is the same pattern recommended here ([issue #1937](https://github.com/pyrevitlabs/pyRevit/issues/1937)).

**Bad to use because:**
- A user says the in-process CPython engine "crashed often", and the maintainers would not make it the default ([issue #2124, user comment](https://github.com/pyrevitlabs/pyRevit/issues/2124)).
- GPL-3.0 code cannot be embedded in closed software ([README](https://github.com/pyrevitlabs/pyRevit)).
- The official tutorials are Notion pages that would not render for me, so they are not verified ([Notion page](https://pyrevitlabs.notion.site/Create-Your-First-CPython-Command-b8a7718c554645d1a18454c0b363e3c9)).

**Numbers:**
| property | value | source |
|---|---|---|
| Bundled engines (Mar 2024) | IronPython 2.7.11, CPython 3.8.5 | [issue #2124](https://github.com/pyrevitlabs/pyRevit/issues/2124) |
| Latest release | v7.0.0 (06 Oct) | [releases](https://github.com/pyrevitlabs/pyRevit/releases) |

**Take for Studio:**
- Plan to upgrade the bundled Python regularly. An in-process CPython that people say "crashed often" is a warning.

### TouchDesigner Python (docs read 2026-11-01)
**How it works:**
- "The current version of Python shipped with TouchDesigner is 3.11". Python is used in scripts, expressions and the textport ([Python page](https://docs.derivative.ca/Python)).
- To add external packages, users install them into a parallel Python 3.11 and add the path in Preferences, `PYTHONPATH`, or `sys.path` in an Execute DAT ([Python page](https://docs.derivative.ca/Python)).
- The Script SOP keeps its callbacks in a DAT: `cook(scriptOP)`, `setupParameters()` and `onPulse(par)` ([Script SOP](https://docs.derivative.ca/Script_SOP), last edited 16 Nov 2021, about 5 years old).
- "Python threads don't have access to TouchDesigner objects" ([Python page](https://docs.derivative.ca/Python)).

**Good to use because:**
- Keeping callbacks in a DAT makes the code a visible part of the network ([Script SOP](https://docs.derivative.ca/Script_SOP)).

**Bad to use because:**
- The app's own tools rely on its bundled NumPy and OpenCV. Loading other versions is "at your own risk" ([Python page](https://docs.derivative.ca/Python)).

**Numbers:**
| property | value | source |
|---|---|---|
| Bundled Python | 3.11 | [Python page](https://docs.derivative.ca/Python) |

**Take for Studio:**
- Keep Studio's own Python packages, if any, apart from user packages. A user `pip install` must never be able to break a built-in node.

### Unreal Editor Python (UE 5.8 docs)
**How it works:**
- "the Python environment is only available in the Unreal Editor, not when your Project is running" ([UE docs](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python)).
- "The Python Editor Script Plugin contains an embedded version of Python 3.11.8". Switching Python with `UE_PYTHON_DIR` needs an engine rebuild ([UE docs](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python)).
- The `unreal` module "is not pre-generated; it automatically reflects whatever is available in Blueprints" ([UE docs](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python)).
- "while the Unreal Editor is running a Python script, its UI becomes blocked". `unreal.ScopedSlowTask` shows progress. The feature is labelled Experimental ([UE docs](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python)).

**Good to use because:**
- The scripting API comes from the existing type registry, so it never drifts from the editor ([UE docs](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python)).

**Bad to use because:**
- Scripts block the UI ([UE docs](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python)).

**Numbers:**
| property | value | source |
|---|---|---|
| Embedded Python | 3.11.8 | [UE docs](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python) |

**Take for Studio:**
- Generate the Python-side shape and type stubs from Studio's type registry at build time. Studio has no runtime reflection, so they must be generated, not reflected.
- Never run a script on the UI thread.

### C# scripting hosts: Roslyn scripting API (Microsoft.CodeAnalysis.CSharp.Scripting 5.9.0, Aug 2026)
**How it works:**
- You call `CSharpScript.EvaluateAsync(...)`, or `CSharpScript.Create<T>(code, globalsType: typeof(Globals))` then `.Compile()` and `RunAsync(globals)`. Inputs are fields on a host "globals" object ([Scripting API samples](https://github.com/dotnet/roslyn/blob/main/docs/wiki/Scripting-API-Samples.md)).
- `script.CreateDelegate()` returns a delegate you can call again and again, and it "doesn't hold compilation resources ... alive" ([samples](https://github.com/dotnet/roslyn/blob/main/docs/wiki/Scripting-API-Samples.md)).
- The globals type "has to be defined in an assembly loaded from a file" ([samples](https://github.com/dotnet/roslyn/blob/main/docs/wiki/Scripting-API-Samples.md)).
- The scripting APIs "can't be used within Universal Windows Applications and .NET Native", because those models do not support loading runtime-generated code ([samples](https://github.com/dotnet/roslyn/blob/main/docs/wiki/Scripting-API-Samples.md)).

**Good to use because:**
- It gives you full C#, and the compiled delegate can be reused across runs ([samples](https://github.com/dotnet/roslyn/blob/main/docs/wiki/Scripting-API-Samples.md)).
- MIT licence (measured: NuGet catalog `licenseExpression`).

**Bad to use because:**
- It fails when the app is published with Native AOT: "Operation is not supported on this platform". The issue has been open since 2024-05-24 and sits in the Backlog milestone ([roslyn #73689](https://github.com/dotnet/roslyn/issues/73689)).
- "Every CSharpScript.EvaluateAsync() call generates a new assembly that does not get unloaded". The Roslyn team said "Unloading is currently not supported" (tmat, 2020). The issue is still open ([roslyn #41722](https://github.com/dotnet/roslyn/issues/41722)).
- The first call is slow. A third-party wrapper documents that loading the compiler "can take a significant time to complete (in some cases up to 4 seconds)" ([CS-Script docs](https://www.cs-script.net/cs-script.core/help/html/bd7ee734-896b-4281-ce08-71d867253ae4.htm)).

**Numbers:**
| property | value | source |
|---|---|---|
| First evaluation | "up to 4 seconds" (third party) | [CS-Script docs](https://www.cs-script.net/cs-script.core/help/html/bd7ee734-896b-4281-ce08-71d867253ae4.htm) |
| Roslyn DLLs, net10.0 | Microsoft.CodeAnalysis.dll 3,103,056 B; Microsoft.CodeAnalysis.CSharp.dll 7,079,208 B; Scripting DLLs 34,600 B + 137,512 B; total 10,354,376 B (about 10.4 MB) | measured: downloaded the 5.9.0 nupkgs from `api.nuget.org/v3-flatcontainer` and read `lib/net10.0` sizes with `zipfile` |
| Latest version | 5.9.0, published 2026-08-17 | measured: NuGet registration API |

**Take for Studio:**
- Roslyn cannot run inside the AOT Studio process. If Studio offers C#, Roslyn runs in a helper process (see Part 2).

### Other C# hosts: dotnet-script, CS-Script, LINQPad, Rhino 8 C# (read 2026-11-01)
**How it works:**
- dotnet-script ([README](https://github.com/dotnet-script/dotnet-script)):
  - Packages are declared with `#r "nuget: AutoMapper, 6.1.0"` and files are included with `#load`.
  - It recompiles only when a SHA256 hash of the source changes.
  - Scripts can be debugged in VS Code.
  - It needs a .NET 8, 9 or 10 SDK. MIT licence.
- CS-Script ([wiki](https://github.com/oleg-shilo/cs-script/wiki/Choosing-Compiler-Engine)):
  - It has three engines: `dotnet`, `csc` and `roslyn`.
  - Roslyn "is the only engine that does not require SDK installed", but it cannot reference NuGet packages.
  - For hosted scripts, "Caching is disabled by default".
  - The `csc` engine uses an out-of-process build service on port 17001.
- LINQPad ([How LINQPad works](https://www.linqpad.net/HowLINQPadWorks.aspx)):
  - It "compiles your scripts using the Microsoft Roslyn libraries".
  - "For each query, LINQPad creates a separate server, which ... runs in its own process". This "prevents scripts from interfering with each other (or the UI)" and "allows LINQPad to safely cancel a query".
  - Messages travel over a custom layer on Windows shared memory.
- Rhino 8 C# compiles and caches scripts inside Rhino, and supports `#r "nuget:"` and the debugger ([GH C# guide](https://developer.rhino3d.com/guides/scripting/scripting-gh-csharp/), [C# guide](https://developer.rhino3d.com/guides/scripting/scripting-csharp/)).

**Good to use because:**
- LINQPad shows the model Studio needs: a compile-and-run server process per query, a shared-memory transport, and safe cancel ([How LINQPad works](https://www.linqpad.net/HowLINQPadWorks.aspx)).
- dotnet-script's hash-based compile cache and `#r "nuget:"` syntax are a common convention ([README](https://github.com/dotnet-script/dotnet-script)).

**Bad to use because:**
- dotnet-script and the CS-Script `dotnet` and `csc` engines need a full .NET SDK ([dotnet-script README](https://github.com/dotnet-script/dotnet-script), [CS-Script wiki](https://github.com/oleg-shilo/cs-script/wiki/Choosing-Compiler-Engine)). The SDK zip is about 300 MB (measured below).
- LINQPad is commercial, and "The NuGet package manager is available only in the Developer and Premium editions" ([FAQ](https://www.linqpad.net/FAQ.aspx)).

**Numbers:**
| property | value | source |
|---|---|---|
| dotnet-script latest | 2.0.1, 2026-05-28, MIT | measured: NuGet registration API |
| CS-Script latest | 4.14.13, 2026-10-23, MIT, netstandard2.0 | measured: NuGet catalog |
| .NET SDK 10.0.403 win-x64 zip | 300,745,255 B | measured: HTTP HEAD on `builds.dotnet.microsoft.com` URL from the `release-metadata/10.0/releases.json` file |

**Take for Studio:**
- Copy LINQPad's design: a separate compile and run process, cancel by killing it, and a fast transport.
- Use the dotnet-script syntax `#r "nuget: Name, Version"` and its hash-based compile cache.

---

## Part 2. Options for a .NET 10 Native AOT host

### The constraint: Native AOT limits (Microsoft Learn, updated 2026-07-27)
**How it works:**
- Native AOT apps have these limits ([Native AOT overview](https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/)):
  - "No dynamic loading, for example, `Assembly.LoadFile`."
  - "No runtime code generation, for example, `System.Reflection.Emit`."
  - Trimming is required.
  - "System.Linq.Expressions always use their interpreted form".
- `DllImport` uses an IL stub that is "generated at runtime", so it "isn't available for ahead-of-time (AOT) compiler" scenarios. `[LibraryImport]` (from .NET 7) generates the marshalling code at compile time ([P/Invoke source generation](https://learn.microsoft.com/en-us/dotnet/standard/native-interop/pinvoke-source-generation)).
- Native hosting with `nethost` and `hostfxr` "only support framework-dependent deployments", and "Only one runtime can be loaded inside a single process" ([Write a custom .NET host](https://learn.microsoft.com/en-us/dotnet/core/tutorials/netcore-hosting)). I found no Microsoft page on hosting CoreCLR inside a Native AOT process. Not verified.
- .NET 11 adds an interpreter "to bring CoreCLR to platforms that do not support runtime code generation (notably for WASM and iOS)". In Preview 1 it was "not yet ready for general use" ([.NET 11 Preview 1 runtime notes](https://github.com/dotnet/core/blob/main/release-notes/11.0/preview/preview1/runtime.md)).
- .NET has no in-process permission sandbox: "Code access security (CAS) is an unsupported, legacy technology" ([SYSLIB0003](https://learn.microsoft.com/en-us/dotnet/fundamentals/syslib-diagnostics/syslib0003)).

**Good to use because:**
- CPython is a C library. Calling its C API through `[LibraryImport]` is fully AOT-safe ([P/Invoke source generation](https://learn.microsoft.com/en-us/dotnet/standard/native-interop/pinvoke-source-generation)).

**Bad to use because:**
- No C# compile-and-load can happen inside the AOT process ([Native AOT overview](https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/)).
- No managed sandbox exists inside the process ([SYSLIB0003](https://learn.microsoft.com/en-us/dotnet/fundamentals/syslib-diagnostics/syslib0003)).

**Numbers:**
| property | value | source |
|---|---|---|
| LibraryImport generator | since .NET 7 | [P/Invoke source generation](https://learn.microsoft.com/en-us/dotnet/standard/native-interop/pinvoke-source-generation) |
| CoreCLR runtimes per process (hosting API) | 1 | [custom host](https://learn.microsoft.com/en-us/dotnet/core/tutorials/netcore-hosting) |

**Take for Studio:**
- Python can live in the Studio process because it is native code, but it should not (see the crash and sandbox rows below).
- C# user code can only run out of process, or through an interpreter.

### Python option (a1): embed CPython through its C API with your own LibraryImport bindings (Python 3.15.2 docs)
**How it works:**
- The host follows the embedding docs ([Embedding Python](https://docs.python.org/3/extending/embedding.html)):
  - Initialise with `PyConfig` and `Py_InitializeFromConfig()`.
  - Load a module with `PyImport_Import()`.
  - Call a function with `PyObject_CallObject()`.
  - Manage reference counts by hand.
- The Stable ABI lets a binary work across Python versions. "On Windows, extensions that use a Stable ABI should be linked against `python3.dll`", and the Stable ABI "works the same way for all uses of the API, for example embedding". `abi3` covers only non-free-threaded builds ([C API Stability](https://docs.python.org/3/c-api/stable.html)).
- A thread that Python did not create must first "register these threads with the interpreter by creating a new thread state and attaching it". `PyGILState_Ensure` is soft-deprecated in 3.15 ([Thread states and the GIL](https://docs.python.org/3/c-api/threads.html)).
- Restarting the interpreter is unreliable. After `Py_FinalizeEx()`, "Dynamically loaded extension modules loaded by Python are not unloaded" and "Some extensions may not work properly if their initialization routine is called more than once" ([Interpreter lifecycle](https://docs.python.org/3/c-api/interp-lifecycle.html)).
- Sub-interpreters (Python 3.14 and later) do not share the GIL. But "not all PyPI packages support use in multiple interpreters yet", and you should "not use multiple interpreters in security-sensitive situations" ([concurrent.interpreters](https://docs.python.org/3/library/concurrent.interpreters.html)).

**Good to use because:**
- No reflection is needed, and the cost of a call is one native call per C API function ([P/Invoke source generation](https://learn.microsoft.com/en-us/dotnet/standard/native-interop/pinvoke-source-generation)).
- Large arrays can be shared without copying inside one process, through the buffer protocol or the Arrow C Data Interface ("zero-copy sharing of Arrow data between independent runtimes and components running in the same process", [Arrow C Data Interface](https://arrow.apache.org/docs/format/CDataInterface.html)).
- Users get real CPython with C-extension packages such as numpy ([Rhino Python guide](https://developer.rhino3d.com/guides/scripting/scripting-python/)).

**Bad to use because:**
- The script shares Studio's process and memory, as the Rhino docs say of their in-process design ([pyvenvs guide](https://developer.rhino3d.com/guides/scripting/advanced-pyvenvs/)). So a crash in a C extension or in user code takes Studio down. This is my inference from the process model. I found no doc saying it in these words.
- After `pip install`, you cannot reliably restart the interpreter to load new packages ([Interpreter lifecycle](https://docs.python.org/3/c-api/interp-lifecycle.html)).
- There is no sandbox. Audit hooks "are not suitable for implementing a 'sandbox' ... malicious code can trivially disable or bypass hooks" ([sys docs](https://docs.python.org/3/library/sys.html)).
- Debugging is fiddly. In an embedded host, `sys.executable` is the host exe, so debugpy relaunches the host. The fix is `debugpy.configure(python="...")` ([debugpy #1097](https://github.com/microsoft/debugpy/issues/1097)).

**Numbers:**
| property | value | source |
|---|---|---|
| Published per-call cost, embedded CPython from .NET | none found from a primary source; see R21M measurements | n/a |
| python315.dll size | 7,910,624 B | measured: `zipfile` listing of `python-3.15.2-embed-amd64.zip` |
| Stable ABI since | Python 3.2 (`abi3`) | [C API Stability](https://docs.python.org/3/c-api/stable.html) |

**Take for Studio:**
- This is technically clean for AOT, but it gives no crash isolation and no restart. Use it, if at all, only as a later "fast mode" for trusted, numpy-only scripts.

### Python option (a2): CSnakes (stable 1.2.1, Aug 2025; 2.0.0-beta.350, Jul 2026)
**How it works:**
- CSnakes is "a .NET Source Generator and Runtime that you can use to embed Python code and libraries into your C#.NET Solution". It "Uses Python's C-API for fast invocation of Python code directly in the .NET process" ([README](https://github.com/tonybaloney/CSnakes)).
- Native AOT works only with source-generated bindings. "Manual Python binding using the runtime API directly is not supported in AOT scenarios", and `result.As<MyType>()` is marked "This won't work in AOT". "The published application will still require a Python runtime" ([Native AOT page](https://tonybaloney.github.io/CSnakes/v1/advanced/native-aot/)).
- Python is found in one of three ways ([installation](https://tonybaloney.github.io/CSnakes/v1/getting-started/installation/), [environments](https://tonybaloney.github.io/CSnakes/v1/user-guide/environments/)):
  - `FromRedistributable()`, which "will automatically download Python 3.12".
  - An environment variable.
  - Conda.
  Packages come from `.WithPipInstaller()` or `.WithUvInstaller()` into a virtual environment.
- NumPy arrays are exposed as `Span<T>`, `ReadOnlySpan<T>`, 2D spans and (.NET 9) `TensorSpan`. The span "is writeable", so C# edits show up in Python ([Buffers](https://tonybaloney.github.io/CSnakes/v1/user-guide/buffers/)).

**Good to use because:**
- It is the only binding I found whose own docs claim Native AOT support ([Native AOT page](https://tonybaloney.github.io/CSnakes/v1/advanced/native-aot/)).
- Bulk data can cross as buffers, and the docs call a numpy array "the fastest way to pass large amounts of data to Python" ([Performance](https://tonybaloney.github.io/CSnakes/v1/advanced/performance/)).
- MIT licence ([README](https://github.com/tonybaloney/CSnakes)).
- It was made by Microsoft staff. On .NET calls the author "Anthony from the Python Cloud Advocacy team at Microsoft" and the project "his latest experiment" ([Microsoft Learn show](https://learn.microsoft.com/en-us/shows/on-dotnet/a-sneak-peek-at-csnakes-embed-python-code-in-dotnet-apps)). It lives on a personal GitHub account, so I would not call it an official Microsoft product.

**Bad to use because:**
- Lists cost a lot to pass. "functions which take lists and dictionaries as arguments are not [zero-copy]; they are copied", one Python object per element. Marshalling value types is "a relatively expensive operation" ([Performance](https://tonybaloney.github.io/CSnakes/v1/advanced/performance/)).
- Bindings are generated at build time from `.py` files listed as AdditionalFiles ([Native AOT page](https://tonybaloney.github.io/CSnakes/v1/advanced/native-aot/)). So scripts that users write at run time cannot get typed bindings. Studio would ship a fixed runner module that runs user code (my inference).
- It has no source generation for custom classes or dataclasses ([Limitations](https://tonybaloney.github.io/CSnakes/v1/community/limitations/)).
- Being in-process, it has the same crash and sandbox problems as option (a1).
- Sources conflict on support:
  - The README says "Supports .NET 8 and 9" and "Python 3.9-3.13", but elsewhere it says "3.8-3.13" ([README](https://github.com/tonybaloney/CSnakes)).
  - The 2.0 beta adds net10.0 (measured below).
  - A third-party comparison table says CSnakes Native AOT is "Not supported" ([DotNetPy COMPARISON.md, third party](https://github.com/rkttu/dotnetpy/blob/main/docs/COMPARISON.md)). This contradicts CSnakes' own docs.

**Numbers:**
| property | value | source |
|---|---|---|
| Latest stable | 1.2.1, 2025-08-08, targets net8.0 and net9.0 | measured: NuGet registration API |
| Latest prerelease | 2.0.0-beta.350, 2026-07-15, targets net10.0, net8.0, net9.0 | measured: NuGet registration API |
| Total downloads (CSnakes.Runtime) | 527,506 | measured: NuGet search API, 2026-11-01 |
| nupkg size (2.0.0-beta.350) | 537,396 B | measured: HTTP HEAD on flat container |
| Published per-call timings | none ("The page gives no timing or benchmark figures") | [Performance](https://tonybaloney.github.io/CSnakes/v1/advanced/performance/) |

**Take for Studio:**
- If Studio ever embeds Python, CSnakes' pattern fits AOT:
  - a fixed, build-time runner module;
  - user code passed in as text;
  - shapes passed as numpy buffers, not lists.
- CSnakes 2.x is still beta. Check its net10.0 support before relying on it.

### Python option (a3): pythonnet, Python.Included, Python.Deployment (pythonnet 3.2.1, Oct 2026)
**How it works:**
- pythonnet runs CPython beside the CLR. It is "Compatible and tested with Python 3.11 through 3.15", supports free-threaded builds from 3.14, and uses the MIT licence ([pythonnet docs](https://pythonnet.github.io/pythonnet/)).
- It uses `System.Reflection.Emit`:
  - `ClassDerived.cs` calls `DefineDynamicAssembly`, `DefineType` and `GetILGenerator` to build .NET subclasses for Python classes ([source](https://github.com/pythonnet/pythonnet/blob/master/src/runtime/Types/ClassDerived.cs)).
  - A GitHub code search also finds `Reflection.Emit` in `DelegateManager.cs` and `Util/CodeGenerator.cs` (measured: `gh api search/code -f q='"System.Reflection.Emit" repo:pythonnet/pythonnet'`).
- Issue "Removal of Reflection.Emit" was opened in 2019, citing Unity's AOT (il2cpp). It is still open ([pythonnet #997](https://github.com/pythonnet/pythonnet/issues/997)).
- Python.Included bundles `python-3.13.0-embed-amd64.zip` in its assembly and unpacks it to the user's home folder on first run. It "only implements deployment on top of" pythonnet, and "The code is stable for Windows" ([README](https://github.com/henon/Python.Included)).

**Good to use because:**
- It is mature, and Rhino 8 and 9 and Dynamo build on it ([Rhino forum](https://discourse.mcneel.com/t/rhino-beta-feature-python-3-13/205209), [Dynamo blog](https://dynamobim.org/pythonnet3-a-new-dynamo-python-to-fix-everything/)).

**Bad to use because:**
- It uses Reflection.Emit, which Native AOT forbids ([Native AOT overview](https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/), [ClassDerived.cs](https://github.com/pythonnet/pythonnet/blob/master/src/runtime/Types/ClassDerived.cs)). I found no pythonnet doc that claims AOT support.
- Calls into .NET-heavy code are slow ([Rhino forum, user](https://discourse.mcneel.com/t/python-3-about-10x-slower-than-old-python-component/215094)).
- Major versions break user scripts ([Dynamo migration guide](https://dynamobim.org/dynamo-pythonnet3-upgrade-a-practical-guide-to-migrating-your-dynamo-graphs/)).
- Python.Included's licence is unclear. The README says PSF, but the repo sidebar shows MIT ([README](https://github.com/henon/Python.Included)).

**Numbers:**
| property | value | source |
|---|---|---|
| pythonnet latest | 3.2.1, 2026-10-08; total downloads 3,399,434 | measured: NuGet registration and search APIs |
| pythonnet nupkg | 230,640 B | measured: HTTP HEAD |
| Python.Included latest | 3.13.6, 2026-07-07; nupkg 10,950,962 B | measured: NuGet API, HTTP HEAD |
| Python.Deployment latest | 2.0.7, 2026-07-07, MIT | measured: NuGet registration API |

**Take for Studio:**
- Do not use pythonnet in the AOT host. Studio does not need Python to call back into .NET objects. It only needs data in and data out.

### Python option (b): a separate Python process over a pipe (recommended default)
**How it works:**
- Studio starts a private `python.exe`, from the embeddable package or a uv-managed install. It runs a fixed worker script that loops: read a request frame, run the user code, write a response frame. Studio talks to it over stdin/stdout or a named pipe.
  - pyRevit's maintainers suggest the same subprocess route ([pyRevit #1937](https://github.com/pyrevitlabs/pyRevit/issues/1937)).
  - Hops uses a separate process for the same reasons ([Hops guide](https://developer.rhino3d.com/guides/compute/hops-component/)).
- Frames can be encoded several ways:
  - MessagePack. MessagePack-CSharp v4 preview claims "full Native AOT support" through a source generator ([MessagePack-CSharp](https://github.com/MessagePack-CSharp/MessagePack-CSharp)).
  - Apache Arrow IPC. Arrow .NET supports IPC "File" and "Stream" ([arrow-dotnet](https://github.com/apache/arrow-dotnet)).
  - gRPC. It "supports .NET native ahead-of-time (AOT) in .NET 8" ([gRPC and Native AOT](https://learn.microsoft.com/en-us/aspnet/core/grpc/native-aot)).
- Windows can contain the worker ([Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects), [AppContainer isolation](https://learn.microsoft.com/en-us/windows/win32/secauthz/appcontainer-isolation)):
  - A Job object limits working set and priority. With `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, closing the last job handle "terminates all associated processes".
  - An AppContainer adds file, network and process isolation.
- To debug, the worker calls `debugpy.listen()` and then `debugpy.wait_for_client()`, and the user attaches VS Code ([debugpy README](https://github.com/microsoft/debugpy)). Because the worker is a real `python.exe`, the embedded-host `sys.executable` problem does not apply ([debugpy #1097](https://github.com/microsoft/debugpy/issues/1097)).

**Good to use because:**
- Crash isolation: a numpy segfault or a `while True` kills only the worker. Studio can kill the worker on timeout or cancel, as LINQPad does ([How LINQPad works](https://www.linqpad.net/HowLINQPadWorks.aspx)).
- Fresh packages are easy: restarting the worker loads them. This avoids the `Py_FinalizeEx` caveats ([Interpreter lifecycle](https://docs.python.org/3/c-api/interp-lifecycle.html)).
- Each flow or library tool can have its own environment and Python version, which avoids Rhino's one-process conflicts ([pyvenvs guide](https://developer.rhino3d.com/guides/scripting/advanced-pyvenvs/)).
- It is the only path to a real sandbox, through OS isolation: AppContainer plus a Job object ([AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/appcontainer-isolation)).
- The Studio side has no reflection, so it is AOT-clean: just pipes and source-generated serializers ([gRPC AOT](https://learn.microsoft.com/en-us/aspnet/core/grpc/native-aot), [MessagePack-CSharp](https://github.com/MessagePack-CSharp/MessagePack-CSharp)).

**Bad to use because:**
- Each call pays for IPC and serialisation, and the first call pays for process start. Published figures:
  - An old third-party Linux benchmark measured pipes at "162,441 msg/s" for 100-byte messages ([ipc-bench](https://github.com/goldsborough/ipc-bench)).
  - gRPC publishes only a live dashboard, with no latency figures on its page ([gRPC benchmarking](https://grpc.io/docs/guides/benchmarking/), last modified 2022).
- Large geometry must be serialised, or put in shared memory. The Arrow C Data Interface is for the same process only ([Arrow C Data Interface](https://arrow.apache.org/docs/format/CDataInterface.html)).
- Python cannot reach live Studio objects directly. Everything is data in and data out. This is also a design benefit.

**Numbers:**
| property | value | source |
|---|---|---|
| Pipe message rate, 100 B | 162,441 msg/s, about 6.2 µs per message (derived as 1/162,441 s); Ubuntu 20.04, i5-4590S; third party | [ipc-bench](https://github.com/goldsborough/ipc-bench) |
| Shared memory message rate, 100 B | 4,702,557 msg/s; same setup | [ipc-bench](https://github.com/goldsborough/ipc-bench) |
| MessagePack IntKey deserialise | 72.67 ns vs 455.28 ns for MsgPackCliArray | [MessagePack-CSharp README](https://github.com/MessagePack-CSharp/MessagePack-CSharp) |
| MessagePack NuGet | 3.1.4 stable, MIT; 4.0.0-preview.2 newest | measured: NuGet catalog and registration |
| debugpy wheel, cp314 win_amd64 | 5,397,429 B, v1.8.22, MIT | measured: PyPI JSON API |
| pyarrow wheel, cp314 win_amd64 | 29,237,858 B, v26.0.0, Apache-2.0 | measured: PyPI JSON API |

**Take for Studio:**
- Make this the default:
  - One warm worker per Python environment, started on first use and kept alive.
  - Requests carry struct-of-arrays buffers.
  - A Job object kills the worker with Studio, and a per-call timeout kills a stuck worker.
- Keep a pool size setting, as in Hops ([Hops guide](https://developer.rhino3d.com/guides/compute/hops-component/)).

### Python option (c): IronPython 3 (3.4.2, Dec 2024)
**How it works:**
- "The current target is Python 3.4, although features and behaviors from later versions may be included". It targets .NET Framework 4.6.2, .NET Standard 2.0, .NET 8.0 and .NET 10.0, under Apache-2.0 ([README](https://github.com/IronLanguages/ironpython3)).
- It runs on the Dynamic Language Runtime. A contributor wrote that "almost none of IronPython is AOT safe". The proposal to mark the AOT-unsafe code was closed as "not planned" in March 2025 ([ironpython3 #1896](https://github.com/IronLanguages/ironpython3/issues/1896)).
- numpy, pandas and scipy are unsupported because IronPython "does not currently support packages which are CPython extension modules" ([Package compatibility wiki, Apr 2025](https://github.com/IronLanguages/ironpython3/wiki/Package-compatibility)).

**Good to use because:**
- It is pure .NET, so calls into .NET are fast, as Rhino users see with IronPython ([Rhino Python guide](https://developer.rhino3d.com/guides/scripting/scripting-python/)).

**Bad to use because:**
- It cannot run in a Native AOT host ([#1896](https://github.com/IronLanguages/ironpython3/issues/1896), [Native AOT overview](https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/)).
- The language level is 3.4, with no numpy ([README](https://github.com/IronLanguages/ironpython3), [wiki](https://github.com/IronLanguages/ironpython3/wiki/Package-compatibility)).
- Dynamo calls IronPython 2.7 obsolete, and the Dynamo team no longer maintains its IronPython packages ([Dynamo 4.0](https://dynamobim.org/dynamo-core-4-0-release/)).

**Numbers:**
| property | value | source |
|---|---|---|
| Latest release | 3.4.2, 2024-12-20 | measured: NuGet registration API |
| nupkg size | 6,763,733 B | measured: HTTP HEAD |

**Take for Studio:**
- Do not use it.

### Python option (d): python.org embeddable package, plus uv or pip for packages (Python 3.15.2, uv docs March 2026)
**How it works:**
- The embeddable package "is a ZIP file containing a minimal Python environment. It is intended for acting as part of another application" ([Using Python on Windows](https://docs.python.org/3/using/windows.html)):
  - It is "(almost) fully isolated from the user's system".
  - The standard library ships as `.pyc` files in a ZIP.
  - Tcl/Tk, pip and the docs "are not included".
  - A `._pth` file restricts the search paths.
  - "Using pip to manage dependencies as for a regular Python installation is not supported with this distribution".
  - It can be installed with `py install 3.15-embed --target=<directory>`.
- uv covers environments and packages ([uv docs](https://docs.astral.sh/uv/), [uv scripts guide](https://docs.astral.sh/uv/guides/scripts/)):
  - It is "10-100x faster" than pip and installs Python versions itself.
  - It reads inline script metadata (PEP 723).
  - "scripts must be explicitly locked using `uv lock`". `uv lock --script` writes a lock file such as `example.py.lock`.
- uv is dual-licensed MIT or Apache-2.0 ([uv repo](https://github.com/astral-sh/uv)).
- python-build-standalone, from Astral, provides "Self-contained, portable, high-performance Python distributions", Python 3.11 to 3.16, standard and free-threaded, under MPL-2.0 ([repo](https://github.com/astral-sh/python-build-standalone)).
- CPython's licence is the PSF License v2: a "nonexclusive, royalty-free, world-wide license" to distribute "Python alone or in any derivative version", provided the PSF notice is kept. It is GPL-compatible but not copyleft. Bundled OpenSSL 3 is Apache 2.0, and libffi and zlib have permissive licences ([History and License](https://docs.python.org/3/license.html)).

**Good to use because:**
- It is small, private and isolated from any Python the user has installed ([Windows docs](https://docs.python.org/3/using/windows.html)).
- uv plus PEP 723 plus a lock file gives each script reproducible dependencies. This matches Rhino's in-script `# r:` idea, but with locks ([uv scripts](https://docs.astral.sh/uv/guides/scripts/), [Rhino packages](https://developer.rhino3d.com/guides/scripting/advanced-packages/)).
- The licence is permissive ([license page](https://docs.python.org/3/license.html)).

**Bad to use because:**
- The embeddable package has no pip and "Virtual environments are not supported", which is why Dynamo users bootstrap pip by hand ([Dynamo wiki](https://github.com/DynamoDS/Dynamo/wiki/Customizing-Dynamo's-Python-3-installation)). Using uv with a full build, such as python-build-standalone, avoids this.
- Packages with C code are big. A numpy wheel is 12.7 MB and pyarrow is 29.2 MB (measured below).

**Numbers:**
| property | value | source |
|---|---|---|
| python-3.15.2-embed-amd64.zip | 13,740,486 B download; 26,496,099 B unpacked; 39 files | measured: HTTP HEAD and `zipfile` sum on the python.org/ftp file |
| python-3.14.10-embed-amd64.zip | 12,619,664 B | measured: HTTP HEAD |
| python-3.13.17-embed-amd64.zip | 11,441,267 B | measured: HTTP HEAD |
| Latest stable releases on the Windows page | 3.14.10 (Oct 25, 2026), 3.13.17 (Oct 21, 2026); 3.15.2 docs current | [python.org downloads](https://www.python.org/downloads/windows/), [docs](https://docs.python.org/3/license.html) |
| numpy 2.5.4 cp314 win_amd64 wheel | 12,703,552 B | measured: PyPI JSON API |
| shapely 2.2.0 cp314 win_amd64 wheel | 1,843,568 B | measured: PyPI JSON API |
| uv vs pip | "10-100x faster" (vendor claim) | [uv docs](https://docs.astral.sh/uv/) |

**Take for Studio:**
- Bundle one pinned CPython (embeddable, or a python-build-standalone build) for the worker. Add or ship uv to create one environment per script hash or per library flow from a PEP 723 header, and lock it.
- Show "Installing packages..." as a node state. Never install silently on file open without trust.

### Python sandboxing and security (cross-cutting)
**How it works:**
- Audit hooks are "not suitable for implementing a 'sandbox'. In particular, malicious code can trivially disable or bypass hooks" ([sys.addaudithook](https://docs.python.org/3/library/sys.html)).
- Sub-interpreters: "do not use multiple interpreters in security-sensitive situations" ([concurrent.interpreters](https://docs.python.org/3/library/concurrent.interpreters.html)).
- Blender disables auto-run "since Python does not restrict what a script can do" ([Blender manual](https://docs.blender.org/manual/en/latest/advanced/scripting/security.html)).
- Windows OS boundaries: an AppContainer "prevents the application from modifying files that it should not" and controls network access. Job objects enforce limits and kill-on-close ([AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/appcontainer-isolation), [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)).

**Good to use because:**
- OS-level isolation is real and documented ([AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/appcontainer-isolation)).

**Bad to use because:**
- There is no language-level sandbox in CPython or .NET ([sys](https://docs.python.org/3/library/sys.html), [SYSLIB0003](https://learn.microsoft.com/en-us/dotnet/fundamentals/syslib-diagnostics/syslib0003)).

**Numbers:**
| property | value | source |
|---|---|---|
| Sandbox inside CPython | none (official docs) | [sys docs](https://docs.python.org/3/library/sys.html) |

**Take for Studio:**
- Treat a script like an executable:
  - Ask for trust per file or library.
  - Show the script's packages and network use before the first run.
  - Run it in a separate process, with an optional AppContainer "safe mode".

### C# option (a): Roslyn scripting inside the AOT process
**How it works:**
- Roslyn compiles to an in-memory assembly and loads it. Native AOT has "No dynamic loading" and "No runtime code generation" ([Native AOT overview](https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/)).
- A user reports that `CSharpScript.EvaluateAsync` throws "Operation is not supported on this platform" when the app is published with AOT ([roslyn #73689](https://github.com/dotnet/roslyn/issues/73689)).

**Good to use because:**
- It would be simplest, if it worked. It does not.

**Bad to use because:**
- It is not possible under Native AOT ([#73689](https://github.com/dotnet/roslyn/issues/73689), [Native AOT overview](https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/)).

**Numbers:**
| property | value | source |
|---|---|---|
| Roslyn issue status | open, Backlog, since 2024-05-24 | [#73689](https://github.com/dotnet/roslyn/issues/73689) |

**Take for Studio:**
- Rule this out.

### C# options (b) and (c): compile and run in a separate JIT helper process
**How it works:**
- Studio ships a small, normal (JIT) .NET 10 helper, `ScriptHost.exe`. The helper:
  - compiles the user's C# with Roslyn;
  - loads it into a collectible `AssemblyLoadContext`;
  - runs it on data received over a named pipe;
  - unloads or recycles it.
  LINQPad runs "a separate server" process per query in the same way ([How LINQPad works](https://www.linqpad.net/HowLINQPadWorks.aspx)).
- Unloading is "cooperative". It finishes only when no thread is running the code and nothing outside holds references. Threads and static handles can block it ([Assembly unloadability](https://learn.microsoft.com/en-us/dotnet/standard/assembly/unloadability)). Recycling the helper process is the reliable fallback.
- Packages can use the `#r "nuget: Name, Version"` syntax, as dotnet-script does ([dotnet-script](https://github.com/dotnet-script/dotnet-script)) and Rhino does ([Rhino packages](https://developer.rhino3d.com/guides/scripting/advanced-packages/)).
- Debugging: the helper is ordinary CoreCLR, so standard .NET debuggers can attach. dotnet-script shows VS Code debugging of scripts ([dotnet-script](https://github.com/dotnet-script/dotnet-script)).
- Option (c), a JIT runtime inside Studio's process through `hostfxr`, is not documented for Native AOT hosts. The hosting API supports only framework-dependent apps and "Only one runtime can be loaded inside a single process" ([custom host](https://learn.microsoft.com/en-us/dotnet/core/tutorials/netcore-hosting)). Not verified, and it would give no crash isolation.

**Good to use because:**
- It gives full C#, NuGet, real debugging, crash isolation and cancel by kill ([How LINQPad works](https://www.linqpad.net/HowLINQPadWorks.aspx)).
- Studio itself stays fully AOT.

**Bad to use because:**
- The install grows by about 100 MB (measured below).
- The first compile is slow ("up to 4 seconds" per [CS-Script docs](https://www.cs-script.net/cs-script.core/help/html/bd7ee734-896b-4281-ce08-71d867253ae4.htm)).
- Generated assemblies must be unloaded or the process recycled ([roslyn #41722](https://github.com/dotnet/roslyn/issues/41722), [unloadability](https://learn.microsoft.com/en-us/dotnet/standard/assembly/unloadability)).
- Shape types must be shared through a contract assembly that both sides compile, and data crosses the pipe as serialised data.

**Numbers:**
| property | value | source |
|---|---|---|
| .NET 10.0.14 runtime, win-x64 zip | 36,971,047 B download; 80,659,791 B unpacked; 193 files | measured: HTTP HEAD and `zipfile` sum; URL from `builds.dotnet.microsoft.com/dotnet/release-metadata/10.0/releases.json` (latest 10.0.14, 2026-10-25) |
| Roslyn compiler DLLs (net10.0) | 10,354,376 B | measured (see Roslyn section) |
| Reference assemblies (Microsoft.NETCore.App.Ref 10.0.14) | 238 DLLs, 11,635,504 B unpacked; nupkg 7,189,223 B | measured: downloaded nupkg, `zipfile` sum |
| Helper total, framework files only | about 102.6 MB unpacked (80.66 + 10.35 + 11.64 MB) | computed from the three rows above |

**Take for Studio:**
- This is the only realistic way to run user C#. Ship it as an optional component so the base install stays small.

### C# option (d): interpreters
**How it works:**
- DynamicExpresso is "an interpreter for simple C# statements". It "doesn't generate assembly but it creates an expression tree on the fly". Its Limitations section says "for/foreach/while/do operators" are not supported. MIT licence ([README](https://github.com/dynamicexpresso/DynamicExpresso)).
- Under Native AOT, "System.Linq.Expressions always use their interpreted form, which is slower" ([Native AOT overview](https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/)). An expression-tree interpreter could therefore run in AOT. DynamicExpresso does not state AOT support, so this is not verified.
- The .NET 11 CoreCLR interpreter targets WASM and iOS and was "not yet ready for general use" in Preview 1 ([runtime notes](https://github.com/dotnet/core/blob/main/release-notes/11.0/preview/preview1/runtime.md)).
- I found no maintained full C# (statements, loops, classes) interpreter in the sources I read.

**Good to use because:**
- It works in-process with no helper ([README](https://github.com/dynamicexpresso/DynamicExpresso)).

**Bad to use because:**
- It handles expressions only, which Studio's Expression node and formula fields already cover. It is slower when interpreted ([Native AOT overview](https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/)).

**Numbers:**
| property | value | source |
|---|---|---|
| DynamicExpresso.Core latest | 2.19.2, 2025-05-26, MIT, netstandard2.0 | measured: NuGet catalog |

**Take for Studio:**
- Do not build C# scripting on an interpreter.

### Passing lists of shapes and attributes (design note)
**How it works:**
- Every fast host passes flat arrays, not objects:
  - Houdini has bulk float-array attribute access and numpy setters ([hou.Geometry](https://www.sidefx.com/docs/houdini/hom/hou/Geometry.html)).
  - Blender's `foreach_get` uses "flattened values" ([bpy_prop_collection](https://docs.blender.org/api/current/bpy.types.bpy_prop_collection.html)).
  - CSnakes maps numpy to `Span<T>` ([Buffers](https://tonybaloney.github.io/CSnakes/v1/user-guide/buffers/)).
- Per-element marshalling is what made Python slow in Dynamo and Rhino:
  - Dynamo's PythonNet3 moved to views with "collections are no longer copied" ([Dynamo guide](https://dynamobim.org/dynamo-pythonnet3-upgrade-a-practical-guide-to-migrating-your-dynamo-graphs/)).
  - Rhino added the "Avoid Marshalling" switches ([GH Python guide](https://developer.rhino3d.com/guides/scripting/scripting-gh-python/)).
  - CSnakes copies lists one element at a time ([Performance](https://tonybaloney.github.io/CSnakes/v1/advanced/performance/)).

**Good to use because:**
- Studio's exact lines and arcs pack into a few typed columns. A suggested layout:
  - `kind: uint8`
  - `x0, y0, x1, y1: float64`
  - `cx, cy, r, a0, a1: float64` (NaN when unused)
  - `id/lineage: int64`
  - one column per attribute
- Columns serialise once (MessagePack bin or Arrow IPC) and arrive in Python as numpy arrays. A thin `studio` Python module can wrap them as `Line` and `Arc` objects for readable code. This layout is my proposal, not taken from a source.

**Bad to use because:**
- Ragged data needs offsets arrays, which is harder for beginners. A convenience wrapper hides this.

**Numbers:**
| property | value | source |
|---|---|---|
| Lists passed to Python by CSnakes | one Python object per element (copied) | [Performance](https://tonybaloney.github.io/CSnakes/v1/advanced/performance/) |

**Take for Studio:**
- The contract is struct-of-arrays plus lineage ids. Item mode is just the host looping over rows, so the user never writes the loop.

---

## Summary table: options for Studio

| Option | One call (published) | Lists of shapes | Packages | Sandbox | Crash isolation | Debugging | Licence | Install size |
|---|---|---|---|---|---|---|---|---|
| Py (a1) own C API bindings in-process | no primary figure found | zero-copy buffers possible ([Arrow C Data](https://arrow.apache.org/docs/format/CDataInterface.html)) | uv/pip into venv; no clean restart ([lifecycle](https://docs.python.org/3/c-api/interp-lifecycle.html)) | none ([sys](https://docs.python.org/3/library/sys.html)) | none (same process) | debugpy with `configure(python=)` ([#1097](https://github.com/microsoft/debugpy/issues/1097)) | PSF | 26.5 MB unpacked embeddable 3.15.2 (measured) |
| Py (a2) CSnakes | none published ([Performance](https://tonybaloney.github.io/CSnakes/v1/advanced/performance/)) | numpy to Span; lists copied per element | uv or pip installers | none | none | as a1 | MIT | runtime 0.5 MB nupkg + Python (measured) |
| Py (a3) pythonnet | n/a: not AOT (Reflection.Emit) | views (v3) | pip | none | none | as a1 | MIT | 0.23 MB nupkg + Python (measured) |
| Py (b) worker process + pipe | pipe about 6.2 µs/msg (third party, [ipc-bench](https://github.com/goldsborough/ipc-bench)) plus serialisation | MessagePack or Arrow IPC columns | uv per env, lock files ([uv](https://docs.astral.sh/uv/guides/scripts/)) | OS only: AppContainer + Job ([MS](https://learn.microsoft.com/en-us/windows/win32/secauthz/appcontainer-isolation)) | yes, kill and restart | plain debugpy attach ([README](https://github.com/microsoft/debugpy)) | PSF + MIT/Apache | 26.5 MB Python + uv + packages |
| Py (c) IronPython 3 | n/a: not AOT ([#1896](https://github.com/IronLanguages/ironpython3/issues/1896)) | .NET objects | no C extensions | none | none | limited | Apache-2.0 | 6.8 MB nupkg (measured) |
| C# (a) Roslyn in AOT host | fails under AOT ([#73689](https://github.com/dotnet/roslyn/issues/73689)) | n/a | n/a | n/a | n/a | n/a | MIT | n/a |
| C# (b/c) JIT helper process | first compile "up to 4 seconds" ([CS-Script](https://www.cs-script.net/cs-script.core/help/html/bd7ee734-896b-4281-ce08-71d867253ae4.htm)) | serialised columns over pipe | `#r "nuget:"` | OS only | yes | VS / VS Code attach | MIT (Roslyn) | about 102.6 MB unpacked (measured) |
| C# (d) expression interpreter | interpreted, slower ([AOT doc](https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/)) | in-process | none | none | none | none | MIT | small |

## Conflicts and gaps found
- The CSnakes README gives two Python ranges, "3.9-3.13" and "3.8-3.13". A third-party table says CSnakes does not support AOT, which contradicts CSnakes' own AOT page ([README](https://github.com/tonybaloney/CSnakes), [COMPARISON.md](https://github.com/rkttu/dotnetpy/blob/main/docs/COMPARISON.md)).
- The Python.Included README says PSF licence, while the repo sidebar says MIT ([README](https://github.com/henon/Python.Included)).
- Several Rhino developer pages are now tagged "New in 9". Behaviour in Rhino 8 may differ ([Script Package References](https://developer.rhino3d.com/guides/scripting/advanced-packages/)).
- Not verified:
  - pyRevit Notion docs (would not render).
  - Per-call costs for pythonnet, CSnakes or gRPC from a primary source.
  - Hosting CoreCLR inside a Native AOT process.
  - DynamicExpresso under AOT.
