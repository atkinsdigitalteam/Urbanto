// C16 sample: exposing objects drawn on a custom WPF canvas to UI Automation (UIA).
// Compiled (not run) on Linux with the .NET 8 SDK and EnableWindowsTargeting=true;
// behaviour with Narrator/NVDA is NOT tested here (no Windows in the research machine).
//
// Pattern: the canvas is one FrameworkElement that draws everything itself (DrawingContext,
// SkiaSharp, Direct3D...). Its items are not UIElements, so each item gets a peer that derives
// directly from AutomationPeer (a UIA "fragment"), returned from the canvas peer's
// GetChildrenCore. Keyboard focus stays on the canvas element; the canvas tells UIA which
// item is focused by raising AutomationFocusChanged on that item's peer.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows;
using System.Windows.Automation;
using System.Windows.Automation.Peers;
using System.Windows.Automation.Provider;
using System.Windows.Input;
using System.Windows.Media;

namespace Studio.Accessibility.Sample
{
    /// <summary>A drawable object in model space (metres). Plain data, not a UIElement.</summary>
    public sealed class CanvasItem
    {
        public required string Id { get; init; }          // stable, culture-neutral -> AutomationId
        public required string Kind { get; init; }        // "building", "plot", "road" -> LocalizedControlType
        public required string Label { get; set; }        // "Block A"
        public required string Layer { get; set; }
        public Rect Bounds { get; set; }                  // model units (m)
        public double RotationDeg { get; set; }
        public bool Locked { get; set; }
        public bool IsSelected { get; set; }
        public double AreaM2 => Bounds.Width * Bounds.Height;
    }

    public class DrawingCanvas : FrameworkElement
    {
        public List<CanvasItem> Items { get; } = new();
        public CanvasItem? FocusedItem { get; private set; }
        public double Scale { get; set; } = 4.0;          // screen DIPs per metre
        public double GridStep { get; set; } = 1.0;       // nudge step in metres

        public DrawingCanvas() { Focusable = true; }

        protected override AutomationPeer OnCreateAutomationPeer() => new DrawingCanvasAutomationPeer(this);

        internal Rect ModelToElement(Rect r) => new(r.X * Scale, r.Y * Scale, r.Width * Scale, r.Height * Scale);

        protected override void OnRender(DrawingContext dc)
        {
            dc.DrawRectangle(Brushes.Transparent, null, new Rect(RenderSize));
            foreach (var it in Items)
            {
                var pen = new Pen(it == FocusedItem ? Brushes.DodgerBlue : Brushes.Gray, it.IsSelected ? 3 : 1);
                dc.DrawRectangle(null, pen, ModelToElement(it.Bounds));
            }
        }

        // ---- keyboard model (see report): Tab enters/leaves the canvas, arrows move between objects,
        //      Space selects (Ctrl+Space adds), Ctrl+arrows nudge by the grid step in metres
        protected override void OnKeyDown(KeyEventArgs e)
        {
            bool ctrl = (Keyboard.Modifiers & ModifierKeys.Control) != 0;
            switch (e.Key)
            {
                case Key.Right when !ctrl: MoveFocus(+1); e.Handled = true; break;   // a real canvas: nearest object in that direction
                case Key.Left when !ctrl: MoveFocus(-1); e.Handled = true; break;
                case Key.Space when FocusedItem != null:
                    SetSelected(FocusedItem, !FocusedItem.IsSelected, addToSelection: ctrl);
                    e.Handled = true; break;
                case Key.Right or Key.Left or Key.Up or Key.Down when ctrl && FocusedItem != null:   // AutoCAD-style nudge
                    var (dx, dy) = e.Key switch { Key.Right => (1, 0), Key.Left => (-1, 0), Key.Up => (0, -1), _ => (0, 1) };
                    Nudge(dx * GridStep, dy * GridStep); e.Handled = true; break;
            }
            base.OnKeyDown(e);
        }

        public void MoveFocus(int delta)
        {
            if (Items.Count == 0) return;
            int i = FocusedItem == null ? 0 : (Items.IndexOf(FocusedItem) + delta + Items.Count) % Items.Count;
            FocusItem(Items[i]);
        }

        public void FocusItem(CanvasItem item)
        {
            if (!Items.Contains(item)) return;
            if (!IsKeyboardFocused) Focus();
            FocusedItem = item;
            InvalidateVisual();
            if (UIElementAutomationPeer.FromElement(this) is DrawingCanvasAutomationPeer cp
                && AutomationPeer.ListenerExists(AutomationEvents.AutomationFocusChanged))
            {
                cp.PeerFor(FocusedItem).RaiseAutomationEvent(AutomationEvents.AutomationFocusChanged);
            }
        }

