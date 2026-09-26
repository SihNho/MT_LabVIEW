/* bench.c - card 93-2 (2): per-call cost of stamp() measured IN C (no ctypes), one thread, like one LabVIEW loop.
 *   bench.exe <dll> <iters> <out.bin>
 * Calls stamp(site, &buf) for sites 0,2,3,4,6,8 in that order, <iters> rounds; each call is bracketed by QPC reads.
 * out.bin (int64 LE): [0] freq, [1] ncalls, then per call: before-tick, after-tick (so python checks call order).
 * Also calls site 64 and -1 once each and prints their return codes.  DLL unloaded (FreeLibrary) before exit.
 */
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
typedef int32_t (__cdecl *stamp_t)(int32_t, void *);
static const int SITES[6] = {0, 2, 3, 4, 6, 8};

int main(int argc, char **argv)
{
    HMODULE h; stamp_t fn; long long it, n, k = 0; LARGE_INTEGER f, a, b; long long *rec; FILE *o; int j, r64, rm1;
    static unsigned short img[1024 * 1280];
    if (argc < 4) { fprintf(stderr, "usage\n"); return 2; }
    it = atoll(argv[2]); n = it * 6;
    rec = (long long *)malloc((size_t)(2 * n + 2) * sizeof(long long)); if (!rec) return 3;
    for (k = 0; k < 2 * n + 2; k++) rec[k] = 0;                  /* touch before timing */
    h = LoadLibraryA(argv[1]); if (!h) { fprintf(stderr, "load %lu\n", GetLastError()); return 4; }
    fn = (stamp_t)GetProcAddress(h, "stamp"); if (!fn) return 5;
    QueryPerformanceFrequency(&f); rec[0] = f.QuadPart; rec[1] = n; k = 2;
    for (long long i = 0; i < it; i++)
        for (j = 0; j < 6; j++) {
            QueryPerformanceCounter(&a); fn(SITES[j], img); QueryPerformanceCounter(&b);
            rec[k++] = a.QuadPart; rec[k++] = b.QuadPart;
        }
    r64 = fn(64, img); rm1 = fn(-1, img);
    FreeLibrary(h);
    o = fopen(argv[3], "wb"); if (!o) return 6;
    fwrite(rec, sizeof(long long), (size_t)(2 * n + 2), o); fclose(o);
    printf("BENCH n=%lld r64=%d rm1=%d\n", n, r64, rm1);
    return 0;
}
