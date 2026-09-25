# c89-profiler-fact2

- **agent:** claude
- **role:** fact
- **model:** fable (effort low; peer.ps1 default for role fact)
- **kind:** fact
- **cost:** $2.2050  in 290 / out 11985 / cache-create 42692 / cache-read 444314  (222s, 49 turn(s))
- **date:** 2026-09-26 01:58:42
- **outcome:** ANSWERED (223s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

API-fact question (LabVIEW 2026 / 2020+, Windows). Answer with URLs for every claim; say "not found" where nothing exists.

1. The VI property "Allow debugging" (VI Properties » Execution). Which VI Server property reads it (public class VI, property name and, if published anywhere, its numeric/hex property ID as used by scripting/private-property catalogs such as the LabVIEW Wiki "VI Server class hierarchy" or the LabVIEW scripting property-ID lists)? Can it be read through the LabVIEW ActiveX Automation server (VirtualInstrument object) — list the VirtualInstrument properties/methods NI documents (ExecState, FPState, GetControlValue, ...) and state whether any exposes execution settings such as debugging, reentrancy or priority.
2. Offline: in the .vi file's RSRC container, the `LVSR` block holds VI-settings flags. According to pylabview (mefistotelis/pylabview, LVblock.py / the wiki "Blocks" page) which flag bit(s) encode "debugging allowed / not debuggable" (e.g. VI_FLAGS or VI_FLAGS2 names, bit positions, whether set=disabled), and at what byte offset within LVSR do the flags sit for LabVIEW 2020+ files? Quote the enum names exactly.
3. LabVIEW.ini tokens related to the profiler or to debugging (e.g. tokens documented on the LabVIEW Wiki "LabVIEW configuration file" / "INI tokens" pages). List any that start/auto-save profiling; say "none found" otherwise.
Return a compact fact list, each with its URL.


## Answer

**1. VI Server property for "Allow debugging"**

- Property: VI class, long name `Execution:Allow Debugging`, short name `Exec.AllowDebug`, Boolean, Read/Write, remote access yes, not settable while running, Run-Time Engine: read only. Public (not scripting/private). Property ID listed as **206** in the LabVIEW Wiki VI class table (the table's "Property ID" column; hex-style IDs). https://labviewwiki.org/wiki/VI_class/Execution.Allow_Debugging_property and https://labviewwiki.org/wiki/VI_class
- NI reference page for the same property (content not fetchable through my tool, only navigation returned): https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/vi/allowdebugging.html
- ActiveX: yes. The VirtualInstrument object (obtained via Application.GetVIReference) has a documented `AllowDebugging` property, Boolean, read/write, `object.AllowDebugging`. Writing it recompiles the VI; TRUE generates extra breakpoint/single-step code. https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/activex/vi/allowdebugging.html
- NI's ActiveX VI property list (VI Properties (ActiveX)) also documents other execution settings: `IsReentrant`, `ReentrancyType`, `ExecPriority`, `PreferredExecSystem`, `ExecInlining`, `ExecIsInlineable`, `SuspendOnCall`, `ExecState`, `EditMode`, `IsProbe`, plus `FPState`, `FPBehavior`, `FPWinBounds`, `CodeSize`, `DataSize`, `BDSize`, `FPSize`, `Name`, `Path`, `Description`, `VIType`, `Callers`, `Library`, `OwningApp`, `IsCloneVI`, `CloneName`, `RunOnOpen`, `ShowFPOnCall`, `ShowFPOnLoad`, `CloseFPAfterCall`, `LogAtFinish`, `LogFilePath`, `HistoryText`, `RevisionNumber`, printing/help/toolbar/history properties. https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/activex/vi-p.html
- ActiveX VI methods documented: `Abort`, `Call`, `Call2`, `CenterFrontPanel`, `CloseFrontPanel`, `DisconnectFromLibrary`, `ExportVIStrings`, `FPGetRuntimePos`, `FPRunTimePosRun*` (Centered/Custom/Max/Min/Unchanged), `GetControlValue`, `GetLockState`, `GetVIDependencies`, `ImportVIStrings`, `MakeCurValueDefault`, `OpenFrontPanel`, `PrintPanel`, `PrintVIToHTML/Printer/RTF/Text`, `ReinitializeAllToDefault`, `Revert`, `Run`, `SaveForPrevious`, `SaveInstrument`, `SaveRunTimeMenu`, `SetControlValue`, `SetLockState`, `SetVIIcon`. https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/activex/vi-m.html
- Side note: LabVIEW 2026 Q1 adds a per-target override ("Override VI Properties to Enable Debugging" / Project Environment Settings) stored in `.__<project>UserState\<project>.lvprojstate`, without modifying the VI. https://forums.ni.com/t5/LabVIEW-Public-Beta-Program-in/New-2026-Q1-Feature-Enable-Disable-VI-Debugging-Without-File/td-p/4458707

**2. LVSR block, pylabview**

- Debug flag enum (LVinstrument.py): class `VI_IN_ST_FLAGS` ("VI Insrument State flags"), member `DebugCapable = 1 << 9` with comment "Whether you can use debugging tools on the VI. For example, you can set breakpoints, create probes, enable execution highlighting, and single-step through execution." Set = debugging allowed (positive sense). Other members are `InStBit0..InStBit31` (unknown) and `PrintAfterExec = 1 << 15`. https://raw.githubusercontent.com/mefistotelis/pylabview/master/pylabview/LVinstrument.py
- Structure `LVSRData` field order and byte offsets: `version` u32 @0, `execFlags` u32 @4 (`VI_EXEC_FLAGS`), `viFlags2` u32 @8 (`VI_FLAGS2`), `field0C` u32 @12, `flags10` u16 @16, `field12` u16 @18, `buttonsHidden` u16 @20, `frontpFlags` u16 @22, **`instrState` u32 @24 (0x18)**, `execState` u32 @28, `execPrio` u16 @32, `viType` u16 @34, `prefExecSyst` i32 @36, ... `viSignature` 16 bytes @52, ... `inlineStg` u8 @136, `field8C` u32 @140. So `DebugCapable` is bit 9 of the u32 at LVSR offset 0x18 (mask 0x200). Same URL as above.
- Related `VI_EXEC_FLAGS` (u32 at offset 4): `IsReentrant = 1<<5`, `PooledReentrancy = 1<<7`, `HasSetBP = 1<<12`, `LibProtected = 1<<13` (0x2000), `IsSubroutine = 1<<17`, `SaveParallel = 1<<24`, etc. Same URL.
- pylabview wiki "Blocks" page only documents LVSR as version u32 @0, int16 @4, u16 flags @6 with "Protected 0x2000"; it says nothing about debugging. The code (above) is the authoritative layout. https://github.com/mefistotelis/pylabview/wiki/Blocks
- Not found: I could not retrieve the `class LVSR` parser in LVblock.py (file truncated by my fetch), so any version-dependent block length for 2020+ is unverified. https://github.com/mefistotelis/pylabview/blob/master/pylabview/LVblock.py

**3. LabVIEW.ini profiler / debugging tokens**

- Profiler tokens that start or auto-save profiling: **none found**. LabVIEW Wiki Debugging, Performance, Execution System and Miscellaneous pages contain no "profil*" token. https://labviewwiki.org/wiki/LabVIEW_configuration_file/Debugging , https://labviewwiki.org/wiki/LabVIEW_configuration_file/Performance , https://labviewwiki.org/wiki/LabVIEW_configuration_file/Execution_System , https://labviewwiki.org/wiki/LabVIEW_configuration_file/Miscellaneous
- Debugging tokens (Wiki Debugging page): `DWarnDialog`, `showExePathInWindowTitle`, `prettyExecHilite`, `autoProbe`, `showWarnings`, `massCompAll`. https://labviewwiki.org/wiki/LabVIEW_configuration_file/Debugging
- Undocumented debugging tokens: `debugging` (runtime checks logged to `<lvdir>\dprintf.txt`), `LVdebugKeys` (Ctrl+Shift+H/W internal monitors, Heap Peek), `memoryChecking`, `nodeBreakPointMenuItem`; also `DPrintfLogging=True`. https://labview.brianrenken.com/INI/undoc.htm and https://blog.dmitriev.de/labview/ini_keys/hidden_ini_keys/

Sources:
- [VI class/Execution.Allow Debugging property - LabVIEW Wiki](https://labviewwiki.org/wiki/VI_class/Execution.Allow_Debugging_property)
- [VI class - LabVIEW Wiki](https://labviewwiki.org/wiki/VI_class)
- [AllowDebugging (ActiveX) - NI](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/activex/vi/allowdebugging.html)
- [VI Properties (ActiveX) - NI](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/activex/vi-p.html)
- [VI Methods (ActiveX) - NI](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/activex/vi-m.html)
- [pylabview LVinstrument.py](https://raw.githubusercontent.com/mefistotelis/pylabview/master/pylabview/LVinstrument.py)
- [pylabview wiki Blocks](https://github.com/mefistotelis/pylabview/wiki/Blocks)
- [LabVIEW configuration file/Debugging](https://labviewwiki.org/wiki/LabVIEW_configuration_file/Debugging)
- [Undocumented INI settings](https://labview.brianrenken.com/INI/undoc.htm)
- [LabVIEW's hidden INI Keys](https://blog.dmitriev.de/labview/ini_keys/hidden_ini_keys/)
- [NI 2026 Q1 debugging override](https://forums.ni.com/t5/LabVIEW-Public-Beta-Program-in/New-2026-Q1-Feature-Enable-Disable-VI-Debugging-Without-File/td-p/4458707)

## Sources

(extract from answer)

## What was done with it

Card 89-3. USED: the pylabview layout (`LVSRData.instrState` u32 @0x18, `VI_IN_ST_FLAGS.DebugCapable = 1<<9`,
answer §2) is the decode in `tools/bench/diag_c89_profiler_lvsr.py`; measured on 5 files
(`tools/bench/diag_c89_profiler_lvsr.log`, 15/0): D1_s1_copy / ORIGINAL / kswap all `instrState=0x40800210` →
DebugCapable TRUE; NI's `vi.lib\Utility\High Resolution Relative Seconds.vi` → FALSE with LibProtected TRUE, so the
bit discriminates as claimed. The ActiveX `VirtualInstrument.AllowDebugging` route (§1) is recorded in the plan as the
headless COM cross-check (`--com` switch of the same diag), NOT run in this card (it would start LabVIEW; the offline
read already answers). Property ID "206" from the LabVIEW Wiki is NOT registered in `docs/vi-server-ids.json` — left
unverified, not needed. §3: no profiler ini token → negative-search record.
