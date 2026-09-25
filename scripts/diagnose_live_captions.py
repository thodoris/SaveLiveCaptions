"""
Dump the UI Automation tree of the Windows Live Captions window.

Use this when recording stops working after a Windows update: it shows
whether the "CaptionsScrollViewer" control the recorder reads from still
exists. Open Live Captions first, then run:

    .venv\Scripts\python.exe scripts\diagnose_live_captions.py
"""
import uiautomation as auto

auto.SetGlobalSearchTimeout(1.0)

print("=" * 70)
print("Live Captions UI Automation Diagnostic")
print("=" * 70)

desktop = auto.GetRootControl()

print("\nLooking for Live Captions window...")

window = desktop.Control(
    searchDepth=1,
    ClassName="LiveCaptionsDesktopWindow"
)

if not window.Exists(3):
    print("ERROR: Live Captions window was not found.")
    input("\nPress Enter to exit...")
    raise SystemExit(1)

print("\nFOUND LIVE CAPTIONS WINDOW")
print("-" * 70)
print("Name        :", window.Name)
print("ClassName   :", window.ClassName)
print("AutomationId:", window.AutomationId)

print("\n")
print("=" * 70)
print("DESCENDANT CONTROL TREE")
print("=" * 70)


def safe(control, attribute, default="<error>"):
    """Read a UIA property; the Live Captions tree can change while we walk it."""
    try:
        return getattr(control, attribute)
    except Exception:
        return default


def inspect_control(control, depth=0, max_depth=10):
    if depth > max_depth:
        return

    indent = "  " * depth

    try:
        name = safe(control, "Name", "")
        classname = safe(control, "ClassName", "")
        automation_id = safe(control, "AutomationId", "")
        control_type = safe(control, "ControlTypeName", "")
    except Exception:
        return

    # Print every control, but make potentially interesting controls obvious.
    interesting = (
        "caption" in str(name).lower()
        or "caption" in str(automation_id).lower()
        or "caption" in str(classname).lower()
        or "scroll" in str(name).lower()
        or "scroll" in str(automation_id).lower()
        or "scroll" in str(classname).lower()
        or "text" in str(control_type).lower()
    )

    marker = "  <<< INTERESTING" if interesting else ""

    print(
        f"{indent}[{control_type}] "
        f"Name={name!r} "
        f"ClassName={classname!r} "
        f"AutomationId={automation_id!r}"
        f"{marker}"
    )

    if depth == max_depth:
        return

    try:
        children = control.GetChildren()
    except Exception as e:
        print(f"{indent}  <children error: {e}>")
        return

    for child in children:
        inspect_control(child, depth + 1, max_depth)


inspect_control(window)

print("\n")
print("=" * 70)
print("TARGET SEARCHES")
print("=" * 70)

# Search for any ScrollViewer
print("\n1. Searching for ANY ScrollViewer...")

try:
    scroll = window.Control(
        searchDepth=15,
        ClassName="ScrollViewer"
    )

    if scroll.Exists(2):
        print("FOUND:")
        print("  Name        :", safe(scroll, "Name"))
        print("  ClassName   :", safe(scroll, "ClassName"))
        print("  AutomationId:", safe(scroll, "AutomationId"))
        print("  ControlType :", safe(scroll, "ControlTypeName"))
    else:
        print("NOT FOUND")
except Exception as e:
    print("ERROR:", repr(e))


# Search for the expected control
print("\n2. Searching for AutomationId=CaptionsScrollViewer...")

try:
    target = window.Control(
        searchDepth=15,
        AutomationId="CaptionsScrollViewer"
    )

    if target.Exists(2):
        print("FOUND:")
        print("  Name        :", safe(target, "Name"))
        print("  ClassName   :", safe(target, "ClassName"))
        print("  AutomationId:", safe(target, "AutomationId"))
        print("  ControlType :", safe(target, "ControlTypeName"))
    else:
        print("NOT FOUND")
except Exception as e:
    print("ERROR:", repr(e))


print("\n")
print("=" * 70)
print("Diagnostic complete")
print("=" * 70)

input("\nPress Enter to exit...")