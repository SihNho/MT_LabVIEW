"""visa_aliases.py - what serial resources does NI-VISA actually see, and what are they ALIASED as?

WHY. The main VI's bytes contain four device-ish strings:

    'M-126.PD1, COM4 9600'   'M-126.PD1, COM5 115200'   'Rot, COM3 9600'   'Rot, COM2 115200'

I wrote those up as per-room configuration pairs. The user rejected that immediately and correctly - a device has
ONE port - and then said to cross-check against NI MAX:

    "필요하면 NI Max 들어가서도 확인해서 LabVIEW 상수하고 비교해보도록 하고"

This is that cross-check, done WITHOUT the NI MAX GUI, by calling NI-VISA's C API through ctypes - the same
technique that identified the camera as `cam1` after three attempts to drive LabVIEW's example VIs died behind
modal dialogs.

WHAT IT SETTLES. `viFindRsrc` lists the serial resources this machine really has; `viParseRsrcEx` returns each
one's **alias**, which is the user-assigned name NI MAX stores. If an alias literally reads `Rot, COM3 9600`,
then those strings are aliases and the VI is selecting among them - and only the ones that exist here are real.
Any string in the VI with no matching resource is a leftover from another machine or another room.

WHAT IT DOES NOT SETTLE: which alias the running code actually WIRES. That is a constant in the configuration
section and has to be read from the diagram. This narrows the candidates; it does not replace that read.

READ-ONLY: opens the VISA resource manager, enumerates, closes. No session is opened to any instrument, nothing
is written to any port, no device is touched.

  py tools/bench/visa_aliases.py
"""
import ctypes as C
import sys

VI_SUCCESS = 0
VI_ATTR_RSRC_NAME = 0xBFFF0002
VI_ATTR_INTF_INST_NAME = 0xBFFF00E9
VI_FIND_BUFLEN = 256


def main():
    for dll in ("visa64.dll", "visa32.dll", "nivisa64.dll"):
        try:
            lib = C.windll.LoadLibrary(dll)
            print(f"loaded {dll}", flush=True)
            break
        except OSError:
            continue
    else:
        print("NI-VISA DLL not found (tried visa64/visa32/nivisa64) - is NI-VISA installed?", flush=True)
        return 1

    rm = C.c_uint32()
    if lib.viOpenDefaultRM(C.byref(rm)) != VI_SUCCESS:
        print("viOpenDefaultRM failed", flush=True)
        return 2

    try:
        # --- every serial resource this machine has -------------------------------------------------
        find_list = C.c_uint32()
        count = C.c_uint32()
        desc = C.create_string_buffer(VI_FIND_BUFLEN)
        rc = lib.viFindRsrc(rm, b"ASRL?*INSTR", C.byref(find_list), C.byref(count), desc)
        if rc != VI_SUCCESS:
            print(f"viFindRsrc(ASRL?*INSTR) rc=0x{rc & 0xFFFFFFFF:08X} - no serial resources found", flush=True)
            names = []
        else:
            names = [desc.value.decode("mbcs")]
            for _ in range(count.value - 1):
                if lib.viFindNext(find_list, desc) != VI_SUCCESS:
                    break
                names.append(desc.value.decode("mbcs"))
            lib.viClose(find_list)

        print(f"\n## {len(names)} serial resource(s) present on this machine\n", flush=True)
        print(f"   {'resource':22} {'alias (NI MAX)':34} interface name", flush=True)
        print(f"   {'-' * 22} {'-' * 34} {'-' * 30}", flush=True)
        for n in names:
            intf_type = C.c_uint16()
            intf_num = C.c_uint16()
            rsrc_class = C.create_string_buffer(VI_FIND_BUFLEN)
            expanded = C.create_string_buffer(VI_FIND_BUFLEN)
            alias = C.create_string_buffer(VI_FIND_BUFLEN)
            rc = lib.viParseRsrcEx(rm, n.encode("mbcs"), C.byref(intf_type), C.byref(intf_num),
                                   rsrc_class, expanded, alias)
            a = alias.value.decode("mbcs") if rc == VI_SUCCESS else "<viParseRsrcEx failed>"

            # The NI-specific interface name usually reads like "COM3" or "ASRL3"; open briefly to read it.
            inst = ""
            sess = C.c_uint32()
            if lib.viOpen(rm, n.encode("mbcs"), 0, 0, C.byref(sess)) == VI_SUCCESS:
                buf = C.create_string_buffer(VI_FIND_BUFLEN)
                if lib.viGetAttribute(sess, VI_ATTR_INTF_INST_NAME, buf) == VI_SUCCESS:
                    inst = buf.value.decode("mbcs", "replace")
                lib.viClose(sess)
            print(f"   {n:22} {a:34} {inst}", flush=True)

        # --- compare with what the VI's bytes contain -------------------------------------------------
        from_vi = ["M-126.PD1, COM4 9600", "M-126.PD1, COM5 115200",
                   "Rot, COM3 9600", "Rot, COM2 115200"]
        aliases = set()
        for n in names:
            it, inum = C.c_uint16(), C.c_uint16()
            rc_, ex_, al_ = (C.create_string_buffer(VI_FIND_BUFLEN) for _ in range(3))
            if lib.viParseRsrcEx(rm, n.encode("mbcs"), C.byref(it), C.byref(inum), rc_, ex_, al_) == VI_SUCCESS:
                if al_.value:
                    aliases.add(al_.value.decode("mbcs"))

        print("\n## the four strings found in the main VI, against this machine\n", flush=True)
        for s in from_vi:
            mark = "PRESENT as an alias here" if s in aliases else "not an alias on this machine"
            print(f"   {s!r:28} -> {mark}", flush=True)
        print("\n   (An entry that is not an alias here is a leftover from another machine or room,", flush=True)
        print("    OR simply not an alias at all - e.g. a plain string constant the code compares.", flush=True)
        print("    Which one the running code WIRES is still a diagram read, not an inference.)", flush=True)
    finally:
        lib.viClose(rm)
    return 0


if __name__ == "__main__":
    sys.exit(main())
