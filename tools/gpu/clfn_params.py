"""clfn_params.py - decode the LabVIEW type string of the import wizard's `Parameter Info` array (OpCLFNParams_v0 'type string')
and compose flattened Parameter Info data for our CLFN (mt2_track_simple).  Flattened data rules (NI 'Flattened Data'): big-endian,
strings/arrays prefixed by I32 sizes, booleans 1 byte, clusters = fields concatenated in order, enums = their integer width.
Enum widths / field order / ring item lists come from the type string (decoded here, printed by `py clfn_params.py --td <file>`);
the numeric codes of ring items = item order (verified against the CallLibrary.Prototype string after each set).
"""
import struct, sys, json

# ---- type-string decoder (LabVIEW 8.x 16-bit words, big-endian; 0x40 in the type code = 'has name' Pascal string appended) ----
TYPE_NAMES = {0x01: "I8", 0x02: "I16", 0x03: "I32", 0x04: "I64", 0x05: "U8", 0x06: "U16", 0x07: "U32", 0x08: "U64", 0x09: "SGL", 0x0A: "DBL",
              0x0B: "EXT", 0x15: "EnumU8", 0x16: "EnumU16", 0x17: "EnumU32", 0x21: "Bool", 0x30: "String", 0x32: "Path", 0x40: "Array",
              0x50: "Cluster", 0x53: "Variant", 0x70: "Refnum"}
ENUM_WIDTH = {0x15: 1, 0x16: 2, 0x17: 4}
SCALAR_FMT = {0x01: "b", 0x02: ">h", 0x03: ">i", 0x04: ">q", 0x05: "B", 0x06: ">H", 0x07: ">I", 0x08: ">Q", 0x09: ">f", 0x0A: ">d"}


def td_bytes(words):
    """I16 array (COM tuple) -> bytes, big-endian words"""
    return b"".join(struct.pack(">H", w & 0xFFFF) for w in words)


def pstr(b, o):
    n = b[o]; return b[o + 1:o + 1 + n].decode("latin-1"), o + 1 + n


def dump_td(b):
    """print every descriptor found in a flattened type string (heuristic walk: length-prefixed records)"""
    o = 0; recs = []
    while o + 4 <= len(b):
        ln, code = struct.unpack_from(">HH", b, o)
        if ln < 4 or o + ln > len(b):
            o += 2; continue
        body = b[o + 4:o + ln]; base = code & 0xFF; recs.append((o, ln, code, body))
        desc = TYPE_NAMES.get(base & 0x7F, hex(base)); extra = ""
        try:
            if (base & 0x7F) in ENUM_WIDTH:
                n = struct.unpack_from(">H", body, 0)[0]; items = []; p = 2
                for _ in range(n):
                    s, p = pstr(body, p); items.append(s)
                extra = f" items={items}"
                if code & 0x40 and p < len(body):
                    extra += f" name={pstr(body, p)[0]!r}"
            elif (base & 0x7F) == 0x50:
                n = struct.unpack_from(">H", body, 0)[0]; idx = struct.unpack_from(f">{n}H", body, 2); extra = f" fields(idx)={list(idx)}"
                p = 2 + 2 * n
                if code & 0x40 and p < len(body):
                    extra += f" name={pstr(body, p)[0]!r}"
            elif (base & 0x7F) == 0x40:
                nd = struct.unpack_from(">H", body, 0)[0]; dims = struct.unpack_from(f">{nd}I", body, 2); p = 2 + 4 * nd
                el = struct.unpack_from(">H", body, p)[0]; extra = f" ndims={nd} dims={list(dims)} elem(idx)={el}"
                p += 2
                if code & 0x40 and p < len(body):
                    extra += f" name={pstr(body, p)[0]!r}"
            else:
                if code & 0x40 and len(body) > 0:
                    # numeric/string/bool: body may start with type-specific words; name is the trailing Pascal string
                    for q in range(len(body)):
                        if body[q] == len(body) - q - 1:
                            extra = f" name={pstr(body, q)[0]!r}"; break
        except Exception as e:
            extra = f" (decode error {e})"
        print(f"@{o:04X} len={ln} code=0x{code:04X} {desc}{extra}")
        o += ln
    return recs


