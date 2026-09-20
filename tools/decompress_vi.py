import sys
import zlib
import re

def find_zlib_streams(data):
    # common zlib header bytes: 0x78 followed by 0x01, 0x9C, 0xDA, 0x5E
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

def try_decompress_all(data):
    results = []
    starts = find_zlib_streams(data)
    print(f"Found {len(starts)} candidate zlib headers")
    for s in starts:
        d = zlib.decompressobj()
        try:
            out = d.decompress(data[s:s+2_000_000])
            if len(out) > 50:
                results.append((s, out))
        except Exception:
            continue
    return results

def extract_ascii(data, min_len=5):
    pattern = re.compile(rb'[\x20-\x7e]{%d,}' % min_len)
    return [m.decode('ascii', errors='ignore') for m in pattern.findall(data)]

def main():
    path = sys.argv[1]
    out_path = sys.argv[2]
    with open(path, 'rb') as f:
        data = f.read()

    results = try_decompress_all(data)
    print(f"Successfully decompressed {len(results)} streams")

    with open(out_path, 'w', encoding='utf-8') as f:
        for s, out in results:
            f.write(f"\n===== STREAM AT OFFSET {s}, decompressed size {len(out)} =====\n")
            strs = extract_ascii(out, 4)
            for st in strs:
                f.write(st + '\n')

if __name__ == '__main__':
    main()
