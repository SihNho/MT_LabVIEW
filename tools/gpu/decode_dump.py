"""decode_dump.py - print %TEMP%\\mt_track_dump.bin (written by dump.inc on the DLL's first LabVIEW call): every block as
tag, address, ok flag, and the bytes as int32 / float32 / uint64 views, so the real handle and cluster layout can be read off."""
import os, struct
import numpy as np
p = os.path.join(os.environ.get("TEMP", r"C:\Users\KimLab\AppData\Local\Temp"), "mt_track_dump.bin")
b = open(p, "rb").read(); magic, cross = struct.unpack("<ii", b[:8]); o = 8
print("magic", hex(magic), "cross", cross, "bytes", len(b))
while o + 32 <= len(b):
    tag = b[o:o + 16].rstrip(b"\0").decode("latin-1"); addr, ok, n = struct.unpack("<QII", b[o + 16:o + 32]); o += 32
    data = b[o:o + n]; o += n
    print(f"\n[{tag}] addr 0x{addr:016x} ok {ok} len {n}")
    if not n:
        continue
    i32 = np.frombuffer(data[:len(data) // 4 * 4], np.int32); f32 = np.frombuffer(data[:len(data) // 4 * 4], np.float32)
    u64 = np.frombuffer(data[:len(data) // 8 * 8], np.uint64); f64 = np.frombuffer(data[:len(data) // 8 * 8], np.float64)
    print("  i32:", i32[:16].tolist()); print("  f32:", [f"{v:.6g}" for v in f32[:16]]); print("  u64:", [f"0x{v:x}" for v in u64[:8]]); print("  f64:", [f"{v:.6g}" for v in f64[:8]])
    if tag == "text":
        print("  str:", data.split(b"\0")[0][:100])
