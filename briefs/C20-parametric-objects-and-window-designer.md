# C20: parametric objects in the drawing, and a window designer for them

Research and design only. Write one report with pictures (mockups as HTML/SVG rendered to PNG). No Studio code is shared or wanted.

## Context

Urbanto Studio is a desktop CAD program for urban designers (Windows, C# .NET 10, Avalonia 12) with a node editor called Flow (like
Grasshopper or Geometry Nodes). A flow can already become a tool with exposed inputs (sliders, choices, tables, curves), presets, a form
with sections and show-when rules, a "Player" that runs a library flow from its form, and help text. The look is the modern C19 style
(calm slate surfaces, amber accent only for selection and the primary action, IBM Plex Sans, Tabler outline icons).

The owner's words on the feature (CAD-09, "flow-driven parametric object in the drawing"): "very important feature, needs to be polished
and look modern with customization; reorganize the UI parametric editor so the user can keep it useful and easy to use; he can add or remove
any parameter or controller. Grasshopper's one is so basic and bad, that's why no one uses it; here we need to make it perfect and polished:
a UI panel or pop-up window like Human UI, easy to make a custom window GUI with a window editor, drag and drop things, and so on. Do a
research first."

## What to do

1. Study how others do parametric objects and custom parameter UIs, from their own docs, videos and design write-ups, with links: Rhino
   Grasshopper (Human UI, Synapse, Remote Control panel, Grasshopper Player, Rhino.Compute / ShapeDiver configurators), Revit (families
   and type parameters, the Family Editor, Dynamo Player), Archicad (GDL objects and their parameter UI), Houdini (Digital Assets and the
   Type Properties parameter interface editor, Houdini Engine in other apps), Blender (Geometry Nodes modifier panel, node groups as
   assets), SketchUp Dynamic Components, Vectorworks Marionette, Fusion 360 parameters, Unreal (Details panel customization, Editor
   Utility Widgets), Figma (component properties and variants), and web configurators (ShapeDiver, Vizcom, Hypar).
2. Say what makes each good or bad to use, and why the Grasshopper approach is weak.
3. Propose the Studio design:
   - the parametric object itself: how it lives in the drawing (selection, grips or handles bound to inputs, re-run on edit, undo,
     copies sharing a definition or not, baking it to plain shapes, performance with hundreds of instances);
   - the parameter panel: where it shows (Properties, a pop-over, a floating window), groups, ordering, live preview, presets, reset;
   - the window designer: a drag-and-drop editor where the author builds a custom window for the object (controls palette: slider, number,
     choice, toggle, colour, table, curve, image, text, button, chart, tabs, sections; layout grid; bindings to flow inputs and outputs;
     conditional show/enable; themes from the app tokens), and how users then open that window;
   - how adding or removing parameters and controllers works for the author and for the user.
4. Mockups (HTML/SVG rendered to PNG): the parametric object selected in the drawing with its handles and panel; the window designer with
   a custom window being built; the finished custom window in use; dark and light.
5. A ranked build plan in steps of S/M/L, the first step useful on its own, and ten things not to copy.

Deliverable: branch `report/C20`, folder `reports/C20/` (report .md, mockups .html and .png, a sources list). Plain English, short
sentences, no em dashes.
