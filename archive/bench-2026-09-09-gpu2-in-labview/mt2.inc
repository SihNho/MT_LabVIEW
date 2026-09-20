// mt2.inc - GPU tracking interface v2 (2026-09-09, our design; see docs/gpu-backend.md "GPU interface v2").
//   ctx = mt2_open(cal_path, cross, flags, status, len)        calibration + windows to the GPU once, buffers allocated once
//   mt2_set_image(ctx, pixel_ptr, line_width, width, height)  IMAQ buffer pointer (no LabVIEW copy); pinned on first use
//   mt2_track(ctx, nb, xyz_in[3nb], good_in[nb], xyz_out[3nb], idx_out[nb], good_out[nb], status, len)   one launch per frame
//   mt2_close(ctx)
// Numerics: identical to GPUTracking_* (same Ctx, same fused kernel); x,y in are DBL and rounded half-to-even like the
// kernel VI's I32 coercion.  Status strings: "No_Errors t=.. u=.. k=.. e=.." or the error text (<= status_len - 1 bytes).
struct Mt2 {
    void* h;                       // Ctx*
    int cross, nb, S; double zstep;
    const unsigned char* pix; int line_width, width, height;
    unsigned char* stage; size_t stage_bytes;   // DLL-owned PINNED staging buffer (never pin LabVIEW's IMAQ buffer: IMAQ may free/re-allocate it
                                                // under the registration -> stale pages and per-frame register churn, seen 2026-09-09 13:2x)
    int keepalive;
};

static void mt2_status(char* status, int len, const char* text) { if (status && len > 0) { strncpy(status, text, len - 1); status[len - 1] = 0; } }

// Single-context policy (2026-09-09, user: the experiment VI is normally stopped with LabVIEW's Abort button, so mt2_close never
// runs and the next open would leak the previous GPU allocation).  mt2_open closes any context this DLL still holds before making
// a new one; the rig runs exactly one tracking loop, so nothing legitimate is ever closed by this.
static long long g_mt2_live = 0;
static long long g_mt2_ctx = 0; static char g_mt2_path[1024] = "";          // the one-node entry's cached context (mt2_track_simple)

API int mt2_close(long long ctx);

API long long mt2_open(const char* cal_path, int cross, int flags, char* status, int status_len) {
    if (!cal_path || cross <= 0 || cross > CROSS_MAX) { mt2_status(status, status_len, "mt2_open: bad arguments"); return 0; }
    if (g_mt2_live) { mt2_close(g_mt2_live); g_mt2_live = 0; }              // an aborted run's context, if any
    int n = 0, S = 0, L = 0;
    if (cal_file_header(cal_path, &n, &S, &L) != 0) { mt2_status(status, status_len, g_err); return 0; }
    if (L != 2 * (cross / 2) - 1) { snprintf(g_err, sizeof g_err, "mt2_open: cal profile length %d != 2*half-1 for cross %d", L, cross); mt2_status(status, status_len, g_err); return 0; }
    double wrs[CROSS_MAX], wh[CROSS_MAX]; make_win_rs(cross, wrs); make_win_h(cross, wh);
    void* h = nullptr;
    if (mt_gpu_init(cross, S, n, wrs, wh, &h) != 0) { mt2_status(status, status_len, g_err); return 0; }
    int nb_file = 0; double zs = 0;
    if (load_cal_file(h, cal_path, cross, &nb_file, &zs) != 0) { mt2_status(status, status_len, g_err); mt_gpu_free(h); return 0; }
    Mt2* m = (Mt2*)calloc(1, sizeof(Mt2)); m->h = h; m->cross = cross; m->nb = nb_file; m->S = S; m->zstep = zs; m->keepalive = flags & 1;
    if (m->keepalive) mt_gpu_keepalive(1);
    snprintf(g_err, sizeof g_err, "No_Errors beads=%d slices=%d zstep=%.4g", nb_file, S, zs); mt2_status(status, status_len, g_err);
    g_mt2_live = (long long)(intptr_t)m;
    return g_mt2_live;
}

API int mt2_set_image(long long ctx, unsigned long long pixel_ptr, int line_width, int width, int height) {
    Mt2* m = (Mt2*)(intptr_t)ctx; if (!m || !pixel_ptr || width <= 0 || height <= 0 || line_width < width) return -1;
    const unsigned char* p = (const unsigned char*)(uintptr_t)pixel_ptr;
    size_t need = (size_t)width * height;
    if (need != m->stage_bytes) {                                          // packed pinned staging buffer, (re)allocated on a size change only
        if (m->stage) cudaFreeHost(m->stage);
        m->stage = nullptr; m->stage_bytes = 0;
        if (cudaMallocHost((void**)&m->stage, need) != cudaSuccess) { cudaGetLastError(); m->stage = nullptr; } else m->stage_bytes = need;
    }
    m->pix = p; m->line_width = line_width; m->width = width; m->height = height; return 0;
}

