"""
BurnBook Roaster - The AI-powered savage.
Turns dry analysis into devastating commentary.
"""

import json
import os
from typing import Dict, Any, Optional
import urllib.request
import urllib.error


SEVERITY_PROMPTS = {
    "gentle": "Be constructive and encouraging, but honest. Like a kind mentor.",
    "medium": "Be direct and sarcastic. Call out real issues with wit.",
    "brutal": "Be savage. Pull no punches. Roast the code like a comedy roast. Be hilarious but educational.",
    "nuclear": (
        "MAXIMUM DESTRUCTION MODE. Roast this code like Gordon Ramsay reviewing roadkill. "
        "Be absolutely merciless, drop pop culture references, memes, and comparisons to famous coding disasters. "
        "Make it funny but ensure every joke teaches something real. No mercy."
    ),
}

SYSTEM_PROMPT = """You are BurnBook, the world's most savage code reviewer. 
You analyze code quality results and deliver brutal but educational roasts.
You're like a comedy roast, but for code. Every joke should land AND teach something.
You reference coding disasters (like the Mars Orbiter bug, the Therac-25, etc.), 
memes (has anyone really been far even as decided to use even go want), 
and real-world consequences of bad code.
Be specific about the actual issues found. Don't make things up.
Keep roasts punchy — 3-5 sentences per section.
Use emojis sparingly but effectively.
Always end with ONE actionable improvement suggestion.
"""


