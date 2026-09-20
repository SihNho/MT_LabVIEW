import sys
import zlib
import re

def find_zlib_streams(data):
    starts = []
    for second in (0x01, 0x5e, 0x9c, 0xda):
        idx = 0
        while True:
            idx = data.find(bytes([0x78, second]), idx)
            if idx == -1:
                break
            starts.append(idx)
            idx += 1
    return sorted(set(starts))

def decompressed_text(path):
    with open(path, 'rb') as f:
        data = f.read()
    starts = find_zlib_streams(data)
    blobs = []
    for s in starts:
        d = zlib.decompressobj()
        try:
            out = d.decompress(data[s:s+2_000_000])
            if len(out) > 50:
                blobs.append(out)
        except Exception:
            continue
    pattern = re.compile(rb'[\x20-\x7e]{5,}')
    strs = set()
    for b in blobs:
        for m in pattern.findall(b):
            s = m.decode('ascii', errors='ignore')
            strs.add(s)
    # also raw file strings
    for m in pattern.findall(data):
        strs.add(m.decode('ascii', errors='ignore'))
    return strs

def looks_readable(s):
    if len(s) < 5:
        return False
    letters = sum(c.isalpha() for c in s)
    spaces = s.count(' ')
    if letters < 4:
        return False
    if letters / len(s) < 0.5:
        return False
    # must have at least one space or be a recognizable word-ish token
    return True

def main():
    path_old = sys.argv[1]
    path_new = sys.argv[2]
    out_path = sys.argv[3]

    old_strs = decompressed_text(path_old)
    new_strs = decompressed_text(path_new)

    only_new = sorted(s for s in (new_strs - old_strs) if looks_readable(s))
    only_old = sorted(s for s in (old_strs - new_strs) if looks_readable(s))

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"=== Strings only in NEW ({path_new}) — {len(only_new)} ===\n")
        for s in only_new:
            f.write(s + '\n')
        f.write(f"\n=== Strings only in OLD ({path_old}) — {len(only_old)} ===\n")
        for s in only_old:
            f.write(s + '\n')

    print(f"only_new: {len(only_new)}, only_old: {len(only_old)}")

if __name__ == '__main__':
    main()
