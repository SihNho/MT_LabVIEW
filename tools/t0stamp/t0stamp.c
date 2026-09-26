/* t0stamp.c v2 - per-site QueryPerformanceCounter completion stamps for LabVIEW CLFN nodes (card 93-2, PD200(c)(2)).
 * v1 (card 90-1) is kept as t0stamp_v1.c / t0stamp_v1.dll: it flushed every 1024th stamp to disk (WriteFile +
 * FlushFileBuffers) INSIDE stamp(), in the caller's thread (review archive/peer/2026-09-26-c93-h1-stamp-array-copy.md).
 *
 *   int32_t stamp(int32_t site, void *any)       cdecl, exported, unchanged signature
 *
 * `site` 0..63 selects a buffer; `any` is NEVER dereferenced.  v2: NO file I/O and no lock in stamp(): one QPC read,
 * one InterlockedIncrement, one store into a static preallocated per-site array of CAP stamps (pre-touched at attach,
 * so no page fault on the hot path).  A stamp beyond CAP is DROPPED and counted (overflow).  Files are written ONLY
 * at DLL_PROCESS_DETACH, in the same format as v1:
 *   <T0STAMP_DIR or <dll dir>\t0stamp_out>\t0_site<SS>_pid<PID>.bin  (int64 LE: [0] = QPC frequency, then counts
 *   in call order), plus t0_meta_pid<PID>.txt: one line per used site "site calls stored overflow".
 * Return 0 ok, 1 site out of range (nothing stored), 2 overflow (dropped, counted).
 */
#include <windows.h>
#include <stdint.h>
#include <stdio.h>

#define NSITES 64
#define CAP    65536             /* 64 x 65536 x 8 B = 32 MiB; a 120 s leg at 90 Hz x 8 beads ~ 86,400 on For sites */

typedef struct {
    volatile LONG idx;           /* total calls for this site (atomic); stored = min(idx, CAP) */
    LONGLONG      buf[CAP];
} site_t;

static site_t   g_site[NSITES];
static LONGLONG g_freq;
static char     g_dir[MAX_PATH];
static HMODULE  g_self;
static volatile LONG g_init;

static void ensure_dir(void)
{
    DWORD n = GetEnvironmentVariableA("T0STAMP_DIR", g_dir, MAX_PATH);
    if (n == 0 || n >= MAX_PATH) {
        char p[MAX_PATH]; char *s;
        GetModuleFileNameA(g_self, p, MAX_PATH);
        s = strrchr(p, '\\'); if (s) *s = 0;
        _snprintf(g_dir, MAX_PATH, "%s\\t0stamp_out", p);
    }
    CreateDirectoryA(g_dir, NULL);
}

__declspec(dllexport) int32_t __cdecl stamp(int32_t site, void *any)
{
    LARGE_INTEGER t; LONG i;
    (void)any;
    if (site < 0 || site >= NSITES || !g_init) return 1;
    QueryPerformanceCounter(&t);
    i = InterlockedIncrement(&g_site[site].idx) - 1;
    if (i >= CAP) return 2;                                /* dropped; idx - CAP = overflow count */
    g_site[site].buf[i] = t.QuadPart;
    return 0;
}

static void write_all(void)
{
    int k; char p[MAX_PATH]; DWORD w; HANDLE f, m; unsigned long pid = (unsigned long)GetCurrentProcessId();
    _snprintf(p, MAX_PATH, "%s\\t0_meta_pid%lu.txt", g_dir, pid);
    m = INVALID_HANDLE_VALUE;
    for (k = 0; k < NSITES; k++) {
        LONG n = g_site[k].idx, st = n < CAP ? n : CAP; char line[96]; int len;
        if (n <= 0) continue;
        if (m == INVALID_HANDLE_VALUE)
            m = CreateFileA(p, GENERIC_WRITE, FILE_SHARE_READ, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        len = _snprintf(line, sizeof line, "%d %ld %ld %ld\r\n", k, (long)n, (long)st, (long)(n - st));
        if (m != INVALID_HANDLE_VALUE && len > 0) WriteFile(m, line, (DWORD)len, &w, NULL);
        {
            char q[MAX_PATH];
            _snprintf(q, MAX_PATH, "%s\\t0_site%02d_pid%lu.bin", g_dir, k, pid);
            f = CreateFileA(q, GENERIC_WRITE, FILE_SHARE_READ, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
            if (f == INVALID_HANDLE_VALUE) continue;
            WriteFile(f, &g_freq, sizeof g_freq, &w, NULL);
            WriteFile(f, g_site[k].buf, (DWORD)(st * sizeof(LONGLONG)), &w, NULL);
            CloseHandle(f);
        }
    }
    if (m != INVALID_HANDLE_VALUE) CloseHandle(m);
}

BOOL WINAPI DllMain(HINSTANCE h, DWORD reason, LPVOID res)
{
    LARGE_INTEGER f; int k;
    (void)res;
    if (reason == DLL_PROCESS_ATTACH) {
        g_self = h; DisableThreadLibraryCalls(h);
        QueryPerformanceFrequency(&f); g_freq = f.QuadPart;
        for (k = 0; k < NSITES; k++) {                      /* pre-touch: commit every page now, not on the hot path */
            volatile char *b = (volatile char *)g_site[k].buf; size_t o;
            for (o = 0; o < sizeof g_site[k].buf; o += 4096) b[o] = 0;
            g_site[k].idx = 0;
        }
        ensure_dir(); g_init = 1;
    } else if (reason == DLL_PROCESS_DETACH) {
        g_init = 0; write_all();
    }
    return TRUE;
}
