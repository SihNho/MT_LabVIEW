import sys
import re

def extract_ascii(data, min_len=4):
    pattern = re.compile(rb'[\x20-\x7e]{%d,}' % min_len)
    return [m.decode('ascii', errors='ignore') for m in pattern.findall(data)]

def extract_utf16(data, min_len=4):
    pattern = re.compile(rb'(?:[\x20-\x7e]\x00){%d,}' % min_len)
    out = []
    for m in pattern.finditer(data):
        try:
            out.append(m.group(0).decode('utf-16-le', errors='ignore'))
        except Exception:
            pass
    return out

def main():
    path = sys.argv[1]
    with open(path, 'rb') as f:
        data = f.read()

    print(f"File size: {len(data)} bytes\n")

    ascii_strings = extract_ascii(data, 5)
    print(f"Total ASCII strings (len>=5): {len(ascii_strings)}\n")

    # dump all to a file for grepping
    out_path = sys.argv[2] if len(sys.argv) > 2 else 'strings_out.txt'
    with open(out_path, 'w', encoding='utf-8') as f:
        for s in ascii_strings:
            f.write(s + '\n')
    print(f"Wrote strings to {out_path}")

if __name__ == '__main__':
    main()
