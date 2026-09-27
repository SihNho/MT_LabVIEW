# Card 111-1 - Error List of D1_l2_b1_20260927_193100.vi (md5 b705728ab0714dc8179fc955283800f9), full read

Source read: `errorlist_D1_l2_b1_20260927_193100_c111.json` (+ `_raw`), window N 99, items 99, all gates True. Log `tools/bench/diag_c111_b1_errorlist.log`.

## Owners (read from a byte-identical scratch of the saved file)

- #11261 chain [['Diagram', 23166], ['WhileLoop', 10170]]; #8323 row [(23166, 'Diagram', 25618)], its owner chain [['WhileLoop', 10170]]; loop 1.5 = 23032; loop map {637: '1.1', 10170: '1.2', 23041: '1.7', 23032: '1.5'}
- wire 25618 ends: [(11261, 'BuildArray', 'appended array', True), (23166, 'Diagram', 'Force (pN) vs Extension (nm) ', False)]
- #11261 terminals: [('appended array', True, 25618), ('array', False, 0), ('element', False, 0)]

## Items that can be on #11261 / wire 25618 (text; double-click capture)

- item 0: Build Array 'Build Array': Contains unwired or bad terminal -> G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop\tools\bench\errorlist_shots\bd_203721_after0.png
- item 2: Build Array'Build Arrav': Contains unwired orbad terminal -> G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop\tools\bench\errorlist_shots\bd_203742_after2.png
- item 3: Build Array 'Build Array': Contains unwired or bad terminal -> G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop\tools\bench\errorlist_shots\bd_203751_after3.png
- item 4: Build Array 'Build Array': Contains unwired or bad terminal -> G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop\tools\bench\errorlist_shots\bd_203800_after4.png
- item 6: You have connected two terminals of different types. -> G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop\tools\bench\errorlist_shots\bd_203823_after6.png
- item 23: You have connected two terminals of different types. -> G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop\tools\bench\errorlist_shots\bd_204137_after23.png
- item 24: You have connected two terminals of different types. -> G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop\tools\bench\errorlist_shots\bd_204148_after24.png
- item 46: You have connected two terminals of different types. -> G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop\tools\bench\errorlist_shots\bd_204605_after46.png
- item 9: You have connected two arrays of different dimensions. -> G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop\tools\bench\errorlist_shots\bd_203859_after9.png
- item 28: You have connected two arrays of different dimensions. -> G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop\tools\bench\errorlist_shots\bd_204235_after28.png

## Attribution (count level; rule: L2-A3 class count first, then plan_l2b1 open rows by node kind / terminal name / B1-new RBW wire ends on an open-row node or a uid cited in its `why`; everything else UNATTRIBUTED)

