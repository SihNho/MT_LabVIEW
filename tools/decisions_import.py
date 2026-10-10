# ---
# labview: none
# hardware: none
# offline-args: selftest
# evidence: tools/bench/cards/task_chat-X1.json
# ---
"""decisions_import.py - copy the user's decisions out of Claude Code's private memory directory into the repo.

Card chat-X1 (user 2026-10-10): the project must continue from ANY session (Claude Code or Codex), so the decisions
that so far lived only in `~/.claude/projects/<this project>/memory/*.md` are copied to `docs/decisions/<same name>.md`:
the original frontmatter kept line for line, `type` / `status` / `date` / `source` (and `superseded_by`) added, the
body VERBATIM. `docs/decisions/INDEX.md` lists one line per decision grouped by topic; superseded ones at the end.

The memory directory is READ ONLY here (card rule "do not modify ~/.claude memory dir"). MEMORY.md (the memory index)
is not copied - INDEX.md replaces it. Re-running overwrites the copies (idempotent); a memory file with no TOPIC entry
below fails the run, so a new memory file cannot be silently left out.

Existing tools checked first: `tools/frontmatter.py` (adds default frontmatter to docs without one - not a copier),
no other tool reads the memory directory.

  py tools/decisions_import.py            # write docs/decisions/*.md + INDEX.md
  py tools/decisions_import.py selftest   # parse/compose checks on an in-memory sample, writes nothing
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "docs", "decisions")
MEM = os.path.join(os.path.expanduser("~"), ".claude", "projects",
                   "G--Codes-LabVIEW-Codes-MinLab-zz-LabView-VI-AAA-UNIST-2--Tracking-V6-ParallelLoop", "memory")

GROUPS = [
    ("hw", "Hardware, motors and the rig"),
    ("orig", "Originals, computation and the new VI's design"),
    ("lv", "LabVIEW technique"),
    ("run", "Runner, cycles and sessions"),
    ("model", "Models and cost"),
    ("rev", "Reviews and peers"),
    ("doc", "Documents"),
    ("com", "Reporting and communication with the user"),
]

TOPIC = {
    # hardware, motors, rig
    "hardware_operation_permission": "hw", "hardware_do_not_run_the_motor": "hw",
    "hardware_never_operate_asi_piezo_stage": "hw", "motor_safe_motion_envelope": "hw",
    "motor_limits_set_and_released_every_cycle": "hw", "pi_reference_at_every_cycle_start": "hw",
    "motors_allowed_real_runs_close_labview": "hw", "rotor_follows_signed_hardware_count": "hw",
    "no_serial_on_the_frame_path": "hw", "rig_reassembly_is_a_last_resort": "hw",
    "camera_free_runs_never_gate_it": "hw", "camera_settings_in_vi_cal_out_of_scope": "hw",
    "experimental_load_beads_and_frame_rate": "hw", "ramping_tolerates_background_load": "hw",
    "plan_everything_possible_before_the_rig": "hw", "unattended_runs_drive_bead_picking_by_gui": "hw",
    "main_vi_run_sequence_needs_bead_clicks": "hw",
    # originals, computation, design of the new VI
    "preserve_the_original_computation": "orig", "restructure_inside_a_copy_of_the_original": "orig",
    "build_it_right_original_vi_runs_experiments": "orig", "user_owns_the_original_vi_state": "orig",
    "tiff_writer_is_a_fixture_insertion_not_original": "orig",
    "prioritize_semantic_analysis_read_the_main_vi": "orig",
    "diagram_was_cleaned_up_position_means_nothing": "orig", "read_the_code_before_asking": "orig",
    "ask_the_user_about_rig_domain_meaning": "orig", "locals_not_queues_focus_loop_own_clock": "orig",
    "display_in_separate_loop_fed_by_locals": "orig", "display_policy_and_camera_panel_decisions": "orig",
    "prefer_the_freshest_frame_over_a_complete_backlog": "orig", "gpu_is_the_default_top_level_vi": "orig",
    "gpu_backend_acceptance_tolerance": "orig", "keep_cpu_and_gpu_tracking_backends": "orig",
    "tracking_backend_selectable_subvi": "orig", "design_gpu_interface_fresh_not_saleh": "orig",
    "three_way_benchmark_in_labview": "orig", "delivery_cycles_are_a_means_to_the_final_step": "orig",
    "project_v6_parallelization": "orig",
    # LabVIEW technique
    "build_tool_vis_by_scripting_not_clicking": "lv", "close_every_reference_verified_by_handle_count": "lv",
    "timeouts_must_be_mechanical_and_unbypassable": "lv", "watchdog_long_running_processes": "lv",
    "labview_restart_standing_permission": "lv", "scratch_instances_are_free_to_kill": "lv",
    "create_and_delete_scratch_targets": "lv", "two_labview_versions_2026_harness_2019_rig": "lv",
    "labview_renders_panels_on_cpu_not_gpu": "lv", "context_help_shows_which_terminal_is_targeted": "lv",
    "labview_snaps_to_terminals_hover_and_verify": "lv", "verify_wiring_by_scripting_not_screenshots": "lv",
    "gui_click_optimization_first": "lv", "gui_actions_need_before_after_capture": "lv",
    "gui_control_must_compare_captures": "lv", "bank_gui_control_knowledge_after_each_success": "lv",
    "uitars_local_grounder_chosen": "lv", "consider_gemini_vision_executor_for_gui_loop": "lv",
    "reuse_existing_vi_scripting_libraries": "lv", "interpreter_style_scripting_driver": "lv",
    "batch_async_scripting_workflow": "lv", "driver_vi_inputs_as_controls": "lv",
    "feedback_labview_session_reuse": "lv", "feedback_shared_labview_checkpointing": "lv",
    "broken_intermediate_gui_save_allowed": "lv", "offline_prerun_and_error_list_before_labview": "lv",
    "split_big_steps_and_save_intermediates": "lv", "build_offline_test_fixtures": "lv",
    "consecutive_runs_wait_by_condition": "lv", "establish_cheap_automation_standard_before_grinding": "lv",
    # runner, cycles, sessions
    "cycles_run_in_fresh_sessions_via_runner": "run", "new_session_meant_fresh_subagents": "run",
    "purpose_cycles_assignment_session": "run", "deliverable_first_hooks_outside_runner": "run",
    "deliverable_build_goes_first_in_a_cycle": "run", "finish_the_cycle_without_stopping": "run",
    "graceful_shutdown_finish_the_cycle": "run", "runner_time_budget_is_not_a_stop": "run",
    "stop_runner_at_weekly_90": "run", "acceleration_items_2026_09_28": "run",
    "parallelize_only_independent_work": "run", "json_protocol_goalmap_pending_decisions": "run",
    "fable_firefighter_cycle_on_trigger": "run", "intra_cycle_escalation_to_fable": "run",
    "judgement_vs_material_session_split": "run", "agent_vs_session_terminology": "run",
    "tools_allowed_when_cycle_judges_them_necessary": "run", "guards_exist_to_catch_errors_early": "run",
    "procedural_rules_need_refusal_not_reminders": "run", "counting_must_live_in_files_not_in_my_memory": "run",
    "five_step_batch_cycle_and_layered_docs": "run", "quota_limit_schedule_resume_and_rerun": "run",
    "chat_compacts_instead_of_handoff": "run", "backend_agnostic_project_goal": "run",
    "secrets_env_only_and_handover_planned": "run",
    # models and cost
    "fable_usage_cost_control": "model", "model_table_2026_09_27": "model",
    "model_ladders_fable_low_material_judgement_by_signal": "model", "opus_55_pinned_effort_high_not_max": "model",
    "benchmark_models_before_adopting": "model", "score_models_by_total_cost_to_success": "model",
    "run_mode_economy_performance": "model", "cloud_credit_interactive_sessions_only": "model",
    "ultracode_out_jev_for_bulk_checks": "model",
    # reviews and peers
    "review_structure_has_three_layers": "rev", "prior_art_review_is_the_fourth_peer": "rev",
    "devils_advocate_before_acting_on_a_diagnosis": "rev", "recurring_errors_become_peer_review_triggers": "rev",
    "search_the_web_when_troubleshooting": "rev", "research_fallback_ladder": "rev",
    "peer_agents_for_troubleshooting": "rev", "claude_subsessions_join_the_peer_pool": "rev",
    "codex_roles_move_to_claude": "rev", "gemini_roles_delegated_to_claude": "rev",
    "hypothesis_reviews_move_to_opus_max": "rev", "repeated_outcome_verdict_does_not_stop": "rev",
    "jev_exception_to_no_new_device": "rev", "jev_apply_broadly_not_just_firefighter": "rev",
    "jev_per_item_verification_llm_sums_up": "rev", "claude_gpt_debate_live_gdoc": "rev",
    # documents
    "docs_are_linted_and_ingested_every_cycle": "doc", "archive_history_dont_read_it_by_default": "doc",
    "claude_writes_every_document_here": "doc", "archive_benchmarks_for_meeting_reports": "doc",
    "obsidian_vault_needs_ingest_not_direct_writes": "doc", "wiki_agent_debate_and_machine_notes": "doc",
    "user_wants_learnable_labview_notes": "doc", "always_attribute_third_party_code": "doc",
    "labview_knowledge_must_be_portable_across_projects": "doc",
    "turn_labview_findings_into_guidelines_and_audit_docs": "doc",
    # reporting and communication
    "report_runner_events_without_being_asked": "com", "prose_must_be_reviewed_before_showing": "com",
    "explain_in_plain_language": "com", "no_coined_terms_use_standard_names": "com",
    "stay_responsive_during_long_work": "com", "state_confidence_before_the_user_has_to_ask": "com",
    "presentation_slide_count_leaves_room_for_questions": "com",
    "user_added_slides_are_content_restyle_them": "com", "approved_means_do_it_now": "com",
    "discuss_the_design_before_building_it": "com", "ask_the_user_when_blocked": "com",
    "wait_for_start_after_design_discussion": "com", "judge_changes_on_two_axes_speed_and_cost": "com",
}

# SUPERSEDED only where the file itself or a later decision says so (card rule). slug -> (superseded_by, evidence)
SUPERSEDED = {
    "hardware_do_not_run_the_motor": ("hardware_operation_permission",
                                      "its own description: SUPERSEDED 2026-09-16"),
    "hardware_never_operate_asi_piezo_stage": ("hardware_operation_permission",
                                               "its own description: SUPERSEDED 2026-09-16"),
    "hypothesis_reviews_move_to_opus_max": ("codex_roles_move_to_claude",
                                            "codex_roles_move_to_claude (2026-09-18): the five-comparison trial has "
                                            "effectively run, hypothesis reviews on the claude peer alone; model now "
                                            "Opus 5.5 high per model_table_2026_09_27"),
    "model_ladders_fable_low_material_judgement_by_signal": ("model_table_2026_09_27",
                                                             "model_table_2026_09_27: material Opus 5.5 high, the "
                                                             "Fable-low material trial ended (3x cost, no gain)"),
}

FM_RE = re.compile(r"\A﻿?---\r?\n(.*?)\r?\n---\r?\n", re.S)


def split(text):
    """(frontmatter_lines, body) of a memory file; frontmatter_lines is [] when the file has none."""
    m = FM_RE.match(text)
    if not m:
        return [], text
    return m.group(1).splitlines(), text[m.end():]


def field(lines, key):
    """The value of a top-level `key:` line (quotes stripped), or ''."""
    for ln in lines:
        if ln.startswith(key + ":"):
            v = ln.split(":", 1)[1].strip()
            if len(v) >= 2 and v[0] == v[-1] == '"':
                v = v[1:-1].replace('\\"', '"')
            return v
    return ""


def modified_date(lines, path):
    for ln in lines:
        m = re.match(r"\s*modified:\s*(\d{4}-\d{2}-\d{2})", ln)
        if m:
            return m.group(1)
    import time
    return time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(path))) if path else "2026-10-10"


def compose(slug, fm_lines, body, date):
    """The repo copy: original frontmatter lines + the added keys, then the body verbatim."""
    st = "superseded" if slug in SUPERSEDED else "in-force"
    add = ["type: decision", "status: %s" % st, "date: %s" % date, "source: memory/%s.md" % slug]
    if slug in SUPERSEDED:
        add.append("superseded_by: %s" % SUPERSEDED[slug][0])
    keep = [ln for ln in fm_lines if not re.match(r"(type|status|date|source|superseded_by):", ln)]
    return "---\n" + "\n".join(keep + add) + "\n---\n" + body


def short(desc, n=170):
    desc = " ".join(desc.split())
    return desc if len(desc) <= n else desc[:n - 1].rstrip() + "…"


def index(entries):
    """docs/decisions/INDEX.md from [(slug, topic, desc, status, date)]."""
    out = ["---", "type: index", "status: reference", "date: 2026-10-10", "tags: [decisions, index]", "---", "",
           "# Decisions - index",
           "",
           "The user's decisions, one file each, copied VERBATIM from Claude Code's memory directory by",
           "`tools/decisions_import.py` (card chat-X1, user 2026-10-10). Every file keeps its original frontmatter and adds",
           "`type`, `status` (`in-force` | `superseded`), `date` and `source`. Rules derived from them: `docs/rules/`.",
           "A later decision wins over an earlier one; a decision the rules contradict is a question for the judgement",
           "session, not a silent override.", ""]
    for key, title in GROUPS:
        rows = [e for e in entries if e[1] == key and e[3] == "in-force"]
        out += ["## %s (%d)" % (title, len(rows)), ""]
        for slug, _, desc, _, date in sorted(rows, key=lambda e: e[0]):
            out.append("- [%s](%s.md) (%s) - %s" % (slug, slug, date, short(desc)))
        out.append("")
    sup = [e for e in entries if e[3] == "superseded"]
    out += ["## Superseded (%d) - history only, do not act on these" % len(sup), ""]
    for slug, _, desc, _, date in sorted(sup):
        by, why = SUPERSEDED[slug]
        out.append("- [%s](%s.md) (%s) - superseded by [%s](%s.md): %s" % (slug, slug, date, by, by, why))
    out.append("")
    return "\n".join(out)


def run():
    names = sorted(f for f in os.listdir(MEM) if f.endswith(".md") and f != "MEMORY.md")
    missing = [n[:-3] for n in names if n[:-3] not in TOPIC]
    stale = [k for k in TOPIC if k + ".md" not in names]
    if missing or stale:
        print("UNMAPPED memory files (add a TOPIC entry): %s; TOPIC entries with no file: %s" % (missing, stale))
        return 1, 0
    os.makedirs(OUT, exist_ok=True)
    entries = []
    for n in names:
        slug = n[:-3]
        p = os.path.join(MEM, n)
        with open(p, encoding="utf-8", newline="") as f:
            text = f.read()
        fm, body = split(text)
        date = modified_date(fm, p)
        with open(os.path.join(OUT, n), "w", encoding="utf-8", newline="") as f:
            f.write(compose(slug, fm, body, date))
        entries.append((slug, TOPIC[slug], field(fm, "description"),
                        "superseded" if slug in SUPERSEDED else "in-force", date))
    with open(os.path.join(OUT, "INDEX.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(index(entries))
    return 0, len(entries)


def selftest():
    sample = '---\nname: x\ndescription: "a \\"b\\" c"\nmetadata: \n  modified: 2026-09-16T03:04:28.019Z\n---\n\n# Body\nline\n'
    fm, body = split(sample)
    ok = []
    ok.append(("frontmatter parsed", fm[0] == "name: x" and body == "\n# Body\nline\n"))
    ok.append(("quoted description", field(fm, "description") == 'a "b" c'))
    ok.append(("modified date", modified_date(fm, None) == "2026-09-16"))
    c = compose("hardware_do_not_run_the_motor", fm, body, "2026-09-16")
    ok.append(("body verbatim", c.endswith("---\n" + body)))
    ok.append(("superseded keys", "status: superseded" in c and "superseded_by: hardware_operation_permission" in c))
    ok.append(("in-force key", "status: in-force" in compose("x", fm, body, "2026-09-16")))
    ok.append(("every group has a title", set(TOPIC.values()) <= {k for k, _ in GROUPS}))
    ok.append(("superseded slugs are mapped", all(k in TOPIC and v[0] in TOPIC for k, v in SUPERSEDED.items())))
    for label, good in ok:
        print("  %s  %s" % ("PASS" if good else "FAIL", label))
    return sum(1 for _, g in ok if g), sum(1 for _, g in ok if not g)


def main():
    sys.path.insert(0, HERE)
    import protocol
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        p, f = selftest()
        print(protocol.result_line({"status": "PASS" if not f else "FAIL", "gates": {"pass": p, "fail": f},
                                    "first_fail": None if not f else "selftest", "artefacts": []}))
        return 1 if f else 0
    rc, n = run()
    art = [] if rc else [{"path": "docs/decisions/INDEX.md", "md5": protocol_md5(os.path.join(OUT, "INDEX.md"))}]
    print("decisions written: %d (+ INDEX.md) -> %s" % (n, OUT))
    print(protocol.result_line({"status": "PASS" if not rc else "FAIL", "gates": {"pass": 1 - rc, "fail": rc},
                                "first_fail": None if not rc else "unmapped memory files", "artefacts": art}))
    return rc


def protocol_md5(p):
    import hashlib
    with open(p, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


if __name__ == "__main__":
    sys.exit(main())