API int mt2_track(long long ctx, int nb, const double* xyz_in, const unsigned char* good_in, double* xyz_out, int* idx_out, unsigned char* good_out,
                  char* status, int status_len) {
    Mt2* m = (Mt2*)(intptr_t)ctx;
    if (!m || !xyz_in || !xyz_out || !idx_out || !good_out) { mt2_status(status, status_len, "mt2_track: null argument"); return -10; }
    if (!m->pix) { mt2_status(status, status_len, "mt2_track: no image (call mt2_set_image)"); return -11; }
    if (nb != m->nb) { snprintf(g_err, sizeof g_err, "mt2_track: nb %d != calibration beads %d", nb, m->nb); mt2_status(status, status_len, g_err); return -12; }
    mt_gpu_keepalive_touch();                                              // the keep-alive thread parks itself if this stops arriving
    Ctx* c = (Ctx*)m->h; size_t bytes = (size_t)m->height * m->width;
    LARGE_INTEGER f0, t0, t1; QueryPerformanceFrequency(&f0); QueryPerformanceCounter(&t0);
    if (bytes != c->img_bytes) { if (c->d_img) cudaFree(c->d_img); if (cudaMalloc(&c->d_img, bytes) != cudaSuccess) { mt2_status(status, status_len, "cudaMalloc image"); return -13; } c->img_bytes = bytes; }
    // strided IMAQ rows -> packed PINNED staging buffer (host memcpy, ~0.1 ms) -> one DMA; falls back to a pageable 2-D copy
    LARGE_INTEGER tu0, tu1; QueryPerformanceCounter(&tu0);
    if (m->stage) {
        for (int r = 0; r < m->height; r++) memcpy(m->stage + (size_t)r * m->width, m->pix + (size_t)r * m->line_width, m->width);
        if (cudaMemcpy(c->d_img, m->stage, bytes, cudaMemcpyHostToDevice) != cudaSuccess) { mt2_status(status, status_len, "cudaMemcpy image"); return -14; }
    } else if (cudaMemcpy2D(c->d_img, m->width, m->pix, m->line_width, m->width, m->height, cudaMemcpyHostToDevice) != cudaSuccess) { mt2_status(status, status_len, "cudaMemcpy2D image"); return -14; }
    QueryPerformanceCounter(&tu1); g_t_up = 1e3 * (double)(tu1.QuadPart - tu0.QuadPart) / (double)f0.QuadPart;
    int* xi = (int*)malloc(nb * sizeof(int)); int* yi = (int*)malloc(nb * sizeof(int)); int* gi = (int*)malloc(nb * sizeof(int));
    double* xo = (double*)malloc(nb * sizeof(double)); double* yo = (double*)malloc(nb * sizeof(double)); double* zo = (double*)malloc(nb * sizeof(double)); int* go = (int*)malloc(nb * sizeof(int));
    for (int b = 0; b < nb; b++) { xi[b] = (int)rint(xyz_in[3 * b]); yi[b] = (int)rint(xyz_in[3 * b + 1]); gi[b] = good_in ? (good_in[b] ? 1 : 0) : 1; }
    int rc = mt_gpu_track_fused_dev(m->h, m->height, m->width, nb, xi, yi, gi, xo, yo, zo, idx_out, go);   // (H, W)   // image already on the device
    if (rc == 0) {
        for (int b = 0; b < nb; b++) { xyz_out[3 * b] = xo[b]; xyz_out[3 * b + 1] = yo[b]; xyz_out[3 * b + 2] = zo[b]; good_out[b] = (unsigned char)(go[b] ? 1 : 0); }
        QueryPerformanceCounter(&t1);
        snprintf(g_err, sizeof g_err, "No_Errors t=%.2f u=%.2f k=%.2f e=%.2f", 1e3 * (double)(t1.QuadPart - t0.QuadPart) / (double)f0.QuadPart, g_t_up, g_t_gpu, g_t_ev);
    }
    mt2_status(status, status_len, g_err);
    free(xi); free(yi); free(gi); free(xo); free(yo); free(zo); free(go);
    return rc;
}

API int mt2_close(long long ctx) {
    Mt2* m = (Mt2*)(intptr_t)ctx; if (!m) return -1;
    if (m->keepalive) mt_gpu_keepalive(0);
    if (m->stage) cudaFreeHost(m->stage);
    if (g_mt2_live == ctx) g_mt2_live = 0;
    if (g_mt2_ctx == ctx) { g_mt2_ctx = 0; g_mt2_path[0] = 0; }             // the one-node entry's cache points here too
    mt_gpu_free(m->h); free(m); return 0;
}

// One-node convenience entry for the LabVIEW subVI: the DLL opens and caches the context by calibration path, registers the
// IMAQ buffer, tracks.  Parameters are plain C types (the scripted CLFN is configured to exactly these):
//   const char* cal_path | uint64 pixel_ptr | int line_width_bytes | int width | int height | int nb |
//   const double* xyz_in[3nb] | const uint8* good_in[nb] | double* xyz_out[3nb] | int32* idx_out[nb] | uint8* good_out[nb] |
//   char* status (>= 64 bytes) | int status_len | int flags (bit0 keep-alive)    -> int rc (0 = ok)
API int mt2_track_simple(const char* cal_path, unsigned long long pixel_ptr, int line_width_bytes, int width, int height, int nb,
                         const double* xyz_in, const unsigned char* good_in, double* xyz_out, int* idx_out, unsigned char* good_out,
                         char* status, int status_len, int flags) {
    if (!cal_path) { mt2_status(status, status_len, "mt2_track_simple: no cal path"); return -1; }
    if (!g_mt2_ctx || strcmp(cal_path, g_mt2_path) != 0) {
        if (g_mt2_ctx) { mt2_close(g_mt2_ctx); g_mt2_ctx = 0; }
        g_mt2_ctx = mt2_open(cal_path, 120, flags, status, status_len);
        if (!g_mt2_ctx) return -2;
        strncpy(g_mt2_path, cal_path, 1023); g_mt2_path[1023] = 0;
    }
    if (mt2_set_image(g_mt2_ctx, pixel_ptr, line_width_bytes, width, height) != 0) { mt2_status(status, status_len, "mt2_track_simple: bad image args"); return -3; }
    return mt2_track(g_mt2_ctx, nb, xyz_in, good_in, xyz_out, idx_out, good_out, status, status_len);
}
