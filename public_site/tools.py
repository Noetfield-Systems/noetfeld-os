"""Public operator tools served from noetfeld-os."""

from __future__ import annotations

from dataclasses import dataclass

PUBLIC_ORIGIN = "https://api.noetfield.com"


@dataclass(frozen=True)
class ToolPage:
    slug: str
    title: str
    description: str
    kicker: str
    hero_headline: str
    hero_subheadline: str
    form_html: str = ""
    presets: tuple[tuple[str, str], ...] = ()
    math_line: str = ""
    notes: tuple[tuple[str, str], ...] = ()
    kind: str = "calc"
    hide_amount: bool = False


HUB = ToolPage(
    slug="hub",
    title="Free operator tools // Noetfield OS",
    description="One-minute checks that will tell you to leave a process alone. No signup. Nothing stored.",
    kicker="Free · no signup · nothing stored",
    hero_headline="Most operators can name the process that annoys them. Almost none can name what it costs.",
    hero_subheadline="Five one-minute checks. Conservative math. An honest leave-it-alone line. If the number is a hobby, the page says so instead of selling you a fix.",
    kind="hub",
)

PAGES: dict[str, ToolPage] = {
    "quiet-leak": ToolPage(
        slug="quiet-leak",
        title="Quiet leak // What is this process costing you?",
        description="Four inputs. Rate times 1.3 times 48 weeks. Under $3,000 a year, leave it alone.",
        kicker="Same math as the operator post",
        hero_headline="What is this process costing you?",
        hero_subheadline="Pick the quiet one. Double entry. Status copied into a tracker. A draft rewritten after the model said it was done.",
        presets=(
            ('{"touches":10,"minutes":8,"rate":45,"people":3}', "Double data entry"),
            ('{"touches":6,"minutes":15,"rate":40,"people":2}', "Invoice chase"),
            ('{"touches":12,"minutes":5,"rate":38,"people":4}', "CRM copy-paste"),
        ),
        form_html="""
       <label>Times a week someone touches it
        <input type="number" name="touches" min="0" step="0.5" value="8" inputmode="decimal" required />
       </label>
       <label>Minutes per touch
        <span class="hint">Include the context switch.</span>
        <input type="number" name="minutes" min="0" step="0.5" value="12" inputmode="decimal" required />
       </label>
       <label>Hourly rate before overhead (CAD)
        <input type="number" name="rate" min="0" step="1" value="45" inputmode="decimal" required />
       </label>
       <label>How many people do this
        <input type="number" name="people" min="0" step="1" value="3" inputmode="decimal" required />
       </label>
        """,
        math_line="Annual cost = touches × (minutes ÷ 60) × rate × 1.3 × people × 48. Under $3,000, leave it alone.",
        notes=(
            (
                "People undercount touches by about half",
                "Count one real day before you estimate. The number you type from memory is usually the complaint, not the work.",
            ),
            (
                "The expensive leaks are the quiet ones",
                "Nobody files a ticket for the copy between two systems. Everyone accepted it years ago. That is why it survives.",
            ),
        ),
    ),
    "ai-spend": ToolPage(
        slug="ai-spend",
        title="AI spend // Invoice versus workflow",
        description="What share of the AI invoice maps to a named workflow and a named accepter.",
        kicker="Invoice versus workflow",
        hero_headline="Most teams can name the AI invoice. Almost none can name which workflow created it.",
        hero_subheadline="If spend is small and one team owns it, a spreadsheet is enough. If several teams are in it and you cannot attribute 20% of the bill, the leak is explanation, not tokens.",
        presets=(
            ('{"monthly":800,"attributed":80,"teams":1,"named":"yes"}', "One team, small bill"),
            ('{"monthly":12000,"attributed":10,"teams":6,"named":"no"}', "Several teams, unexplained"),
        ),
        form_html="""
       <label>Monthly AI / Copilot spend (CAD)
        <input type="number" name="monthly" min="0" step="50" value="4000" inputmode="decimal" required />
       </label>
       <label>Share you can attribute to a named workflow (%)
        <input type="number" name="attributed" min="0" max="100" step="1" value="15" inputmode="decimal" required />
       </label>
       <label>Teams using it
        <input type="number" name="teams" min="1" step="1" value="3" inputmode="decimal" required />
       </label>
       <label>Does a named person accept the output before it leaves?
        <select name="named" required>
         <option value="no" selected>No</option>
         <option value="yes">Yes</option>
        </select>
       </label>
        """,
        math_line="Unattributed annual = monthly × (1 − attributed share) × 12. Leave it alone under $1,500 a month with one team.",
        notes=(
            (
                "Licensed Copilot is not the whole bill",
                "People count seats and forget personal ChatGPT. That unofficial line is often larger, and it never shows up in the invoice meeting.",
            ),
            (
                "The draft that shipped with no name on it",
                "Nobody files a ticket for that. So it survives. That is the expensive leak.",
            ),
        ),
    ),
    "who-accepted": ToolPage(
        slug="who-accepted",
        title="Who accepted // Chat log versus process",
        description="If you cannot name who accepted the last AI output, you have a chat log, not a process.",
        kicker="Chat log versus process",
        hero_headline="If you cannot name who accepted the last AI output, you do not have a process.",
        hero_subheadline="A process has a named person, a pass/fail check, and a reason you can open later. The page will tell you to stop shopping if you already have that.",
        presets=(
            ('{"deliverables":8,"signed":95,"minutes":5,"rate":55,"replay":"yes"}', "Already signed"),
            ('{"deliverables":30,"signed":10,"minutes":25,"rate":65,"replay":"no"}', "Chat drafts, heavy rewrite"),
        ),
        form_html="""
       <label>AI-assisted deliverables per week
        <input type="number" name="deliverables" min="0" step="1" value="20" inputmode="decimal" required />
       </label>
       <label>Share a named person signs (%)
        <input type="number" name="signed" min="0" max="100" step="1" value="25" inputmode="decimal" required />
       </label>
       <label>Minutes of redo on an unsigned item
        <input type="number" name="minutes" min="0" step="1" value="18" inputmode="decimal" required />
       </label>
       <label>Hourly rate before overhead (CAD)
        <input type="number" name="rate" min="0" step="1" value="55" inputmode="decimal" required />
       </label>
       <label>Can you replay why the last one passed?
        <select name="replay" required>
         <option value="no" selected>No</option>
         <option value="yes">Yes</option>
        </select>
       </label>
        """,
        math_line="Unsigned volume × redo minutes × loaded rate × 48 weeks. Leave it alone at 90% signed with a replayable why.",
        notes=(
            (
                "The builder must not grade itself",
                "If the same person or model that produced the draft also marks it done, you do not have a check. You have a hope.",
            ),
            (
                "Redo is the bill you already pay",
                "Minutes spent rewriting finished drafts is the real cost. The tool prices that, not a fantasy saving.",
            ),
        ),
    ),
    "copilot-seats": ToolPage(
        slug="copilot-seats",
        title="Copilot seats // Two numbers, not one",
        description="Unused licenses and ungoverned use, counted separately on purpose.",
        kicker="Two numbers, not one",
        hero_headline="You are paying for seats. You are not paying for a decision trail.",
        hero_subheadline="Unused licenses are an adoption problem. Ungoverned use is an explanation problem. Showing only one of those numbers is how a page stays dishonest.",
        presets=(
            ('{"licensed":12,"used":11,"hours":2,"rate":45,"seat":360}', "Small team, used"),
            ('{"licensed":200,"used":40,"hours":6,"rate":70,"seat":360}', "Wide rollout, thin use"),
        ),
        form_html="""
       <label>Licensed seats
        <input type="number" name="licensed" min="0" step="1" value="80" inputmode="decimal" required />
       </label>
       <label>Seats used last week
        <input type="number" name="used" min="0" step="1" value="35" inputmode="decimal" required />
       </label>
       <label>Hours per used seat per week
        <input type="number" name="hours" min="0" step="0.5" value="4" inputmode="decimal" required />
       </label>
       <label>Hourly rate before overhead (CAD)
        <input type="number" name="rate" min="0" step="1" value="55" inputmode="decimal" required />
       </label>
       <label>Annual cost per seat (CAD)
        <span class="hint">Default 360 for Copilot-class licensing. Change it if you know the real number.</span>
        <input type="number" name="seat" min="0" step="10" value="360" inputmode="decimal" required />
       </label>
        """,
        math_line="Unused waste = unused seats × annual seat cost. Ungoverned use = used seats × hours × loaded rate × 48 weeks.",
        notes=(
            (
                "Unused seats under about 10",
                "That is adoption. Do not buy a control plane to fix a habit. Ask why people are not in the tool.",
            ),
            (
                "Used seats with no named accepter",
                "That is the expensive line. Hours are being spent and nobody can replay why an output left the building.",
            ),
        ),
    ),
    "board-five": ToolPage(
        slug="board-five",
        title="Board five // Yes or no only",
        description="Five yes or no questions. Score 0 or 1: do not buy. The tool will say that out loud.",
        kicker="Yes or no only",
        hero_headline="The board questions you either can answer or you cannot.",
        hero_subheadline="No scores dressed up as science. Check what you can actually name today. The page will tell you not to buy.",
        presets=(("{}", "Clear all"),),
        form_html="""
       <div class="tools-checks">
        <label><input type="checkbox" name="workflow" /> Can you name the workflow?</label>
        <label><input type="checkbox" name="owner" /> Can you name the owner?</label>
        <label><input type="checkbox" name="spend" /> Can you name last month’s spend for it?</label>
        <label><input type="checkbox" name="failed" /> Can you name the last time it failed?</label>
        <label><input type="checkbox" name="accepted" /> Can you name who accepted the last output?</label>
       </div>
        """,
        math_line="Score is a count of yes answers. 0 to 1 leave it. 2 to 3 Copilot Readiness if procurement needs a file. 4 to 5 Trust Brief only if you need the memo.",
        notes=(
            (
                "0 or 1: do not buy",
                "Name one workflow and who accepts its output. Then come back. A diagnostic sold into a blank page is theatre.",
            ),
            (
                "4 or 5: a memo can be defended",
                "Trust Brief is a six-week policy map, not a product tour. Use it when the board needs that memo, not before.",
            ),
        ),
        hide_amount=True,
    ),
    "embed": ToolPage(
        slug="embed",
        title="Embed these tools // Advisors",
        description="One iframe. No signup. We do not set cookies on your visitors and we do not store their numbers.",
        kicker="Advisors · free",
        hero_headline="Put the check on your own page.",
        hero_subheadline="One iframe. No signup. We do not set cookies on your visitors and we do not store their numbers. Keep the Noetfield link under the frame so people can open the full page.",
        kind="embed",
    ),
}

