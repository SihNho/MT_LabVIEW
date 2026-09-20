import win32com.client as win32
import sys

try:
    lv = win32.GetActiveObject("LabVIEW.Application")

    # Get all open VIs
    vois = lv.VIsInMemory
    bd_ref = None

    for voi in vois:
        if "GUIBENCH_v0.vi" in voi.Name and "Block Diagram" in voi.Name:
            bd_ref = voi
            break

    if not bd_ref:
        print("Could not find GUIBENCH_v0.vi Block Diagram")
        sys.exit(1)

    # Create Index Array node at (1100, 600)
    # Using New VI Object method
    node = bd_ref.NewVIObject(2, "Index Array", 1100, 600)

    if node:
        print("SUCCESS: Index Array node placed")
    else:
        print("FAILED: Could not create Index Array node")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