        public void SetSelected(CanvasItem item, bool selected, bool addToSelection)
        {
            if (selected && !addToSelection)
                foreach (var other in Items) other.IsSelected = false;
            item.IsSelected = selected;
            InvalidateVisual();
            if (UIElementAutomationPeer.FromElement(this) is not DrawingCanvasAutomationPeer cp) return;
            var peer = cp.PeerFor(item);
            var evt = !selected ? AutomationEvents.SelectionItemPatternOnElementRemovedFromSelection
                    : addToSelection ? AutomationEvents.SelectionItemPatternOnElementAddedToSelection
                    : AutomationEvents.SelectionItemPatternOnElementSelected;
            if (AutomationPeer.ListenerExists(evt)) peer.RaiseAutomationEvent(evt);
            if (AutomationPeer.ListenerExists(AutomationEvents.PropertyChanged))
                peer.RaisePropertyChangedEvent(SelectionItemPatternIdentifiers.IsSelectedProperty, !selected, selected);
        }

        public void Nudge(double dxM, double dyM)
        {
            var moved = Items.Where(i => i.IsSelected && !i.Locked).ToList();
            if (moved.Count == 0 && FocusedItem is { Locked: false } f) moved.Add(f);
            foreach (var it in moved) it.Bounds = Rect.Offset(it.Bounds, dxM, dyM);
            InvalidateVisual();
            if (UIElementAutomationPeer.FromElement(this) is not DrawingCanvasAutomationPeer cp) return;
            foreach (var it in moved) cp.PeerFor(it).InvalidatePeer();   // re-reads Name/BoundingRectangle
            // Tell the user what happened without moving focus (Windows 10 1709+, .NET 6+ WPF / .NET Framework 4.8.1).
            string dir = dxM > 0 ? "east" : dxM < 0 ? "west" : dyM > 0 ? "south" : "north";
            double dist = Math.Abs(dxM) + Math.Abs(dyM);
            cp.RaiseNotificationEvent(AutomationNotificationKind.ActionCompleted,
                                      AutomationNotificationProcessing.MostRecent,
                                      $"Moved {moved.Count} object{(moved.Count == 1 ? "" : "s")} {dist:0.##} m {dir}",
                                      "Studio.Canvas.Nudge");
        }

        public void AddItem(CanvasItem item)
        {
            Items.Add(item);
            InvalidateVisual();
            // Re-query GetChildrenCore so clients see the new child. Verify with Accessibility
            // Insights/AccEvent that a StructureChanged event reaches the client.
            (UIElementAutomationPeer.FromElement(this) as AutomationPeer)?.ResetChildrenCache();
        }
    }

    /// <summary>Peer for the canvas: a Pane that contains selectable items and supports multi-select.</summary>
    public sealed class DrawingCanvasAutomationPeer : FrameworkElementAutomationPeer, ISelectionProvider
    {
        private readonly Dictionary<string, CanvasItemAutomationPeer> _peers = new();
        public DrawingCanvasAutomationPeer(DrawingCanvas owner) : base(owner) { }
        private DrawingCanvas Canvas => (DrawingCanvas)Owner;

        internal CanvasItemAutomationPeer PeerFor(CanvasItem item)
        {
            // Reuse peers so a UIA client sees a stable element (RuntimeId) for the same object.
            if (!_peers.TryGetValue(item.Id, out var p)) _peers[item.Id] = p = new CanvasItemAutomationPeer(this, item);
            return p;
        }

        protected override AutomationControlType GetAutomationControlTypeCore() => AutomationControlType.Pane;
        protected override string GetLocalizedControlTypeCore() => "plan view";      // localise in Studio
        protected override string GetClassNameCore() => nameof(DrawingCanvas);
        protected override string GetNameCore() => $"Plan, {Canvas.Items.Count} objects";
        protected override List<AutomationPeer> GetChildrenCore() =>
            Canvas.Items.Select(i => (AutomationPeer)PeerFor(i)).ToList();

        public override object? GetPattern(PatternInterface patternInterface) =>
            patternInterface == PatternInterface.Selection ? this : base.GetPattern(patternInterface);

        // ISelectionProvider
        public bool CanSelectMultiple => true;
        public bool IsSelectionRequired => false;
        public IRawElementProviderSimple[] GetSelection() =>
            Canvas.Items.Where(i => i.IsSelected).Select(i => ProviderFromPeer(PeerFor(i))).ToArray();

        internal DrawingCanvas CanvasOwner => Canvas;
    }

    /// <summary>Peer for one drawn object: a UIA fragment with SelectionItem, Transform and Invoke.</summary>
    public sealed class CanvasItemAutomationPeer : AutomationPeer, ISelectionItemProvider, ITransformProvider, IInvokeProvider
    {
        private readonly DrawingCanvasAutomationPeer _parent;
        private readonly CanvasItem _item;
        public CanvasItemAutomationPeer(DrawingCanvasAutomationPeer parent, CanvasItem item) { _parent = parent; _item = item; }
        private DrawingCanvas Canvas => _parent.CanvasOwner;

