# ucbench report v1 (card chat-B4) - facts only

Run tag `stub_v1`, par 4, total spend $0.00 (scorer cells $0.00). Arms: SH = claude-opus-5-5 high, SXH = xhigh, SMX = max (single sessions); UC = `--effort ultracode` (xhigh main loop + Workflow). Same prompt, tools and 60-min cap for every arm. usd / tokens are the cell's own result envelope (`total_cost_usd`, `modelUsage`). Sub-agents = distinct agent_id values in the cell's hook log (sub-agents that made at least one tool call).

Invalid attempts re-run from the start: 0 []
Records: 12, invalid after retries: 0

## L1 (key 9 items)

| arm | runs | recall blind (mean; r1 / r2) | recall mech | precision | false claims | claims | extra real | usd | min | sub-agents | Workflow calls | out tokens | in+cache tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SH | 1 | 0.111; 0.111 | 0.111 | 0.500 | 1 | 2 | 0 | 0 | 0.000 | 0 | 0 | 1 | 1 |
| SXH | 1 | 0.111; 0.111 | 0.111 | 0.500 | 1 | 2 | 0 | 0 | 0.000 | 0 | 0 | 1 | 1 |
| SMX | 1 | 0.111; 0.111 | 0.111 | 0.500 | 1 | 2 | 0 | 0 | 0.000 | 0 | 0 | 1 | 1 |
| UC | 1 | 0.111; 0.111 | 0.111 | 0.500 | 1 | 2 | 0 | 0 | 0.000 | 2 | 1 | 1 | 1 |

- UC minus SXH (orchestration effect, same main-loop effort): recall 0.000, precision 0.000, false claims 0, usd 0, minutes 0.000
- UC minus SMX (cost-matched alternative): recall 0.000, precision 0.000, false claims 0, usd 0, minutes 0.000
- key items found by UC runs only: 0 []
- key items found by single-session runs only (never by UC): 0 []
- key items found by no run: 8 ['K2', 'K3', 'K4', 'K5', 'K6', 'K7', 'K8', 'K9']

## L2 (key 23 items)

| arm | runs | recall blind (mean; r1 / r2) | recall mech | precision | false claims | claims | extra real | usd | min | sub-agents | Workflow calls | out tokens | in+cache tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SH | 1 | 0.043; 0.043 | 0.043 | 0.500 | 1 | 2 | 0 | 0 | 0.000 | 0 | 0 | 1 | 1 |
| SXH | 1 | 0.043; 0.043 | 0.043 | 0.500 | 1 | 2 | 0 | 0 | 0.000 | 0 | 0 | 1 | 1 |
| SMX | 1 | 0.043; 0.043 | 0.043 | 0.500 | 1 | 2 | 0 | 0 | 0.000 | 0 | 0 | 1 | 1 |
| UC | 1 | 0.043; 0.043 | 0.043 | 0.500 | 1 | 2 | 0 | 0 | 0.000 | 2 | 1 | 1 | 1 |

- UC minus SXH (orchestration effect, same main-loop effort): recall 0.000, precision 0.000, false claims 0, usd 0, minutes 0.000
- UC minus SMX (cost-matched alternative): recall 0.000, precision 0.000, false claims 0, usd 0, minutes 0.000
- key items found by UC runs only: 0 []
- key items found by single-session runs only (never by UC): 0 []
- key items found by no run: 22 ['K2', 'K3', 'K4', 'K5', 'K6', 'K7', 'K8', 'K9', 'K10', 'K11', 'K12', 'K13', 'K14', 'K15', 'K16', 'K17', 'K18', 'K19', 'K20', 'K21', 'K22', 'K23']

## L3 (key 110 items)

| arm | runs | recall blind (mean; r1 / r2) | recall mech | precision | false claims | claims | extra real | usd | min | sub-agents | Workflow calls | out tokens | in+cache tokens | count acc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SH | 1 | 0.009; 0.009 | 0.009 | 0.500 | 1 | 2 | 0 | 0 | 0.000 | 0 | 0 | 1 | 1 | 0.000 |
| SXH | 1 | 0.009; 0.009 | 0.009 | 0.500 | 1 | 2 | 0 | 0 | 0.000 | 0 | 0 | 1 | 1 | 0.000 |
| SMX | 1 | 0.009; 0.009 | 0.009 | 0.500 | 1 | 2 | 0 | 0 | 0.000 | 0 | 0 | 1 | 1 | 0.000 |
| UC | 1 | 0.009; 0.009 | 0.009 | 0.500 | 1 | 2 | 0 | 0 | 0.000 | 2 | 1 | 1 | 1 | 0.000 |

- UC minus SXH (orchestration effect, same main-loop effort): recall 0.000, precision 0.000, false claims 0, usd 0, minutes 0.000
- UC minus SMX (cost-matched alternative): recall 0.000, precision 0.000, false claims 0, usd 0, minutes 0.000
- key items found by UC runs only: 0 []
- key items found by single-session runs only (never by UC): 0 []
- key items found by no run: 109 ['K2', 'K3', 'K4', 'K5', 'K6', 'K7', 'K8', 'K9', 'K10', 'K11', 'K12', 'K13', 'K14', 'K15', 'K16', 'K17', 'K18', 'K19', 'K20', 'K21', 'K22', 'K23', 'K24', 'K25', 'K26', 'K27', 'K28', 'K29', 'K30', 'K31', 'K32', 'K33', 'K34', 'K35', 'K36', 'K37', 'K38', 'K39', 'K40', 'K41', 'K42', 'K43', 'K44', 'K45', 'K46', 'K47', 'K48', 'K49', 'K50', 'K51', 'K52', 'K53', 'K54', 'K55', 'K56', 'K57', 'K58', 'K59', 'K60', 'K61', 'K62', 'K63', 'K64', 'K65', 'K66', 'K67', 'K68', 'K69', 'K70', 'K71', 'K72', 'K73', 'K74', 'K75', 'K76', 'K77', 'K78', 'K79', 'K80', 'K81', 'K82', 'K83', 'K84', 'K85', 'K86', 'K87', 'K88', 'K89', 'K90', 'K91', 'K92', 'K93', 'K94', 'K95', 'K96', 'K97', 'K98', 'K99', 'K100', 'K101', 'K102', 'K103', 'K104', 'K105', 'K106', 'K107', 'K108', 'K109', 'K110']

