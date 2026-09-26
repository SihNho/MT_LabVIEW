/* t0stamp.c - per-site QueryPerformanceCounter completion stamps for LabVIEW CLFN nodes (card 90-1, PD196(d)).
 *
 *   int32_t stamp(int32_t site, void *any)       cdecl, exported
 *
 * `site` 0..63 selects a buffer; `any` is NEVER dereferenced (Adapt-to-Type wire branch - it only sequences the call
 * after the wire's producer).  Each call appends one raw QPC count to the site's ring; every 1024th stamp the buffer is
 * flushed to  <T0STAMP_DIR or <dll dir>\t0stamp_out>\t0_site<SS>_pid<PID>.bin  (little-endian int64; first record of
 * the file = QueryPerformanceFrequency, then counts in call order); all sites are flushed at DLL_PROCESS_DETACH.
 * Return 0 ok, 1 site out of range (nothing written).
 *
 * Thread safety: the hot path is one InterlockedIncrement on the site's index + one store into a preallocated static
 * array (no allocation); the flush holds a per-site CRITICAL_SECTION only.  A stamp that lands in the CHUNK being
 * flushed waits on that lock (rare: once per 1024 calls), so no stamp is lost or reordered within a site.
 */
#include <windows.h>
#include <stdint.h>
#include <stdio.h>

#define NSITES 64
#define CHUNK  1024
#define NCHUNK 2                 /* double buffer: stamps go on while the other chunk is written */

typedef struct {
    LONG            idx;         /* total stamps issued for this site (atomic) */
    LONG            written;     /* chunks flushed so far */
    LONGLONG        buf[NCHUNK][CHUNK];
    CRITICAL_SECTION lock;
    HANDLE          file;        /* INVALID_HANDLE_VALUE until the first flush */
} site_t;

static site_t   g_site[NSITES];
static LONGLONG g_freq;
static char     g_dir[MAX_PATH];
static HMODULE  g_self;
static int      g_init;

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

/* write [lo, hi) of the site's total-index space, i.e. the chunk c = lo / CHUNK.  Caller holds the lock. */
static void flush_range(int site, LONG lo, LONG hi)
{
    site_t *s = &g_site[site]; DWORD w;
    if (hi <= lo) return;
    if (s->file == INVALID_HANDLE_VALUE) {
        char p[MAX_PATH];
        _snprintf(p, MAX_PATH, "%s\\t0_site%02d_pid%lu.bin", g_dir, site, (unsigned long)GetCurrentProcessId());
        s->file = CreateFileA(p, GENERIC_WRITE, FILE_SHARE_READ, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        if (s->file == INVALID_HANDLE_VALUE) return;
        WriteFile(s->file, &g_freq, sizeof g_freq, &w, NULL);
    }
    WriteFile(s->file, &s->buf[(lo / CHUNK) % NCHUNK][lo % CHUNK], (DWORD)((hi - lo) * sizeof(LONGLONG)), &w, NULL);
    FlushFileBuffers(s->file);
}

__declspec(dllexport) int32_t __cdecl stamp(int32_t site, void *any)
{
    LARGE_INTEGER t; LONG i; site_t *s;
    (void)any;
    if (site < 0 || site >= NSITES || !g_init) return 1;
    s = &g_site[site];
    QueryPerformanceCounter(&t);
    i = InterlockedIncrement(&s->idx) - 1;                 /* my slot in total-index space */
    s->buf[(i / CHUNK) % NCHUNK][i % CHUNK] = t.QuadPart;
    if ((i % CHUNK) == CHUNK - 1) {                        /* I closed a chunk: flush it */
        EnterCriticalSection(&s->lock);
        flush_range(site, i - (CHUNK - 1), i + 1);
        s->written++;
        LeaveCriticalSection(&s->lock);
    }
    return 0;
}

static void flush_all(void)
{
    int k;
    for (k = 0; k < NSITES; k++) {
        site_t *s = &g_site[k]; LONG n, done;
        EnterCriticalSection(&s->lock);
        n = s->idx; done = s->written * CHUNK;
        if (n > done) flush_range(k, done, n);            /* the partial tail chunk */
        if (s->file != INVALID_HANDLE_VALUE) { CloseHandle(s->file); s->file = INVALID_HANDLE_VALUE; }
        LeaveCriticalSection(&s->lock);
    }
}

BOOL WINAPI DllMain(HINSTANCE h, DWORD reason, LPVOID res)
{
    int k; LARGE_INTEGER f;
    (void)res;
    if (reason == DLL_PROCESS_ATTACH) {
        g_self = h; DisableThreadLibraryCalls(h);
        QueryPerformanceFrequency(&f); g_freq = f.QuadPart;
        for (k = 0; k < NSITES; k++) { InitializeCriticalSection(&g_site[k].lock); g_site[k].file = INVALID_HANDLE_VALUE; }
        ensure_dir(); g_init = 1;
    } else if (reason == DLL_PROCESS_DETACH) {
        g_init = 0; flush_all();
        for (k = 0; k < NSITES; k++) DeleteCriticalSection(&g_site[k].lock);
    }
    return TRUE;
}