| class | n | L2-A3 | open-row | UNATTRIBUTED | rule / rows |
|---|---|---|---|---|---|
| buildarr | 4 | 1 | 3 | 0 | open-row nodes of that kind (2626 counted in L2-A3); class IN L2-A3 expected: #8566 ['8566:element']; #11261 ['11261:array', '11261:element']; #29973 ['29973:element'] |
| split1darr | 1 | 0 | 1 | 0 | open-row nodes of that kind (2626 counted in L2-A3); class NOT in L2-A3 expected: #27716 ['27716:index'] |
| bundle | 1 | 0 | 1 | 0 | open-row nodes of that kind (2626 counted in L2-A3); class NOT in L2-A3 expected: #11608 ['11261:element(cited #11608)'] |
| indexarr | 1 | 0 | 0 | 1 | open-row nodes of that kind (2626 counted in L2-A3); class NOT in L2-A3 expected:  |
| replacearr | 2 | 0 | 2 | 0 | open-row nodes of that kind (2626 counted in L2-A3); class NOT in L2-A3 expected: #8634 ['8634:array', '8634:index (col)']; #29625 ['29625:array', '29625:index (col)'] |
| imagein | 1 | 1 | 0 | 0 | open rows whose terminal name is in the item text; class IN L2-A3 expected:  |
| unwiredselector | 1 | 0 | 0 | 1 | ; class NOT in L2-A3 expected:  |
| sr_unwired_inside | 2 | 0 | 0 | 2 | B1-new sink-RSR RBW ends (2 new, 0 with an open-row end, 0 of them already credited to another class; pool shared by ['sr_unwired_inside', 'sr_type_undefined']); class NOT in L2-A3 expected:  |
| sr_type_undefined | 2 | 0 | 0 | 2 | B1-new sink-RSR RBW ends (2 new, 0 with an open-row end, 0 of them already credited to another class; pool shared by ['sr_unwired_inside', 'sr_type_undefined']); class NOT in L2-A3 expected:  |
| tunnel_to_input | 15 | 2 | 13 | 0 | B1-new sink-only RBW ends (19 new, 17 with an open-row end, 0 of them already credited to another class; pool shared by ['no_source', 'tunnel_to_input']); class IN L2-A3 expected: 3148 ['5696:Correction Factor', '5696:x,y,z array']; 3210 ['5696:Correction Factor', '5696:x,y,z array']; 3413 ['5696:z indices of all exp(cited #3176)', '6085:Correction Factor']; 3513 ['5696:z index of first ref(cited #2992)', '6085:Correction Factor']; 6145 ['5696:Correction Factor(cited #6132)', '6085:Correction Factor']; 6176 ['5696:Correction Factor', '5696:Correction Factor(cited #6132)']; 9076 ['8634:array', '8634:array(cited #9087)']; 9993 ['8566:element', '8566:element(cited #10004)']; 10166 ['8634:array', '8634:index (col)']; 28365 ['28083:Mag pos when touched to glass', '28083:Mag pos when touched to glass(cited #28370)']; 28684 ['28083:Mag pos when touched to glass', '28083:Magnet position']; 29766 ['29625:array', '29625:index (col)']; 29853 ['29625:array', '29625:array(cited #29911)'] |
| undirected_tunnel | 11 | 0 | 4 | 7 | B1-new sink-LoopTunnel RBW ends (11 new, 11 with an open-row end, 7 of them already credited to another class; pool shared by ['undirected_tunnel']); class NOT in L2-A3 expected: (30636, 30135) ['29973:element']; (30885, 30896) ['30306:left rank', '30306:left rank(cited #30896)']; (31064, 31051) ['27716:index', '27716:index(cited #31051)']; (31128, 31137) ['29009:left rank', '29009:left rank(cited #31137)'] |
| different_types | 4 | 0 | 4 | 0 | B1-new src+sink RBW ends (6 new, 5 with an open-row end, 0 of them already credited to another class; pool shared by ['different_types', 'different_dims']); class NOT in L2-A3 expected: 10043 ['8566:element', '8634:array']; 15847 ['29009:left rank', '29009:right rank']; 20097 ['30306:left rank', '30306:right rank']; 25618 ['11261:array', '11261:element'] |
| different_dims | 2 | 0 | 1 | 1 | B1-new src+sink RBW ends (6 new, 5 with an open-row end, 4 of them already credited to another class; pool shared by ['different_types', 'different_dims']); class NOT in L2-A3 expected: 30241 ['29625:array', '29625:index (col)'] |
| no_source | 9 | 3 | 0 | 6 | B1-new sink-only RBW ends (19 new, 17 with an open-row end, 17 of them already credited to another class; pool shared by ['no_source', 'tunnel_to_input']); class IN L2-A3 expected:  |
| unconnected | 20 | 9 | 0 | 11 | B1-new termless RBW ends (11 new, 0 with an open-row end, 0 of them already credited to another class; pool shared by ['unconnected']); class IN L2-A3 expected:  |
| loose_ends | 23 | 13 | 4 | 6 | B1-new source-only RBW ends (9 new, 4 with an open-row end, 0 of them already credited to another class; pool shared by ['loose_ends']); class IN L2-A3 expected: 4878 ['2626:element(cited #4580)']; 10187 ['8634:index (col)(cited #10068)']; 12256 ['11261:element(cited #11608)']; 29787 ['29625:index (col)(cited #29240)', '29973:element(cited #29240)'] |

**Totals:** items 99 = L2-A3 29 + open-row 33 + UNATTRIBUTED 37 (count-capped). If any count of a class already in the L2-A3 expected file counts as licensed, UNATTRIBUTED = 14.

Not credited because the wire was already credited to another class (one wire, one credit; review `archive/peer/2026-09-27-c111a-selfcheck.md` §1): [('undirected_tunnel', 9076), ('undirected_tunnel', 9993), ('undirected_tunnel', 10166), ('undirected_tunnel', 28365), ('undirected_tunnel', 28684), ('undirected_tunnel', 29766), ('undirected_tunnel', 29853), ('different_dims', 10043), ('different_dims', 15847), ('no_source', 3148), ('no_source', 3210), ('no_source', 3413), ('no_source', 3513), ('no_source', 6145), ('no_source', 6176)]. `unconnected` wires have no ends, so they can never match an open row; the attribution matches COUNTS, not item identities (no uid per item).