CARDS: tuple[tuple[str, str, str, str], ...] = (
    ("quiet-leak", "01", "Quiet leak", "Price one manual process. Honest hobby line at $3,000 a year."),
    ("ai-spend", "02", "AI spend you cannot explain", "What share of the invoice maps to a named workflow."),
    ("who-accepted", "03", "Who accepted this", "Chat log versus a named person and a replayable why."),
    ("copilot-seats", "04", "Copilot seats", "Unused licenses and ungoverned use, shown as two numbers."),
    ("board-five", "05", "Five board questions", "Yes or no. The tool will tell you not to buy."),
    ("embed", "06", "Embed for advisors", "One iframe. No tracking of your visitors."),
)

EMBED_BLOCKS: tuple[tuple[str, str], ...] = (
    ("quiet-leak", "Quiet leak"),
    ("ai-spend", "AI spend"),
    ("who-accepted", "Who accepted"),
    ("copilot-seats", "Copilot seats"),
    ("board-five", "Five board questions"),
)


def canonical(slug: str) -> str:
    if slug in ("", "hub"):
        return f"{PUBLIC_ORIGIN}/tools/"
    return f"{PUBLIC_ORIGIN}/tools/{slug}/"


def get_page(slug: str | None) -> ToolPage | None:
    if slug in (None, "", "hub"):
        return HUB
    return PAGES.get(slug or "")


__all__ = [
    "CARDS",
    "EMBED_BLOCKS",
    "HUB",
    "PAGES",
    "PUBLIC_ORIGIN",
    "ToolPage",
    "canonical",
    "get_page",
]