        // ---- identity and description (what Narrator/NVDA speak on focus)
        protected override string GetNameCore() =>
            $"{_item.Label}, {_item.AreaM2:#,0} square metres";                      // no role word in Name
        protected override AutomationControlType GetAutomationControlTypeCore() => AutomationControlType.Custom;
        protected override string GetLocalizedControlTypeCore() => _item.Kind;         // required for Custom
        protected override string GetAutomationIdCore() => _item.Id;
        protected override string GetClassNameCore() => "CanvasItem";
        protected override string GetItemTypeCore() => _item.Layer;
        protected override string GetItemStatusCore() => _item.Locked ? "locked" : "";
        protected override string GetHelpTextCore() => "Space to select, Ctrl+arrow keys to nudge, Enter for properties";
        protected override int GetPositionInSetCore() => Canvas.Items.IndexOf(_item) + 1;   // "3 of 40"
        protected override int GetSizeOfSetCore() => Canvas.Items.Count;

        // ---- geometry: screen coordinates are required by UIA
        protected override Rect GetBoundingRectangleCore()
        {
            if (PresentationSource.FromVisual(Canvas) == null) return Rect.Empty;
            Rect r = Canvas.ModelToElement(_item.Bounds);
            Point a = Canvas.PointToScreen(r.TopLeft), b = Canvas.PointToScreen(r.BottomRight);
            return new Rect(a, b);
        }
        protected override bool IsOffscreenCore()
        {
            Rect r = Canvas.ModelToElement(_item.Bounds);
            return !r.IntersectsWith(new Rect(Canvas.RenderSize));
        }
        protected override Point GetClickablePointCore() { var r = GetBoundingRectangleCore(); return r.IsEmpty ? new Point(double.NaN, double.NaN) : new Point(r.X + r.Width / 2, r.Y + r.Height / 2); }

        // ---- focus: keyboard focus really sits on the canvas; report the logical focus here
        protected override bool HasKeyboardFocusCore() => Canvas.IsKeyboardFocused && Canvas.FocusedItem == _item;
        protected override bool IsKeyboardFocusableCore() => true;
        protected override void SetFocusCore() => Canvas.FocusItem(_item);
        protected override bool IsEnabledCore() => true;

        // ---- remaining abstract members
        protected override List<AutomationPeer>? GetChildrenCore() => null;
        protected override string GetAcceleratorKeyCore() => "";
        protected override string GetAccessKeyCore() => "";
        protected override AutomationPeer? GetLabeledByCore() => null;
        protected override AutomationOrientation GetOrientationCore() => AutomationOrientation.None;
        protected override bool IsContentElementCore() => true;
        protected override bool IsControlElementCore() => true;
        protected override bool IsPasswordCore() => false;
        protected override bool IsRequiredForFormCore() => false;

        public override object? GetPattern(PatternInterface p) => p switch
        {
            PatternInterface.SelectionItem or PatternInterface.Transform or PatternInterface.Invoke => this,
            _ => null,
        };

        // ISelectionItemProvider
        public bool IsSelected => _item.IsSelected;
        public IRawElementProviderSimple SelectionContainer => ProviderFromPeer(_parent);
        public void Select() => Canvas.SetSelected(_item, true, addToSelection: false);
        public void AddToSelection() => Canvas.SetSelected(_item, true, addToSelection: true);
        public void RemoveFromSelection() => Canvas.SetSelected(_item, false, addToSelection: true);

        // ITransformProvider: UIA passes screen pixels; convert to model units.
        public bool CanMove => !_item.Locked;
        public bool CanResize => !_item.Locked;
        public bool CanRotate => !_item.Locked;
        public void Move(double x, double y)
        {
            if (!CanMove) throw new InvalidOperationException("Object is locked");
            Point p = Canvas.PointFromScreen(new Point(x, y));
            _item.Bounds = new Rect(p.X / Canvas.Scale, p.Y / Canvas.Scale, _item.Bounds.Width, _item.Bounds.Height);
            Canvas.InvalidateVisual(); InvalidatePeer();
        }
        public void Resize(double width, double height)
        {
            if (!CanResize) throw new InvalidOperationException("Object is locked");
            _item.Bounds = new Rect(_item.Bounds.Location, new Size(width / Canvas.Scale, height / Canvas.Scale));
            Canvas.InvalidateVisual(); InvalidatePeer();
        }
        public void Rotate(double degrees)
        {
            if (!CanRotate) throw new InvalidOperationException("Object is locked");
            _item.RotationDeg = (_item.RotationDeg + degrees) % 360; Canvas.InvalidateVisual(); InvalidatePeer();
        }

        // IInvokeProvider: Enter / Narrator Caps Lock+Enter opens the properties panel for this object.
        public void Invoke()
        {
            Canvas.Dispatcher.BeginInvoke(() => { /* open properties panel, move focus to its first field */ });
            if (ListenerExists(AutomationEvents.InvokePatternOnInvoked)) RaiseAutomationEvent(AutomationEvents.InvokePatternOnInvoked);
        }
    }
}
