"""
Swimmingly Season Builder — Clickable MVP Prototype
====================================================
A coach-only dashboard tool that lives inside the Swimmingly Clubhouse.
Helps summer rec swim coaches generate age-appropriate practices for
5–10 week summer seasons.

Run locally:
    pip install streamlit pandas
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta, time, datetime
import random
import json
import os

# =============================================================================
# CONFIG
# =============================================================================
st.set_page_config(
    page_title="Swimmingly Season Builder",
    page_icon="🏊",
    layout="wide",
    initial_sidebar_state="expanded",
)

SWIMMINGLY_BLUE = "#25bfea"
SWIMMINGLY_NAVY = "#101242"
SWIMMINGLY_LIGHT_BLUE = "#8de2f5"
SWIMMINGLY_DARK_GRAY = "#8898aa"
SWIMMINGLY_GRAY = "#a9bfcf"
SWIMMINGLY_LIGHT_GRAY = "#c9d9e4"
TEXT_COLOR = "#101242"  # Navy for all body text — readable on white
SURFACE_BG = "#f4f8fb"  # Soft surface tint based on light gray

# Templates persistence (mock — local JSON file). Swap for DB later.
TEMPLATES_FILE = "schedule_templates.json"

st.markdown(
    f"""
    <style>
        /* Force light surfaces + navy text everywhere, regardless of OS dark mode */
        .stApp {{
            background-color: #ffffff;
        }}
        .main .block-container {{
            padding-top: 2rem;
            max-width: 1200px;
            color: {TEXT_COLOR};
        }}
        .main, .main p, .main li, .main span, .main label, .main div {{
            color: {TEXT_COLOR};
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: {SWIMMINGLY_NAVY} !important;
        }}
        /* Sidebar styling — also navy text on light bg */
        section[data-testid="stSidebar"] {{
            background-color: #f4f8fb;
        }}
        section[data-testid="stSidebar"] * {{
            color: {TEXT_COLOR};
        }}
        /* Primary buttons */
        .stButton>button[kind="primary"] {{
            background-color: {SWIMMINGLY_BLUE};
            color: white !important;
            border: none;
            font-weight: 600;
        }}
        .stButton>button[kind="primary"]:hover {{
            background-color: {SWIMMINGLY_NAVY};
            color: white !important;
        }}
        /* Secondary buttons */
        .stButton>button[kind="secondary"] {{
            background-color: white;
            color: {SWIMMINGLY_NAVY} !important;
            border: 1px solid {SWIMMINGLY_LIGHT_GRAY};
        }}
        .stButton>button[kind="secondary"]:hover {{
            background-color: {SURFACE_BG};
            border-color: {SWIMMINGLY_BLUE};
        }}
        /* Practice cards */
        .practice-card {{
            background: {SURFACE_BG};
            border: 1px solid {SWIMMINGLY_LIGHT_GRAY};
            border-left: 4px solid {SWIMMINGLY_BLUE};
            padding: 14px 16px;
            border-radius: 8px;
            margin-bottom: 10px;
            color: {TEXT_COLOR};
        }}
        .practice-card * {{
            color: {TEXT_COLOR};
        }}
        /* Week headers */
        .week-header {{
            background: {SWIMMINGLY_BLUE};
            color: white !important;
            padding: 8px 14px;
            border-radius: 6px;
            font-weight: 600;
            margin: 16px 0 8px 0;
        }}
        /* Practice plan time blocks */
        .block-box {{
            background: {SURFACE_BG};
            border-left: 3px solid {SWIMMINGLY_BLUE};
            padding: 12px 16px;
            margin-bottom: 12px;
            border-radius: 4px;
            color: {TEXT_COLOR};
        }}
        .block-box * {{
            color: {TEXT_COLOR};
        }}
        .block-box strong {{
            color: {SWIMMINGLY_NAVY};
        }}
        /* Stat cards on dashboard */
        .stat-card {{
            background: white;
            border: 1px solid {SWIMMINGLY_LIGHT_GRAY};
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 28px;
            font-weight: 700;
            color: {SWIMMINGLY_BLUE};
        }}
        .stat-label {{
            font-size: 13px;
            color: {SWIMMINGLY_DARK_GRAY};
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        /* Schedule rows on dashboard */
        .sched-row {{
            background: {SURFACE_BG};
            border: 1px solid {SWIMMINGLY_LIGHT_GRAY};
            border-radius: 6px;
            padding: 10px 12px;
            margin-bottom: 6px;
            color: {TEXT_COLOR};
        }}
        .sched-row * {{
            color: {TEXT_COLOR};
        }}
        /* Captions and helper text */
        .stCaption, [data-testid="stCaptionContainer"] {{
            color: {SWIMMINGLY_DARK_GRAY} !important;
        }}
        /* Form inputs — readable on light bg */
        .stTextInput input, .stTextArea textarea, .stDateInput input,
        .stTimeInput input, .stSelectbox div[data-baseweb="select"],
        .stMultiSelect div[data-baseweb="select"] {{
            background-color: white !important;
            color: {TEXT_COLOR} !important;
        }}
        /* Tables and dataframes */
        .stDataFrame, .stTable {{
            color: {TEXT_COLOR};
        }}
        /* Markdown content default text */
        .stMarkdown {{
            color: {TEXT_COLOR};
        }}
        /* Info/success/warning boxes — make sure text is readable */
        .stAlert {{
            color: {TEXT_COLOR};
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# MOCK DATA — DRILL LIBRARY (sourced from Swimmingly curriculum & drills.swimmingly.app)
# =============================================================================
DRILL_LIBRARY = {
    "freestyle": [
        {"name": "Catch-Up Freestyle", "cue": "One hand always touches the other at full extension before pulling.", "level": "novice"},
        {"name": "Fingertip Drag", "cue": "Drag fingertips on the surface to promote high elbow recovery.", "level": "all"},
        {"name": "Fist Drill", "cue": "Swim with closed fists to feel the forearm catch and connection.", "level": "intermediate"},
        {"name": "6-Kick Switch", "cue": "One arm forward, kick on side for 6 kicks, then switch arms with one stroke.", "level": "all"},
        {"name": "Single-Arm Freestyle", "cue": "One arm pulls, the other rests by the hip. Focus on rotation from the core.", "level": "intermediate"},
        {"name": "Popeye Drill", "cue": "One goggle in, one out when breathing. Low head, slight turn to inhale.", "level": "novice"},
        {"name": "Sailboat Kick Drill", "cue": "One arm extended, one arm up toward the sky. Strong steady flutter kick.", "level": "all"},
        {"name": "3 Stroke Breathing", "cue": "Breathe every 3 strokes to build balance and bilateral rhythm.", "level": "all"},
        {"name": "Count-Your-Strokes", "cue": "Maintain a consistent number of strokes per length.", "level": "intermediate"},
        {"name": "Streamline Kick on Side", "cue": "On side in streamline, kick steady — focuses balance and body line.", "level": "all"},
    ],
    "backstroke": [
        {"name": "Backstroke 6-Kick Switch", "cue": "On back, one arm up, kick 6 on side, then switch with one stroke.", "level": "all"},
        {"name": "Single-Arm Backstroke", "cue": "One arm pulls while the other rests at the side. Drive rotation from hips.", "level": "intermediate"},
        {"name": "Double-Arm Backstroke", "cue": "Both arms pull together with high elbow catch and steady flutter kick.", "level": "novice"},
        {"name": "Backstroke Cup Drill", "cue": "Balance a cup of water on the forehead — head must stay still.", "level": "all"},
        {"name": "L Kick Drill", "cue": "On back, one arm up, one at side — switch every 10 kicks for rotation balance.", "level": "all"},
        {"name": "Streamline Backstroke Kick", "cue": "Streamline on back, dolphin or flutter kick — focuses underwater speed.", "level": "all"},
    ],
    "breaststroke": [
        {"name": "Breaststroke Kick with Board", "cue": "Heels to seat, knees inside shoulders, snap feet together.", "level": "novice"},
        {"name": "Breaststroke Pullout Practice", "cue": "Pull, kick, glide. One stroke per length — feel the streamline.", "level": "intermediate"},
        {"name": "2 Kicks 1 Pull", "cue": "Two kicks per arm pull — exaggerates the glide and timing.", "level": "all"},
        {"name": "3-Second Glide Breast", "cue": "Hold streamline glide for a count of 3 between each stroke.", "level": "all"},
        {"name": "Breaststroke Body Wave", "cue": "Smooth undulation — heels up, hips drive forward through glide.", "level": "intermediate"},
    ],
    "butterfly": [
        {"name": "Butterfly Body Dolphin", "cue": "Arms at sides, smooth body undulation driven from the chest.", "level": "novice"},
        {"name": "One-Arm Butterfly", "cue": "One arm pulls, other extended forward. 2 kicks per cycle.", "level": "intermediate"},
        {"name": "3-3-3 Butterfly", "cue": "3 right-arm, 3 left-arm, 3 full stroke butterfly continuously.", "level": "intermediate"},
        {"name": "Side Breathing Butterfly", "cue": "Quick side breath — head returns down immediately, no lift.", "level": "intermediate"},
        {"name": "Dolphin Kick on Back", "cue": "Streamline on back, strong dolphin kick — builds underwater power.", "level": "all"},
    ],
    "turns_starts": [
        {"name": "Start + Streamline Breakout", "cue": "Tight streamline off the wall, 3 dolphin kicks, sharp breakout.", "level": "all"},
        {"name": "Turn + Push-Off Practice", "cue": "Approach with speed, tuck tight, eyes to knees, push straight.", "level": "all"},
        {"name": "Streamline Push-Offs", "cue": "Push off, hold streamline — glide until surface, then swim.", "level": "novice"},
        {"name": "Vertical Flip Turns", "cue": "Stand, jump, flip in air, land in streamline — builds awareness.", "level": "novice"},
        {"name": "Wall Turns", "cue": "Sprint to wall from flags, flip, streamline past flags, stop.", "level": "all"},
        {"name": "Backstroke Start Drill", "cue": "Explosive push, arched back, tight streamline with fast dolphins.", "level": "intermediate"},
    ],
    "kick_streamline": [
        {"name": "Streamline Kick", "cue": "Tight streamline, ears squeezed by biceps, strong steady kick.", "level": "all"},
        {"name": "Sculling", "cue": "Hands sweep in/out at the front of the stroke — feel the water.", "level": "all"},
        {"name": "Kick on Back Streamline", "cue": "Streamline on back, hips up, steady flutter — focuses balance.", "level": "novice"},
        {"name": "Vertical Kicking", "cue": "Tread water with no arms — builds kick strength and core.", "level": "intermediate"},
    ],
}


# =============================================================================
# AGE GROUP CONFIG
# Yardage now scales with actual minutes — custom durations are supported.
# =============================================================================
AGE_GROUPS = {
    "6 & Under": {"default_duration": 30, "yards_per_min": 10, "complexity": "intro"},
    "7-8":       {"default_duration": 45, "yards_per_min": 11, "complexity": "novice"},
    "9-10":      {"default_duration": 45, "yards_per_min": 18, "complexity": "novice"},
    "11-12":     {"default_duration": 60, "yards_per_min": 23, "complexity": "intermediate"},
    "13-14":     {"default_duration": 60, "yards_per_min": 32, "complexity": "intermediate"},
    "15-18":     {"default_duration": 60, "yards_per_min": 40, "complexity": "advanced"},
}

DEFAULT_WARMUPS = {
    "6 & Under": "4x25 Choice (with kickboard if needed) — focus on streamline push-offs and big strong kicks.",
    "7-8":       "200 Choice: 4x25 Free + 4x25 Kick on back. Streamline off every wall.",
    "9-10":      "300 Choice: 6x25 Free + 6x25 Kick (mix front/back). Push-off past flags.",
    "11-12":     "400 Warm-up: 200 Free smooth + 4x25 Drill + 4x25 Build. Streamline every wall.",
    "13-14":     "500 Warm-up: 300 Choice + 4x50 Kick (25 fast / 25 easy) + 4x25 Build by 25.",
    "15-18":     "600 Warm-up: 300 Free + 4x50 IM Drill + 4x50 Kick + 4x25 Build. Sharp streamlines.",
}

PRACTICE_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
DAY_INDEX = {d: i for i, d in enumerate(PRACTICE_DAYS)}

SEASON_GOALS = [
    "Fun & Retention",
    "Technique Development",
    "Time Drops / Racing",
    "Stroke Development",
    "Endurance",
    "Starts, Turns, and Finishes",
]


# =============================================================================
# SCHEDULE BLOCK HELPERS
# =============================================================================
def default_schedule():
    """Stacked default schedule: each age group back-to-back from 4:00 PM."""
    blocks = []
    cursor = time(16, 0)
    for ag, cfg in AGE_GROUPS.items():
        dur = cfg["default_duration"]
        end = add_minutes(cursor, dur)
        blocks.append({
            "id": f"block_{ag.replace(' ', '_').replace('&', 'and')}",
            "age_groups": [ag],
            "label": ag,
            "start_time": cursor,
            "end_time": end,
            "duration_min": dur,
            "enabled": True,
        })
        cursor = end
    return blocks


def add_minutes(t: time, mins: int) -> time:
    dt = datetime.combine(date.today(), t) + timedelta(minutes=mins)
    return dt.time()


def minutes_between(t1: time, t2: time) -> int:
    d1 = datetime.combine(date.today(), t1)
    d2 = datetime.combine(date.today(), t2)
    return int(round((d2 - d1).total_seconds() / 60))


def fmt_time(t: time) -> str:
    return t.strftime("%I:%M %p").lstrip("0")


# 15-min options across a full day, formatted as "1:00 PM"
TIME_OPTIONS = [time(h, m) for h in range(24) for m in (0, 15, 30, 45)]
TIME_OPTION_LABELS = {t: fmt_time(t) for t in TIME_OPTIONS}


def nearest_time_option(t: time) -> time:
    """Snap a time to the nearest 15-min slot in TIME_OPTIONS."""
    total_min = t.hour * 60 + t.minute
    snapped = round(total_min / 15) * 15
    snapped = max(0, min(snapped, 23 * 60 + 45))
    return time(snapped // 60, snapped % 60)


def primary_age_group(block: dict) -> str:
    """For combined blocks, primary = oldest group. Drives yardage/complexity."""
    order = list(AGE_GROUPS.keys())
    return max(block["age_groups"], key=lambda ag: order.index(ag))


def block_complexity(block: dict) -> str:
    return AGE_GROUPS[primary_age_group(block)]["complexity"]


# =============================================================================
# TEMPLATES PERSISTENCE (mock — local JSON)
# =============================================================================
def _serialize_blocks(blocks):
    out = []
    for b in blocks:
        nb = dict(b)
        if isinstance(b["start_time"], time):
            nb["start_time"] = b["start_time"].isoformat()
        if isinstance(b["end_time"], time):
            nb["end_time"] = b["end_time"].isoformat()
        out.append(nb)
    return out


def _deserialize_blocks(blocks):
    out = []
    for b in blocks:
        nb = dict(b)
        if isinstance(b["start_time"], str):
            nb["start_time"] = time.fromisoformat(b["start_time"])
        if isinstance(b["end_time"], str):
            nb["end_time"] = time.fromisoformat(b["end_time"])
        out.append(nb)
    return out


def load_templates() -> dict:
    if not os.path.exists(TEMPLATES_FILE):
        return {}
    try:
        with open(TEMPLATES_FILE) as f:
            raw = json.load(f)
        return {name: _deserialize_blocks(blocks) for name, blocks in raw.items()}
    except Exception:
        return {}


def save_template(name: str, blocks: list) -> bool:
    templates = load_templates()
    templates[name] = blocks
    try:
        out = {n: _serialize_blocks(bs) for n, bs in templates.items()}
        with open(TEMPLATES_FILE, "w") as f:
            json.dump(out, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Could not save template: {e}")
        return False


def delete_template(name: str):
    templates = load_templates()
    if name in templates:
        del templates[name]
        out = {n: _serialize_blocks(bs) for n, bs in templates.items()}
        with open(TEMPLATES_FILE, "w") as f:
            json.dump(out, f, indent=2)


# =============================================================================
# SEASON PHASING
# =============================================================================
def get_phase(week_num: int, total_weeks: int) -> str:
    if week_num == total_weeks:
        return "Final Week (Taper)"
    pct = week_num / total_weeks
    if pct <= 0.35:
        return "Early Season"
    elif pct <= 0.70:
        return "Mid-Season"
    else:
        return "Late Season"


PHASE_THEMES = {
    "Early Season": [
        ("Freestyle Body Position & Streamline", "freestyle", "kick_streamline"),
        ("Backstroke Fundamentals", "backstroke", "kick_streamline"),
        ("Kick Foundations & Body Line", "kick_streamline", "freestyle"),
        ("Breaststroke Kick Basics", "breaststroke", "kick_streamline"),
        ("Freestyle Breathing & Rotation", "freestyle", "freestyle"),
        ("Backstroke Body Position", "backstroke", "backstroke"),
        ("Streamline & Push-Offs", "kick_streamline", "turns_starts"),
    ],
    "Mid-Season": [
        ("Stroke Refinement: Freestyle", "freestyle", "freestyle"),
        ("Stroke Refinement: Backstroke", "backstroke", "backstroke"),
        ("Breaststroke Legal Technique", "breaststroke", "breaststroke"),
        ("Butterfly Body Dolphin Intro", "butterfly", "kick_streamline"),
        ("Flip Turns & Wall Transitions", "turns_starts", "freestyle"),
        ("Endurance Build — Free/Back", "freestyle", "backstroke"),
        ("IM Rotation Day", "freestyle", "butterfly"),
    ],
    "Late Season": [
        ("Race Pace Freestyle", "freestyle", "turns_starts"),
        ("Sprint Backstroke & Underwaters", "backstroke", "turns_starts"),
        ("Starts & Finishes", "turns_starts", "freestyle"),
        ("Relay Exchanges & Speed", "turns_starts", "freestyle"),
        ("All-Stroke Sharpening", "butterfly", "breaststroke"),
        ("Race Skill Integration", "freestyle", "turns_starts"),
    ],
    "Final Week (Taper)": [
        ("Taper: Sharp & Fast", "freestyle", "turns_starts"),
        ("Race Readiness — Fun & Confidence", "freestyle", "turns_starts"),
    ],
}


# =============================================================================
# PRACTICE GENERATOR
# Takes a schedule block (with custom duration) instead of just age group.
# =============================================================================
def generate_practice(
    block: dict,
    week_num: int,
    total_weeks: int,
    practice_date: date,
    practice_num_in_week: int,
    primary_goals: list,
    coach_notes: str = "",
    custom_warmup: str = None,
    intensity_mod: str = "balanced",
    pool_unit: str = "yards",
) -> dict:
    phase = get_phase(week_num, total_weeks)
    primary_ag = primary_age_group(block)
    age_cfg = AGE_GROUPS[primary_ag]
    duration = block["duration_min"]
    complexity = block_complexity(block)
    is_combined = len(block["age_groups"]) > 1

    # Yardage scales with actual minutes from the schedule
    base_yardage = age_cfg["yards_per_min"] * duration

    theme_options = PHASE_THEMES[phase]
    theme_idx = (week_num + practice_num_in_week) % len(theme_options)
    theme_name, primary_cat, secondary_cat = theme_options[theme_idx]

    if "Starts, Turns, and Finishes" in primary_goals and phase in ("Mid-Season", "Late Season"):
        if random.random() < 0.4:
            theme_name = "Starts, Turns & Finishes Focus"
            primary_cat = "turns_starts"

    if "Fun & Retention" in primary_goals and primary_ag in ("6 & Under", "7-8"):
        fun_finisher = True
    else:
        fun_finisher = random.random() < 0.55

    phase_mult = {"Early Season": 0.85, "Mid-Season": 1.0, "Late Season": 1.05, "Final Week (Taper)": 0.75}[phase]
    intensity_mult = {"easier": 0.8, "balanced": 1.0, "harder": 1.2, "fun": 0.85, "technique": 0.9}[intensity_mod]
    if "Endurance" in primary_goals:
        intensity_mult *= 1.1
    if is_combined:
        intensity_mult *= 0.92  # combined groups go slightly easier than the oldest group alone
    estimated_yardage = int(round(base_yardage * phase_mult * intensity_mult / 25) * 25)

    warmup = custom_warmup or DEFAULT_WARMUPS[primary_ag]

    def pick_drills(category, n=2):
        pool = DRILL_LIBRARY.get(category, [])
        if complexity == "intro":
            pool = [d for d in pool if d["level"] in ("novice", "all")]
        elif complexity == "novice":
            pool = [d for d in pool if d["level"] in ("novice", "all", "intermediate")]
        return random.sample(pool, min(n, len(pool))) if pool else []

    skill_drills = pick_drills(primary_cat, 2 if duration >= 45 else 1)
    if duration >= 60:
        skill_drills += pick_drills(secondary_cat, 1)
    if duration >= 90:
        skill_drills += pick_drills(secondary_cat, 1)

    blocks_layout = build_time_blocks(duration)
    unit = "yds" if pool_unit == "yards" else "m"

    main_set_text = build_main_set(primary_cat, complexity, phase, estimated_yardage, intensity_mod, unit)
    race_skill = build_race_skill(phase, primary_ag, fun_finisher, primary_goals)
    cool_down_yards = max(50, int(round(estimated_yardage * 0.05 / 25) * 25))
    cool_down = f"{cool_down_yards} {unit} EZ — Coach's choice, smooth and relaxed. Focus on breathing down."
    cues = build_coach_cues(primary_cat, phase)
    novice_variation, advanced_variation = build_variations(estimated_yardage, is_combined)

    title = f"{theme_name} — Week {week_num}"

    return {
        "id": f"{block['id']}-{week_num}-{practice_num_in_week}",
        "title": title,
        "date": practice_date,
        "week_num": week_num,
        "phase": phase,
        "block_id": block["id"],
        "block_label": block["label"],
        "age_groups": list(block["age_groups"]),
        "is_combined": is_combined,
        "primary_age_group": primary_ag,
        "duration": duration,
        "start_time": block["start_time"],
        "end_time": block["end_time"],
        "theme": theme_name,
        "estimated_yardage": estimated_yardage,
        "pool_unit": unit,
        "blocks": [
            {"name": "Warm-up", "minutes": blocks_layout[0], "content": warmup},
            {"name": "Skill / Technique", "minutes": blocks_layout[1],
             "content": format_skill_block(skill_drills, complexity, unit)},
            {"name": "Main Set", "minutes": blocks_layout[2], "content": main_set_text},
            {"name": "Race Skill or Fun", "minutes": blocks_layout[3], "content": race_skill},
            {"name": "Cool-down", "minutes": blocks_layout[4], "content": cool_down},
        ],
        "skill_drills": skill_drills,
        "coach_cues": cues,
        "novice_variation": novice_variation,
        "advanced_variation": advanced_variation,
        "fun_finisher": "Sharks & Minnows across the shallow end (last 3 min)" if fun_finisher else None,
        "coach_notes": coach_notes,
        "edited_notes": "",
    }


def build_time_blocks(duration: int) -> list:
    """Allocate minutes across the 5 sections, scaling proportionally with total duration."""
    if duration <= 30:
        props = [0.20, 0.30, 0.30, 0.13, 0.07]
    elif duration <= 45:
        props = [0.18, 0.27, 0.33, 0.13, 0.09]
    elif duration <= 60:
        props = [0.17, 0.25, 0.37, 0.13, 0.08]
    elif duration <= 90:
        props = [0.15, 0.22, 0.45, 0.12, 0.06]
    else:
        props = [0.13, 0.20, 0.50, 0.12, 0.05]
    out = [int(round(duration * p)) for p in props]
    diff = duration - sum(out)
    if diff != 0:
        out[2] += diff  # absorb into main set
    return out


def format_skill_block(drills, complexity, unit):
    if not drills:
        return "Coach's Choice — pick 1–2 drills focused on today's stroke."
    reps = {"intro": 2, "novice": 4, "intermediate": 4, "advanced": 6}.get(complexity, 4)
    return "\n".join(f"• {reps}x25 {unit} {d['name']} — {d['cue']}" for d in drills)


def build_main_set(primary_cat, complexity, phase, total_yardage, intensity, unit):
    main_yards = int(total_yardage * 0.55 / 25) * 25

    if complexity == "intro":
        return (
            f"{max(2, main_yards // 25)}x25 {unit} stroke practice — alternating swim/kick.\n"
            "Coach helps swimmers across; lots of streamline reminders and praise."
        )
    if complexity == "novice":
        if phase == "Early Season":
            return f"{max(2, main_yards // 50)}x50 {unit} (25 drill / 25 swim) — focus on technique under fatigue."
        if phase == "Final Week (Taper)":
            return f"{max(4, main_yards // 25)}x25 {unit} smooth, sharp — perfect technique, fast walls."
        return (
            f"{max(2, main_yards // 50)}x50 {unit} on a comfortable interval — 1 drill / 1 swim alternating.\n"
            f"Then {max(1, main_yards // 100)}x25 {unit} build — strong finishes."
        )
    if complexity == "intermediate":
        if phase == "Early Season":
            return (
                f"{max(2, main_yards // 100)}x100 {unit} — 25 drill / 50 swim / 25 build. Smooth and controlled.\n"
                f"{max(1, (main_yards % 100) // 50)}x50 {unit} kick with strong streamlines."
            )
        if phase == "Mid-Season":
            return (
                f"{max(4, main_yards // 50)}x50 {unit} descending 1–4. Last 50 = race pace.\n"
                f"Then {max(2, main_yards // 200)}x100 {unit} stroke focus — even splits."
            )
        if phase == "Late Season":
            return (
                f"{max(4, main_yards // 75)}x75 {unit} — 25 sprint / 50 cruise. Sharp walls.\n"
                f"{max(2, main_yards // 200)}x50 {unit} from a dive — race-pace breakouts."
            )
        return f"{max(4, main_yards // 50)}x25 {unit} sharp — perfect technique, fast turns. Race-ready feel."
    # advanced
    if phase == "Early Season":
        return (
            f"{max(2, main_yards // 200)}x200 {unit} — 50 drill / 100 swim / 50 build.\n"
            f"{max(4, main_yards // 200)}x50 {unit} kick — strong and steady."
        )
    if phase == "Mid-Season":
        return (
            f"{max(4, main_yards // 100)}x100 {unit} on a tight interval — descending 1–4.\n"
            f"{max(4, main_yards // 200)}x50 {unit} stroke @ race pace +5s."
        )
    if phase == "Late Season":
        return (
            f"{max(6, main_yards // 100)}x100 {unit} broken: 25 sprint / 25 EZ / 50 race pace.\n"
            f"{max(4, main_yards // 200)}x50 {unit} from a dive — sharp breakouts and finishes."
        )
    return f"{max(8, main_yards // 50)}x25 {unit} race-ready sprints from a dive. Quality over quantity."


def build_race_skill(phase, age_group, fun, goals):
    if phase == "Final Week (Taper)":
        return "Relays! 2–3 short fun relays focused on starts, exchanges, and finishes. Celebrate the season."
    if phase == "Late Season":
        return "Race start practice from blocks (or pool deck for younger). 4–6 starts with full streamline breakouts."
    if phase == "Mid-Season":
        if "Starts, Turns, and Finishes" in goals:
            return "Turn focus: 4x25 sprint into the wall, flip, streamline past flags. Coaches give feedback at each wall."
        return "Race skill: 2x25 fast from a dive (or push for 6 & Under). Focus on breakouts and finishes."
    if age_group in ("6 & Under", "7-8") or fun:
        return "Fun game: Sharks & Minnows, kick-board races, or follow-the-leader streamlines. Build excitement."
    return "Skill practice: 4x25 streamline push-offs to swim. Focus on tight streamline + 3 dolphin kicks."


def build_coach_cues(category, phase):
    base = {
        "freestyle": ["Head low, water at the hairline", "Reach long — fingertips first", "Steady kick — small and fast, not big and splashy"],
        "backstroke": ["Eyes up, head still — no looking around", "Pinky-first entry, thumb-first exit", "Hips at the surface, steady flutter"],
        "breaststroke": ["Heels to seat, feet flex out", "Pull–breathe–kick–glide rhythm", "Hold the streamline for 1–2 seconds every stroke"],
        "butterfly": ["Press the chest, hips follow", "Two kicks per pull — one on entry, one on exit", "Quick breath, head straight back down"],
        "turns_starts": ["Approach with speed — don't glide in", "Tuck tight, eyes to knees", "Tight streamline off every wall — count 3 before kicking"],
        "kick_streamline": ["Squeeze your ears with your biceps", "Toes pointed, kick from the hip", "Hips up, head down"],
    }
    cues = base.get(category, ["Streamline every wall", "Strong steady kick", "Reach long"])
    if phase == "Late Season":
        cues = cues + ["Race-day mindset — every wall counts"]
    return cues


def build_variations(yardage, is_combined):
    novice = f"Reduce volume to ~{int(yardage * 0.75 / 25) * 25} yards. Use kickboards as needed. Coach swims alongside for support."
    advanced = f"Add ~{int(yardage * 0.15 / 25) * 25} extra yards. Tighten intervals by 5–10s. Add 2x25 race-pace at the end."
    if is_combined:
        novice = ("**Younger group:** " + novice +
                  " Consider a dedicated lane with a coach for the youngest swimmers.")
        advanced = ("**Older group:** " + advanced +
                    " Put older swimmers on shorter intervals than the younger.")
    return novice, advanced


# =============================================================================
# SEASON GENERATION
# =============================================================================
def generate_season(profile: dict) -> list:
    practices = []
    start = profile["start_date"]
    weeks = profile["weeks"]
    practice_day_names = profile["practice_days"]
    schedule_blocks = [b for b in profile["schedule_blocks"] if b["enabled"]]
    primary_goals = profile["goals"]
    coach_notes = profile["coach_notes"]
    warmup_overrides = profile.get("warmups", {})
    pool_unit = profile["pool_unit"]

    schedule = []
    week_starts = [start + timedelta(days=7 * w) for w in range(weeks)]
    for week_idx, week_start in enumerate(week_starts):
        monday = week_start - timedelta(days=week_start.weekday())
        for i_in_week, day_name in enumerate(practice_day_names):
            day_offset = DAY_INDEX[day_name]
            practice_date = monday + timedelta(days=day_offset)
            if practice_date < start:
                continue
            schedule.append({
                "date": practice_date,
                "week_num": week_idx + 1,
                "practice_num_in_week": i_in_week,
                "day_name": day_name,
            })

    for sched in schedule:
        for block in schedule_blocks:
            primary_ag = primary_age_group(block)
            warmup = warmup_overrides.get(primary_ag)
            p = generate_practice(
                block=block,
                week_num=sched["week_num"],
                total_weeks=weeks,
                practice_date=sched["date"],
                practice_num_in_week=sched["practice_num_in_week"],
                primary_goals=primary_goals,
                coach_notes=coach_notes,
                custom_warmup=warmup,
                pool_unit=pool_unit,
            )
            p["day_name"] = sched["day_name"]
            practices.append(p)
    return practices


# =============================================================================
# SESSION STATE
# =============================================================================
def init_state():
    if "season_profile" not in st.session_state:
        st.session_state.season_profile = None
    if "practices" not in st.session_state:
        st.session_state.practices = []
    if "page" not in st.session_state:
        st.session_state.page = "Dashboard"
    if "selected_practice_id" not in st.session_state:
        st.session_state.selected_practice_id = None
    if "warmups" not in st.session_state:
        st.session_state.warmups = dict(DEFAULT_WARMUPS)
    if "schedule_blocks" not in st.session_state:
        st.session_state.schedule_blocks = default_schedule()
    if "setup_step" not in st.session_state:
        st.session_state.setup_step = "details"
    if "_setup_details" not in st.session_state:
        st.session_state._setup_details = {}

init_state()


# =============================================================================
# SIDEBAR NAV
# =============================================================================
with st.sidebar:
    st.markdown(f"### 🏊 Swimmingly")
    st.markdown("**Season Builder**")
    st.caption("Coach Dashboard")
    st.divider()

    pages = ["Dashboard", "Season Setup", "Season Calendar", "Print View"]
    if st.session_state.selected_practice_id:
        pages.insert(3, "Practice Detail")

    for p in pages:
        if st.button(p, use_container_width=True,
                     type="primary" if st.session_state.page == p else "secondary"):
            st.session_state.page = p
            st.rerun()

    st.divider()
    if st.session_state.season_profile:
        st.caption(f"**Team:** {st.session_state.season_profile['team_name']}")
        st.caption(f"**Practices:** {len(st.session_state.practices)}")
    else:
        st.caption("No season generated yet")


# =============================================================================
# PAGE: DASHBOARD
# =============================================================================
def page_dashboard():
    st.title("🏊 Welcome to Season Builder")
    st.markdown("Plan your full summer season in minutes. Generate age-appropriate practices, "
                "edit anything, and print coach-ready plans.")

    if not st.session_state.season_profile:
        st.info("👋 No season set up yet. Click **Create New Season** to get started.")
        if st.button("Create New Season", type="primary"):
            st.session_state.page = "Season Setup"
            st.rerun()

        st.divider()
        st.subheader("What you'll set up")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**🗓 Schedule**\n\nSeason length, practice days, and start date.")
        with c2:
            st.markdown("**⏰ Practice Times**\n\nExact start times and durations for each age group.")
        with c3:
            st.markdown("**🎯 Season Goals**\n\nFun, technique, racing, endurance — your call.")
        return

    profile = st.session_state.season_profile
    practices = st.session_state.practices

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='stat-card'><div class='stat-number'>{profile['weeks']}</div>"
                    f"<div class='stat-label'>Weeks</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='stat-card'><div class='stat-number'>{len(profile['practice_days'])}</div>"
                    f"<div class='stat-label'>Days / Week</div></div>", unsafe_allow_html=True)
    with c3:
        n_blocks = len([b for b in profile["schedule_blocks"] if b["enabled"]])
        st.markdown(f"<div class='stat-card'><div class='stat-number'>{n_blocks}</div>"
                    f"<div class='stat-label'>Practice Blocks</div></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='stat-card'><div class='stat-number'>{len(practices)}</div>"
                    f"<div class='stat-label'>Practices</div></div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("Season Summary")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Team:** {profile['team_name']}")
        st.markdown(f"**Season starts:** {profile['start_date'].strftime('%B %d, %Y')}")
        st.markdown(f"**Practice days:** {', '.join(profile['practice_days'])}")
        st.markdown(f"**Pool:** 25 {profile['pool_unit']}")
    with c2:
        st.markdown(f"**Primary goals:** {', '.join(profile['goals']) if profile['goals'] else '—'}")
        if profile["coach_notes"]:
            st.markdown(f"**Coach notes:** _{profile['coach_notes']}_")

    st.markdown("**Practice Schedule (every practice day):**")
    for b in profile["schedule_blocks"]:
        if not b["enabled"]:
            continue
        combined_tag = " 🔗" if len(b["age_groups"]) > 1 else ""
        st.markdown(
            f"<div class='sched-row'><strong>{b['label']}</strong>{combined_tag} · "
            f"{fmt_time(b['start_time'])} – {fmt_time(b['end_time'])} "
            f"<span style='color:#888'>({b['duration_min']} min)</span></div>",
            unsafe_allow_html=True,
        )

    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📅 View Season Calendar", type="primary", use_container_width=True):
            st.session_state.page = "Season Calendar"
            st.rerun()
    with c2:
        if st.button("⚙️ Edit Season Setup", use_container_width=True):
            st.session_state.page = "Season Setup"
            st.rerun()
    with c3:
        if st.button("🖨 Print View", use_container_width=True):
            st.session_state.page = "Print View"
            st.rerun()


# =============================================================================
# PAGE: SEASON SETUP — multi-step
# =============================================================================
def page_setup():
    st.title("⚙️ Season Setup")

    steps = [("details", "1. Details"), ("schedule", "2. Schedule"),
             ("warmups", "3. Warm-ups"), ("review", "4. Review")]
    cols = st.columns(len(steps))
    for i, (key, label) in enumerate(steps):
        with cols[i]:
            is_active = st.session_state.setup_step == key
            st.markdown(
                f"<div style='padding:8px; text-align:center; border-radius:6px; "
                f"background:{SWIMMINGLY_BLUE if is_active else '#f0f4f8'}; "
                f"color:{'white' if is_active else '#555'}; "
                f"font-weight:{'600' if is_active else '400'}'>{label}</div>",
                unsafe_allow_html=True,
            )
    st.divider()

    if st.session_state.setup_step == "details":
        page_setup_details()
    elif st.session_state.setup_step == "schedule":
        page_setup_schedule()
    elif st.session_state.setup_step == "warmups":
        page_setup_warmups()
    elif st.session_state.setup_step == "review":
        page_setup_review()


def page_setup_details():
    st.subheader("Season Details")
    st.caption("Tell us about your team and the basic season structure.")

    profile = st.session_state.season_profile or {}

    c1, c2 = st.columns(2)
    with c1:
        team_name = st.text_input("Team Name", value=profile.get("team_name", "Lakeside Dolphins"))
        start_date = st.date_input("Season Start Date",
                                    value=profile.get("start_date", date.today() + timedelta(days=14)))
        weeks = st.slider("Season Length (weeks)", min_value=5, max_value=10,
                          value=profile.get("weeks", 8))
        pool_unit = st.radio("Pool Length", ["yards", "meters"],
                             index=0 if profile.get("pool_unit", "yards") == "yards" else 1,
                             horizontal=True)
    with c2:
        practice_days = st.multiselect("Practice Days",
                                        options=PRACTICE_DAYS,
                                        default=profile.get("practice_days",
                                                            ["Monday", "Tuesday", "Wednesday", "Thursday"]))
        st.markdown("**Primary Season Goals** (pick up to 3)")
        existing_goals = profile.get("goals", ["Technique Development", "Fun & Retention"])
        selected_goals = []
        for goal in SEASON_GOALS:
            if st.checkbox(goal, value=goal in existing_goals, key=f"goal_{goal}"):
                selected_goals.append(goal)

    coach_notes = st.text_area("Optional Coach Notes / Focus Areas",
                                value=profile.get("coach_notes", ""),
                                placeholder="e.g. 'Lots of new swimmers this year — emphasize fundamentals and fun.'",
                                height=80)

    st.session_state._setup_details = {
        "team_name": team_name.strip(),
        "start_date": start_date,
        "weeks": weeks,
        "practice_days": practice_days,
        "goals": selected_goals[:3],
        "coach_notes": coach_notes.strip(),
        "pool_unit": pool_unit,
    }

    c1, c2 = st.columns([1, 1])
    with c2:
        if st.button("Next: Practice Schedule →", type="primary", use_container_width=True):
            if not team_name.strip():
                st.error("Please enter a team name.")
                return
            if not practice_days:
                st.error("Please select at least one practice day.")
                return
            st.session_state.setup_step = "schedule"
            st.rerun()


def stack_schedule(start_t: time):
    """Auto-fill enabled blocks consecutively from a start time, preserving each block's duration."""
    cursor = start_t
    for b in st.session_state.schedule_blocks:
        if b["enabled"]:
            dur = b["duration_min"] if b["duration_min"] > 0 else 60
            b["start_time"] = cursor
            b["end_time"] = add_minutes(cursor, dur)
            cursor = b["end_time"]


def page_setup_schedule():
    st.subheader("Practice Schedule")
    st.caption("Set start and end times for each age group. Same schedule applies every practice day.")

    # Template + utility row
    templates = load_templates()
    tc1, tc2 = st.columns([2, 1])
    with tc1:
        if templates:
            chosen = st.selectbox("Load a saved schedule template",
                                   ["— select —"] + list(templates.keys()),
                                   key="template_load_select")
            if chosen != "— select —" and st.button(f"📥 Load '{chosen}'"):
                st.session_state.schedule_blocks = templates[chosen]
                st.success(f"Loaded template: {chosen}")
                st.rerun()
        else:
            st.caption("_No saved templates yet — save one below after building your schedule._")
    with tc2:
        if st.button("🔁 Reset to defaults", use_container_width=True):
            st.session_state.schedule_blocks = default_schedule()
            st.rerun()

    st.divider()

    blocks = st.session_state.schedule_blocks

    # Header row
    h1, h2, h3, h4, h5, h6 = st.columns([0.4, 2.6, 1.3, 1.3, 1, 0.4])
    h1.markdown("**On**")
    h2.markdown("**Age Group(s)**")
    h3.markdown("**Start**")
    h4.markdown("**End**")
    h5.markdown("**Duration**")
    h6.markdown("**ㅤ**")

    # Render each schedule block
    for idx, block in enumerate(blocks):
        c1, c2, c3, c4, c5, c6 = st.columns([0.4, 2.6, 1.3, 1.3, 1, 0.4])

        with c1:
            blocks[idx]["enabled"] = st.checkbox(
                " ", value=block["enabled"], key=f"sch_en_{idx}", label_visibility="collapsed"
            )

        with c2:
            new_ags = st.multiselect(
                "Age groups",
                options=list(AGE_GROUPS.keys()),
                default=block["age_groups"],
                key=f"sch_ag_{idx}",
                label_visibility="collapsed",
            )
            if not new_ags:
                new_ags = block["age_groups"]  # disallow empty
            blocks[idx]["age_groups"] = new_ags
            blocks[idx]["label"] = " & ".join(new_ags)

        with c3:
            current_start = nearest_time_option(block["start_time"])
            try:
                start_idx = TIME_OPTIONS.index(current_start)
            except ValueError:
                start_idx = TIME_OPTIONS.index(time(16, 0))
            blocks[idx]["start_time"] = st.selectbox(
                "Start",
                TIME_OPTIONS,
                index=start_idx,
                format_func=lambda t: TIME_OPTION_LABELS[t],
                key=f"sch_start_{idx}",
                label_visibility="collapsed",
            )

        with c4:
            current_end = nearest_time_option(block["end_time"])
            try:
                end_idx = TIME_OPTIONS.index(current_end)
            except ValueError:
                end_idx = TIME_OPTIONS.index(time(17, 0))
            blocks[idx]["end_time"] = st.selectbox(
                "End",
                TIME_OPTIONS,
                index=end_idx,
                format_func=lambda t: TIME_OPTION_LABELS[t],
                key=f"sch_end_{idx}",
                label_visibility="collapsed",
            )

        with c5:
            dur = minutes_between(blocks[idx]["start_time"], blocks[idx]["end_time"])
            blocks[idx]["duration_min"] = dur
            color = "#444" if dur > 0 else "#e74c3c"
            st.markdown(
                f"<div style='padding-top:6px; color:{color}; font-size:14px;'>"
                f"<strong>{dur} min</strong></div>",
                unsafe_allow_html=True,
            )

        with c6:
            if st.button("🗑", key=f"sch_del_{idx}", help="Remove this block"):
                blocks.pop(idx)
                st.rerun()

        # Per-row notices
        notices = []
        if len(blocks[idx]["age_groups"]) > 1:
            notices.append(f"🔗 Combined: **{' & '.join(blocks[idx]['age_groups'])}** swim together.")
        if dur <= 0:
            notices.append("⚠️ End time must be after start time.")
        for j, other in enumerate(blocks):
            if j >= idx or not other["enabled"] or not blocks[idx]["enabled"]:
                continue
            if (blocks[idx]["start_time"] < other["end_time"]
                    and other["start_time"] < blocks[idx]["end_time"]):
                notices.append(f"⚠️ Overlaps with **{other['label']}** "
                               f"({fmt_time(other['start_time'])}–{fmt_time(other['end_time'])}).")
        for n in notices:
            st.markdown(f"<small style='color:#666; margin-left:50px'>{n}</small>",
                        unsafe_allow_html=True)

    st.session_state.schedule_blocks = blocks

    # Add new block
    if st.button("➕ Add a custom practice block"):
        last_end = blocks[-1]["end_time"] if blocks else time(16, 0)
        new_block = {
            "id": f"custom_{int(datetime.now().timestamp() * 1000)}",
            "age_groups": ["11-12"],
            "label": "11-12",
            "start_time": last_end,
            "end_time": add_minutes(last_end, 60),
            "duration_min": 60,
            "enabled": True,
        }
        st.session_state.schedule_blocks.append(new_block)
        st.rerun()

    # Timeline preview
    st.divider()
    st.markdown("**Schedule Preview · One Practice Day**")
    render_timeline_preview([b for b in blocks if b["enabled"]])

    # Save template
    st.divider()
    with st.expander("💾 Save / manage schedule templates"):
        col_save, col_del = st.columns(2)
        with col_save:
            tn = st.text_input("Template name", placeholder="e.g. 'Standard Summer 2026'",
                                key="template_save_name")
            if st.button("Save as Template", use_container_width=True):
                if tn.strip():
                    if save_template(tn.strip(), st.session_state.schedule_blocks):
                        st.success(f"Saved template: {tn.strip()}")
                        st.rerun()
                else:
                    st.error("Please enter a template name.")
        with col_del:
            if templates:
                to_delete = st.selectbox("Delete a template",
                                          ["— select —"] + list(templates.keys()),
                                          key="template_delete_select")
                if to_delete != "— select —" and st.button(f"Delete '{to_delete}'",
                                                            use_container_width=True):
                    delete_template(to_delete)
                    st.success(f"Deleted: {to_delete}")
                    st.rerun()
            else:
                st.caption("_No templates saved yet._")

    # Nav
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Back to Details", use_container_width=True):
            st.session_state.setup_step = "details"
            st.rerun()
    with c2:
        enabled_blocks = [b for b in blocks if b["enabled"]]
        any_invalid = any(b["duration_min"] <= 0 for b in enabled_blocks)
        if not enabled_blocks:
            st.warning("Enable at least one practice block to continue.")
        elif any_invalid:
            st.warning("Fix any blocks where end time is before start time.")
        else:
            if st.button("Next: Warm-ups →", type="primary", use_container_width=True):
                st.session_state.setup_step = "warmups"
                st.rerun()


def render_timeline_preview(blocks):
    if not blocks:
        st.info("No enabled blocks to preview.")
        return

    earliest = min(b["start_time"] for b in blocks)
    latest = max(b["end_time"] for b in blocks)
    total_mins = minutes_between(earliest, latest)
    if total_mins <= 0:
        st.warning("Invalid schedule — check start/end times.")
        return

    palette = [
        ("#E6F1FB", "#1AA7EC", "#0C447C"),
        ("#EEEDFE", "#7F77DD", "#3C3489"),
        ("#E1F5EE", "#1D9E75", "#085041"),
        ("#FAEEDA", "#BA7517", "#633806"),
        ("#FBEAF0", "#D4537E", "#72243E"),
        ("#FAECE7", "#D85A30", "#712B13"),
    ]

    # Hour tick labels
    h_earliest = earliest.hour
    h_latest = latest.hour + (1 if latest.minute > 0 else 0)
    ticks = []
    for h in range(h_earliest, h_latest + 1):
        tick_t = time(h % 24, 0)
        if tick_t < earliest:
            continue
        offset_min = minutes_between(earliest, tick_t)
        pct = (offset_min / total_mins) * 100
        if 0 <= pct <= 100:
            label = f"{(h % 12) or 12}:00"
            ticks.append((pct, label))

    tick_html = "".join(
        f"<div style='position:absolute; left:{pct:.1f}%; font-size:11px; color:#888; transform:translateX(-50%)'>{label}</div>"
        for pct, label in ticks
    )

    rows_html = ""
    for i, b in enumerate(blocks):
        bg, border, txt = palette[i % len(palette)]
        offset = minutes_between(earliest, b["start_time"])
        left_pct = (offset / total_mins) * 100
        width_pct = (b["duration_min"] / total_mins) * 100
        combined_tag = " 🔗" if len(b["age_groups"]) > 1 else ""
        rows_html += (
            f"<div style='position:relative; height:30px; margin-bottom:4px'>"
            f"<div style='position:absolute; left:{left_pct:.2f}%; width:{width_pct:.2f}%; height:26px; "
            f"background:{bg}; border-left:3px solid {border}; border-radius:0 4px 4px 0; "
            f"padding:4px 8px; font-size:12px; color:{txt}; font-weight:500; "
            f"white-space:nowrap; overflow:hidden; box-sizing:border-box;'>"
            f"{b['label']}{combined_tag} · {b['duration_min']}min</div>"
            f"</div>"
        )

    total_deck = sum(b["duration_min"] for b in blocks)
    hours = total_deck // 60
    mins = total_deck % 60
    total_str = f"{hours}h {mins}min" if hours else f"{mins} min"

    st.markdown(
        f"""
        <div style='background:white; border:1px solid #e1ecf7; border-radius:8px; padding:14px;'>
          <div style='position:relative; height:18px; border-bottom:1px solid #eee; margin-bottom:8px;'>{tick_html}</div>
          {rows_html}
          <div style='margin-top:10px; padding-top:10px; border-top:1px solid #eee; font-size:12px; color:#888;'>
            Total deck time per day: <strong style='color:#222'>{total_str}</strong>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_setup_warmups():
    st.subheader("Default Warm-ups")
    st.caption("These warm-ups are used for each age group across the season. Edit any you want to customize.")

    for ag in AGE_GROUPS:
        st.session_state.warmups[ag] = st.text_area(
            f"{ag}",
            value=st.session_state.warmups.get(ag, DEFAULT_WARMUPS[ag]),
            key=f"wu_{ag}",
            height=70,
        )

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Back to Schedule", use_container_width=True):
            st.session_state.setup_step = "schedule"
            st.rerun()
    with c2:
        if st.button("Next: Review & Generate →", type="primary", use_container_width=True):
            st.session_state.setup_step = "review"
            st.rerun()


def page_setup_review():
    st.subheader("Review & Generate Season")

    d = st.session_state._setup_details
    blocks = [b for b in st.session_state.schedule_blocks if b["enabled"]]

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Team:** {d['team_name']}")
        st.markdown(f"**Season starts:** {d['start_date'].strftime('%B %d, %Y')}")
        st.markdown(f"**Length:** {d['weeks']} weeks")
        st.markdown(f"**Practice days:** {', '.join(d['practice_days'])}")
        st.markdown(f"**Pool:** 25 {d['pool_unit']}")
    with c2:
        st.markdown(f"**Goals:** {', '.join(d['goals']) if d['goals'] else '—'}")
        if d['coach_notes']:
            st.markdown(f"**Notes:** _{d['coach_notes']}_")
        n_practices = d['weeks'] * len(d['practice_days']) * len(blocks)
        st.markdown(f"**Total practices to generate:** {n_practices}")

    st.markdown("**Practice schedule (each day):**")
    for b in blocks:
        combined = " 🔗" if len(b["age_groups"]) > 1 else ""
        st.markdown(f"- **{b['label']}**{combined}: {fmt_time(b['start_time'])} – {fmt_time(b['end_time'])} ({b['duration_min']} min)")

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Back to Warm-ups", use_container_width=True):
            st.session_state.setup_step = "warmups"
            st.rerun()
    with c2:
        if st.button("🏊 Generate Full Season", type="primary", use_container_width=True):
            profile = {
                **d,
                "schedule_blocks": [dict(b) for b in st.session_state.schedule_blocks],
                "warmups": dict(st.session_state.warmups),
            }
            st.session_state.season_profile = profile
            with st.spinner("Building your season..."):
                random.seed(hash(d['team_name']) % (2**32))
                st.session_state.practices = generate_season(profile)
            st.success(f"✅ Generated {len(st.session_state.practices)} practices!")
            st.session_state.page = "Season Calendar"
            st.session_state.setup_step = "details"
            st.rerun()


# =============================================================================
# PAGE: SEASON CALENDAR
# =============================================================================
def page_calendar():
    st.title("📅 Season Calendar")

    if not st.session_state.practices:
        st.warning("No practices generated yet. Go to **Season Setup** to build your season.")
        return

    profile = st.session_state.season_profile
    practices = st.session_state.practices
    block_options = ["All Practices"] + [b["label"] for b in profile["schedule_blocks"] if b["enabled"]]

    c1, c2 = st.columns([2, 1])
    with c1:
        block_filter = st.selectbox("Filter by Practice Block", block_options)
    with c2:
        view_mode = st.radio("View", ["By Week", "Table"], horizontal=True)

    filtered = practices
    if block_filter != "All Practices":
        filtered = [p for p in practices if p["block_label"] == block_filter]

    if view_mode == "Table":
        df = pd.DataFrame([{
            "Date": p["date"].strftime("%a %b %d"),
            "Time": f"{fmt_time(p['start_time'])} – {fmt_time(p['end_time'])}",
            "Week": p["week_num"],
            "Block": p["block_label"],
            "Theme": p["theme"],
            "Duration": f"{p['duration']} min",
            "Yardage": f"{p['estimated_yardage']} {p['pool_unit']}",
            "Phase": p["phase"],
        } for p in filtered])
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption("💡 Switch to **By Week** view to click into any practice.")
        return

    weeks = sorted(set(p["week_num"] for p in filtered))
    for week in weeks:
        wp = [p for p in filtered if p["week_num"] == week]
        if not wp:
            continue
        phase = wp[0]["phase"]
        st.markdown(f"<div class='week-header'>Week {week} — {phase}</div>", unsafe_allow_html=True)

        dates = sorted(set(p["date"] for p in wp))
        for d in dates:
            day_practices = [p for p in wp if p["date"] == d]
            day_practices.sort(key=lambda x: x["start_time"])
            st.markdown(f"**{d.strftime('%A, %B %d')}**")
            cols = st.columns(min(3, len(day_practices)))
            for i, p in enumerate(day_practices):
                with cols[i % len(cols)]:
                    combined_tag = " 🔗" if p["is_combined"] else ""
                    st.markdown(
                        f"<div class='practice-card'>"
                        f"<strong>{p['block_label']}</strong>{combined_tag}<br>"
                        f"<span style='color:#666; font-size:12px'>{fmt_time(p['start_time'])} – {fmt_time(p['end_time'])} · {p['duration']} min</span><br>"
                        f"<span style='color:#444'>{p['theme']}</span><br>"
                        f"<small>{p['estimated_yardage']} {p['pool_unit']}</small>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                    if st.button("View Practice →", key=f"view_{p['id']}", use_container_width=True):
                        st.session_state.selected_practice_id = p["id"]
                        st.session_state.page = "Practice Detail"
                        st.rerun()


# =============================================================================
# PAGE: PRACTICE DETAIL
# =============================================================================
def find_practice(pid):
    for i, p in enumerate(st.session_state.practices):
        if p["id"] == pid:
            return i, p
    return None, None


def regenerate(pid, mod="balanced"):
    idx, p = find_practice(pid)
    if p is None:
        return
    profile = st.session_state.season_profile
    block = next((b for b in profile["schedule_blocks"] if b["id"] == p["block_id"]), None)
    if not block:
        return
    new_p = generate_practice(
        block=block,
        week_num=p["week_num"],
        total_weeks=profile["weeks"],
        practice_date=p["date"],
        practice_num_in_week=random.randint(0, 5),
        primary_goals=profile["goals"],
        coach_notes=profile["coach_notes"],
        custom_warmup=profile["warmups"].get(primary_age_group(block)),
        intensity_mod=mod,
        pool_unit=profile["pool_unit"],
    )
    new_p["id"] = p["id"]
    new_p["day_name"] = p.get("day_name", "")
    new_p["edited_notes"] = p.get("edited_notes", "")
    st.session_state.practices[idx] = new_p


def page_practice_detail():
    pid = st.session_state.selected_practice_id
    idx, p = find_practice(pid)
    if not p:
        st.warning("No practice selected.")
        return

    c1, c2 = st.columns([3, 1])
    with c1:
        st.title(p["title"])
        combined_tag = " 🔗" if p["is_combined"] else ""
        st.markdown(
            f"**{p['date'].strftime('%A, %B %d, %Y')}** · "
            f"{fmt_time(p['start_time'])} – {fmt_time(p['end_time'])} · "
            f"**{p['block_label']}**{combined_tag} · "
            f"{p['duration']} min · "
            f"~{p['estimated_yardage']} {p['pool_unit']} · "
            f"_{p['phase']}_"
        )
        if p["is_combined"]:
            st.info(f"🔗 **Combined practice:** {' & '.join(p['age_groups'])} swim together. "
                    f"Yardage and complexity targeted to **{p['primary_age_group']}** — see lane-split variations below.")
    with c2:
        if st.button("← Back to Calendar"):
            st.session_state.page = "Season Calendar"
            st.rerun()

    st.divider()

    st.subheader("Practice Plan")
    total_check = sum(b["minutes"] for b in p["blocks"])
    for block in p["blocks"]:
        st.markdown(
            f"<div class='block-box'>"
            f"<strong>{block['name']}</strong> "
            f"<span style='color:#888;font-size:13px'>· {block['minutes']} min</span><br>"
            f"<div style='margin-top:6px;white-space:pre-line'>{block['content']}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    st.caption(f"Total time: {total_check} min (target: {p['duration']} min)")

    if p.get("fun_finisher"):
        st.success(f"🎉 **Fun Finisher (optional):** {p['fun_finisher']}")

    st.subheader("Coach Cues")
    for cue in p["coach_cues"]:
        st.markdown(f"- {cue}")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Novice Variation**")
        st.info(p["novice_variation"])
    with c2:
        st.markdown("**Advanced Variation**")
        st.info(p["advanced_variation"])

    st.divider()
    st.subheader("Coach Notes")
    new_notes = st.text_area("Edit notes for this practice",
                              value=p.get("edited_notes", ""),
                              placeholder="e.g. 'Watch for Sara's flip turn timing.'",
                              key=f"notes_{pid}",
                              height=80)
    if new_notes != p.get("edited_notes", ""):
        st.session_state.practices[idx]["edited_notes"] = new_notes

    st.divider()
    st.subheader("Regenerate This Practice")
    c1, c2, c3, c4, c5 = st.columns(5)
    if c1.button("🔄 Regenerate", use_container_width=True):
        regenerate(pid, "balanced"); st.rerun()
    if c2.button("🎉 More Fun", use_container_width=True):
        regenerate(pid, "fun"); st.rerun()
    if c3.button("🎯 More Technique", use_container_width=True):
        regenerate(pid, "technique"); st.rerun()
    if c4.button("💪 Make Harder", use_container_width=True):
        regenerate(pid, "harder"); st.rerun()
    if c5.button("🌊 Make Easier", use_container_width=True):
        regenerate(pid, "easier"); st.rerun()


# =============================================================================
# PAGE: PRINT VIEW
# =============================================================================
def page_print():
    st.title("🖨 Print-Friendly View")

    if not st.session_state.practices:
        st.warning("No practices generated yet.")
        return

    profile = st.session_state.season_profile
    practices = st.session_state.practices
    block_options = ["All Blocks"] + [b["label"] for b in profile["schedule_blocks"] if b["enabled"]]

    c1, c2 = st.columns(2)
    with c1:
        block_filter = st.selectbox("Practice Block", block_options)
    with c2:
        week_filter = st.selectbox("Week", ["All Weeks"] + [f"Week {w}" for w in range(1, profile["weeks"] + 1)])

    filtered = practices
    if block_filter != "All Blocks":
        filtered = [p for p in filtered if p["block_label"] == block_filter]
    if week_filter != "All Weeks":
        wn = int(week_filter.replace("Week ", ""))
        filtered = [p for p in filtered if p["week_num"] == wn]

    st.caption(f"Showing {len(filtered)} practices. Use your browser's print (Cmd/Ctrl+P) to print or save as PDF.")
    st.divider()

    for p in filtered:
        st.markdown(f"### {p['title']}")
        combined_tag = " (combined)" if p["is_combined"] else ""
        st.markdown(f"**{p['date'].strftime('%A, %B %d, %Y')}** · "
                    f"{fmt_time(p['start_time'])} – {fmt_time(p['end_time'])} · "
                    f"{p['block_label']}{combined_tag} · {p['duration']} min · "
                    f"~{p['estimated_yardage']} {p['pool_unit']} · {p['phase']}")
        for block in p["blocks"]:
            st.markdown(f"**{block['name']}** ({block['minutes']} min)")
            st.markdown(block["content"].replace("\n", "  \n"))
        if p.get("fun_finisher"):
            st.markdown(f"**Fun Finisher:** {p['fun_finisher']}")
        st.markdown("**Coach Cues:** " + " · ".join(p["coach_cues"]))
        if p.get("edited_notes"):
            st.markdown(f"**Notes:** _{p['edited_notes']}_")
        st.markdown("---")


# =============================================================================
# ROUTER
# =============================================================================
PAGES = {
    "Dashboard": page_dashboard,
    "Season Setup": page_setup,
    "Season Calendar": page_calendar,
    "Practice Detail": page_practice_detail,
    "Print View": page_print,
}

PAGES[st.session_state.page]()