# ---- our parameter list for  int mt2_track_simple(...)  (return value first) ----
# ('name', kind, numeric, passing, dims)  kind: 'ret' 'num' 'arr' 'str'
PARAMS = [
    ("return value", "num", "I32", "value", 0),
    ("cal_path", "str", None, "cstr", 0),
    ("pixel_ptr", "num", "U64", "value", 0),
    ("line_width_bytes", "num", "I32", "value", 0),
    ("width", "num", "I32", "value", 0),
    ("height", "num", "I32", "value", 0),
    ("nb", "num", "I32", "value", 0),
    ("xyz_in", "arr", "DBL", "dataptr", 1),
    ("good_in", "arr", "U8", "dataptr", 1),
    ("xyz_out", "arr", "DBL", "dataptr", 1),
    ("idx_out", "arr", "I32", "dataptr", 1),
    ("good_out", "arr", "U8", "dataptr", 1),
    ("status", "str", None, "cstr", 0),
    ("status_len", "num", "I32", "value", 0),
    ("flags", "num", "I32", "value", 0),
]

if __name__ == "__main__":
    if "--td" in sys.argv:
        words = json.load(open(sys.argv[sys.argv.index("--td") + 1]))
        b = td_bytes(words); print("type string:", len(b), "bytes\n", b.hex()); dump_td(b)

# ---- layout decoded 2026-09-09 from the FGV's 7.x type string (tools/bench/paraminfo_td.json), cluster 'Parameter Info', 11 fields ----
# 1 Parameter Name (string)  2 Num Dimensions (I32)  3 Parameter Type (enum U16)  4 Numeric Type (enum U16)  5 Param Passing (U16)
# 6 Array Passing (U16)  7 String Passing (U16)  8 Adapt Format (U16)  9 ActiveX Types (U16)  10 Const (unused) (bool U8)  11 Minimum Size (STRING)
PARAM_TYPE = {"Numeric": 0, "Array": 1, "String": 2, "Waveform": 3, "Digital Waveform": 4, "Digital Table": 5, "ActiveX": 6, "Any": 7, "Instance Data Pointer": 8, "Void": 9}
NUM_TYPE = {"I8": 0, "I16": 1, "I32": 2, "I64": 3, "U8": 4, "U16": 5, "U32": 6, "U64": 7, "SGL": 8, "DBL": 9, "PTR INT": 10, "PTR UINT": 11}
PASSING = {"value": 0, "ptr": 1}
ARRAY_PASSING = {"dataptr": 0, "handle": 1, "handleptr": 2}
STRING_PASSING = {"cstr": 0, "pascal": 1, "handle": 2, "handleptr": 3}


def lvstr(s):
    b = s.encode("latin-1"); return struct.pack(">i", len(b)) + b


def record(name, kind, numeric, passing, dims, min_size=""):
    # kind "any" = the dialog's "Adapt to Type" (ring item 'Any'), Adapt Format 'By Value' = LabVIEW's "Handles by Value":
    # the DLL receives the ARRAY HANDLE.  Needed for the kernel's BOOLEAN array, which no explicit CLFN type can express
    # (the Numeric Type ring has no Boolean, and a Boolean-array wire into a U8-array parameter is a type mismatch).
    ptype = {"num": "Numeric", "arr": "Array", "str": "String", "void": "Void", "any": "Any"}[kind]
    ntype = NUM_TYPE[numeric] if numeric else 0
    return (lvstr(name) + struct.pack(">i", dims) + struct.pack(">H", PARAM_TYPE[ptype]) + struct.pack(">H", ntype)
            + struct.pack(">H", PASSING[passing] if kind == "num" else 0)
            + struct.pack(">H", ARRAY_PASSING[passing] if kind == "arr" else 0)
            + struct.pack(">H", STRING_PASSING[passing] if kind == "str" else 0)
            + struct.pack(">H", PASSING[passing] if kind == "any" else 0)   # Adapt Format: By Value = "Handles by Value"
            + struct.pack(">H", 0) + bytes([0]) + lvstr(min_size))


def compose(params=PARAMS):
    return struct.pack(">i", len(params)) + b"".join(record(*p) for p in params)


# The LabVIEW-facing variant: the two good-flag arrays are Adapt to Type so the kernel's BOOLEAN array control can be wired
# straight in (mt2_track_simple_b in mt2.inc reads them as LabVIEW array handles).
PARAMS_B = [(n, ("any" if n in ("good_in", "good_out") else k), (None if n in ("good_in", "good_out") else num),
             ("value" if n in ("good_in", "good_out") else p), d) for (n, k, num, p, d) in PARAMS]

if __name__ == "__main__" and "--compose" in sys.argv:
    out = sys.argv[sys.argv.index("--compose") + 1]; data = compose()
    open(out, "w").write(data.hex()); print(out, len(data), "bytes,", len(PARAMS), "records")
    if "--ret-only" in sys.argv:
        data = compose(PARAMS[:1]); open(out.replace(".hex", "_ret.hex"), "w").write(data.hex()); print("ret-only", len(data), "bytes")
    if "--bool" in sys.argv:
        data = compose(PARAMS_B); open(out.replace(".hex", "_b.hex"), "w").write(data.hex()); print("bool variant", len(data), "bytes")