class Roaster:
    """
    The AI roast master. Transforms cold, boring analysis into
    scorching hot commentary that will make developers question
    their career choices (but then actually fix their code).
    """

    def __init__(self, api_key: str, severity: str = "brutal", model: Optional[str] = None):
        self.api_key = api_key
        self.severity = severity
        self.model = model or os.environ.get(
            "BURNBOOK_MODEL", "openai/gpt-4o-mini"
        )
        # Detect if using OpenRouter vs OpenAI directly
        self.base_url = (
            "https://openrouter.ai/api/v1"
            if os.environ.get("OPENROUTER_API_KEY")
            else "https://api.openai.com/v1"
        )
        if self.base_url == "https://api.openai.com/v1":
            self.model = model or "gpt-4o-mini"

    def roast(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Add AI roasting commentary to analysis results."""
        try:
            commentary = self._generate_roast(results)
            results["ai_roast"] = commentary
        except Exception as e:
            results["ai_roast"] = {
                "error": str(e),
                "overall": "The AI roaster itself crashed. Even the roaster is ashamed of your code.",
                "sections": [],
            }
        return results

    def _generate_roast(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate roasting commentary via AI API."""
        score = results.get("score", 0)
        metrics = results.get("metrics", {})
        issues = results.get("issues", [])
        language = results.get("language", "unknown")
        category_scores = results.get("category_scores", {})

        # Build context for AI
        top_issues = self._summarize_top_issues(issues)
        worst_categories = sorted(
            category_scores.items(), key=lambda x: x[1]
        )[:3]

        severity_instruction = SEVERITY_PROMPTS.get(self.severity, SEVERITY_PROMPTS["brutal"])

        prompt = f"""
Analyze this code quality report and deliver your roast.

**Severity Mode:** {self.severity.upper()}
**Instruction:** {severity_instruction}

**Code Stats:**
- Language: {language}
- Overall Score: {score}/100
- Files analyzed: {metrics.get('files_analyzed', 0)}
- Total lines: {metrics.get('total_lines', 0)}
- Total issues: {metrics.get('total_issues', 0)}
- Issues per file: {metrics.get('issues_per_file', 0)}

**Severity breakdown:**
- Critical: {metrics.get('severity_counts', {}).get('critical', 0)}
- High: {metrics.get('severity_counts', {}).get('high', 0)}
- Medium: {metrics.get('severity_counts', {}).get('medium', 0)}
- Low: {metrics.get('severity_counts', {}).get('low', 0)}

**Worst categories (score/100):**
{chr(10).join(f'- {cat}: {score}' for cat, score in worst_categories)}

**Top issues found:**
{top_issues}

Respond with JSON in this exact format:
{{
  "overall": "Your devastating 2-3 sentence overall roast of this codebase",
  "sections": [
    {{
      "category": "category name",
      "roast": "specific roast for this category",
      "tip": "one concrete fix"
    }}
  ],
  "closing": "A final savage/funny closing line that references a specific issue",
  "verdict": "One-line verdict for the README/PR"
}}
"""

        response = self._call_api(prompt)
        return self._parse_response(response, score)

    def _summarize_top_issues(self, issues: list, max_issues: int = 10) -> str:
        """Summarize top issues for the AI prompt."""
        if not issues:
            return "No issues found (suspicious...)"

        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        sorted_issues = sorted(
            issues,
            key=lambda x: severity_order.get(
                x.get("severity", "low") if isinstance(x, dict) else x.severity, 3
            )
        )[:max_issues]

        lines = []
        for issue in sorted_issues:
            if isinstance(issue, dict):
                sev = issue.get("severity", "low")
                msg = issue.get("message", "Unknown issue")
                cat = issue.get("category", "style")
                file_path = issue.get("file", "")
            else:
                sev = issue.severity
                msg = issue.message
                cat = issue.category
                file_path = str(issue.file) if issue.file else ""

            file_name = os.path.basename(str(file_path)) if file_path else ""
            lines.append(f"- [{sev.upper()}] ({cat}) {msg}" + (f" in {file_name}" if file_name else ""))

        return "\n".join(lines)

    def _call_api(self, prompt: str) -> str:
        """Call the AI API."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        if self.base_url.startswith("https://openrouter.ai"):
            headers["HTTP-Referer"] = "https://github.com/burnbook/burnbook"
            headers["X-Title"] = "BurnBook Code Roaster"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.9,
            "max_tokens": 1000,
            "response_format": {"type": "json_object"},
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            headers=headers,
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]

    def _parse_response(self, response: str, score: int) -> Dict[str, Any]:
        """Parse the AI response JSON."""
        try:
            data = json.loads(response)
            return {
                "overall": data.get("overall", self._fallback_roast(score)),
                "sections": data.get("sections", []),
                "closing": data.get("closing", ""),
                "verdict": data.get("verdict", ""),
            }
        except json.JSONDecodeError:
            # Try to extract useful content from malformed JSON
            return {
                "overall": self._fallback_roast(score),
                "sections": [],
                "closing": response[:200] if response else "",
                "verdict": "",
            }

    def _fallback_roast(self, score: int) -> str:
        """Offline fallback roasts by score range."""
        if score <= 20:
            return (
                "This code has more red flags than a Soviet parade. "
                "I've seen better structure in a collapsed soufflé. "
                "The git blame for this should come with a restraining order."
            )
        elif score <= 40:
            return (
                "Your code reads like it was written during a power outage "
                "by someone who learned to code from a fortune cookie. "
                "The senior dev who reviews this will develop trust issues."
            )
        elif score <= 60:
            return (
                "It works. Probably. Like a car with four different tire brands "
                "and a prayer to the stack overflow gods. "
                "Mid is generous, but here we are."
            )
        elif score <= 80:
            return (
                "Not bad! You've achieved the rare feat of writing code that "
                "doesn't immediately make your colleagues quit. "
                "A few more commits and you might actually impress someone."
            )
        else:
            return (
                "Alright, I'll admit it — this is genuinely solid code. "
                "You've made BurnBook almost feel bad. Almost. "
                "Don't let it go to your head."
            )


# Static roast lines for offline mode (categorized)
STATIC_ROASTS = {
    "complexity": [
        "This function is so complex, it needs its own zip code.",
        "I've seen simpler plots in a Christopher Nolan film.",
        "Cyclomatic complexity? More like cyclomatic catastrophe.",
        "This code would make a Rube Goldberg machine jealous.",
    ],
    "naming": [
        "Variable names like 'x', 'tmp', and 'data2'? What is this, a cipher?",
        "I've seen better naming conventions in a 4-year-old's crayon drawings.",
        "Did you name these variables while running from something?",
        "Hungarian notation? That's... a choice. A war crime, but a choice.",
    ],
    "security": [
        "Security issues so bad, even script kiddies are embarrassed for you.",
        "You've essentially left the front door open with a neon 'HACK ME' sign.",
        "This security would fail a 1998 CTF challenge.",
        "SQL injection vulnerabilities in {year}? Bold move.",
    ],
    "documentation": [
        "The documentation is so sparse, it makes README.txt look verbose.",
        "Future you will open this file and weep.",
        "No comments? Hope you enjoy relearning this code in 6 months.",
        "This code is like IKEA furniture with no instructions.",
    ],
    "duplication": [
        "Copy-paste so aggressive it's practically plagiarism of yourself.",
        "DRY principle? More like WET — Write Everything Twice (or thrice).",
        "If repetition was a virtue, you'd be a saint.",
        "This code has more copies than a Xerox machine.",
    ],
    "dead_code": [
        "Dead code rotting in your codebase like forgotten leftovers.",
        "This code has more ghosts than a haunted house.",
        "Unused imports collecting dust like gym memberships.",
        "Comment-disabled code: the software equivalent of hoarding.",
    ],
    "testing": [
        "Test coverage so low it's basically untested.",
        "No tests? That's called 'trusting vibes', not engineering.",
        "The production environment is your test environment. Bold.",
        "Writing code without tests is like skydiving without checking the parachute.",
    ],
}


def get_static_roast(category: str) -> str:
    """Get a static (offline) roast for a category."""
    import random
    roasts = STATIC_ROASTS.get(category, ["This category is... something."])
    return random.choice(roasts)
