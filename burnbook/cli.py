"""
BurnBook CLI - Entry point for the code quality roaster.
"""

import sys
import os
import click
from pathlib import Path
from typing import Optional

from burnbook import __version__
from burnbook.analyzer import Analyzer
from burnbook.roaster import Roaster
from burnbook.formatters import (
    ConsoleFormatter,
    JSONFormatter,
    HTMLFormatter,
    get_score_badge,
    get_score_label,
)


BANNER = r"""
 ____                   ____              _    
|  _ \                 |  _ \            | |   
| |_) |_   _ _ __ _ __ | |_) | ___   ___ | | __
|  _ <| | | | '__| '_ \|  _ < / _ \ / _ \| |/ /
| |_) | |_| | |  | | | | |_) | (_) | (_) |   < 
|____/ \__,_|_|  |_| |_|____/ \___/ \___/|_|\_\

  Your code's honest friend. (That no one asked for.)
  v{version}
"""


def print_banner():
    click.echo(click.style(BANNER.format(version=__version__), fg="red", bold=True))


@click.group()
@click.version_option(__version__, prog_name="burnbook")
def cli():
    """BurnBook — The code quality roaster that tells it like it is.\n
    Your code will never feel safe again. 🔥
    """
    pass


@cli.command()
@click.argument("target", default=".", type=click.Path(exists=True))
@click.option("--lang", "-l", default=None,
              type=click.Choice(["python", "javascript", "typescript", "go", "rust", "java", "auto"]),
              help="Language to analyze (default: auto-detect)")
@click.option("--severity", "-s", default="brutal",
              type=click.Choice(["gentle", "medium", "brutal", "nuclear"]),
              help="Roast severity level")
@click.option("--format", "-f", "output_format", default="console",
              type=click.Choice(["console", "json", "html"]),
              help="Output format")
@click.option("--ci", is_flag=True, default=False,
              help="CI mode: exit with non-zero code if score < 60")
@click.option("--ci-threshold", default=60, type=int,
              help="CI failure threshold (default: 60)")
@click.option("--offline", is_flag=True, default=False,
              help="Offline mode: skip AI roasting (static analysis only)")
@click.option("--no-banner", is_flag=True, default=False,
              help="Skip the ASCII banner")
@click.option("--max-files", default=500, type=int,
              help="Maximum files to analyze (default: 500)")
@click.option("--exclude", multiple=True,
              help="Glob patterns to exclude (can use multiple times)")
@click.option("--output", "-o", default=None, type=click.Path(),
              help="Output file path (for json/html formats)")
def roast(
    target: str,
    lang: Optional[str],
    severity: str,
    output_format: str,
    ci: bool,
    ci_threshold: int,
    offline: bool,
    no_banner: bool,
    max_files: int,
    exclude: tuple,
    output: Optional[str],
):
    """Roast a codebase or file with brutal honesty.\n
    TARGET can be a file or directory (default: current directory).

    \b
    Examples:
      burnbook roast .
      burnbook roast ./src/app.py --severity nuclear
      burnbook roast . --lang python --format json
      burnbook roast . --ci --ci-threshold 70
      burnbook roast . --offline
    """
    if not no_banner and output_format == "console":
        print_banner()

    target_path = Path(target).resolve()

    # Run analysis
    with click.progressbar(
        length=100,
        label=click.style("🔍 Analyzing your code crimes...", fg="yellow"),
        bar_template="%(label)s  %(bar)s  %(info)s",
        fill_char=click.style("█", fg="red"),
        empty_char="░",
        show_percent=True,
        show_eta=False,
    ) if output_format == "console" else _null_context() as bar:

        analyzer = Analyzer(
            target=target_path,
            language=lang,
            max_files=max_files,
            exclude_patterns=list(exclude),
            progress_callback=bar.update if output_format == "console" else None,
        )

        results = analyzer.analyze()

    # AI Roasting
    if not offline:
        api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if api_key:
            if output_format == "console":
                click.echo(click.style("\n🤖 Summoning AI roast master...", fg="magenta"))
            roaster = Roaster(api_key=api_key, severity=severity)
            results = roaster.roast(results)
        else:
            if output_format == "console":
                click.echo(click.style(
                    "\n⚠️  No API key found. Running in offline mode.\n"
                    "   Set OPENROUTER_API_KEY or OPENAI_API_KEY for AI roasting.\n",
                    fg="yellow"
                ))
    else:
        if output_format == "console":
            click.echo(click.style("\n📴 Offline mode — static analysis only.\n", fg="cyan"))

    # Format and output
    if output_format == "console":
        formatter = ConsoleFormatter(severity=severity)
        formatter.render(results)
    elif output_format == "json":
        formatter = JSONFormatter()
        content = formatter.render(results)
        if output:
            Path(output).write_text(content)
            click.echo(f"📄 JSON report saved to {output}")
        else:
            click.echo(content)
    elif output_format == "html":
        formatter = HTMLFormatter(severity=severity)
        content = formatter.render(results)
        out_path = output or "burnbook-report.html"
        Path(out_path).write_text(content)
        if output_format != "json":
            click.echo(f"📄 HTML report saved to {out_path}")

    # CI mode exit code
    if ci:
        score = results.get("score", 0)
        if score < ci_threshold:
            click.echo(click.style(
                f"\n💥 CI FAILED: Score {score} < threshold {ci_threshold}",
                fg="red", bold=True
            ), err=True)
            sys.exit(1)
        else:
            click.echo(click.style(
                f"\n✅ CI PASSED: Score {score} >= threshold {ci_threshold}",
                fg="green", bold=True
            ), err=True)


@cli.command()
@click.argument("target", default=".", type=click.Path(exists=True))
@click.option("--output", "-o", default="burnbook-report.html", type=click.Path(),
              help="Output HTML file path")
@click.option("--lang", "-l", default=None,
              type=click.Choice(["python", "javascript", "typescript", "go", "rust", "java", "auto"]),
              help="Language to analyze")
@click.option("--offline", is_flag=True, default=False,
              help="Offline mode: skip AI roasting")
@click.option("--severity", "-s", default="brutal",
              type=click.Choice(["gentle", "medium", "brutal", "nuclear"]),
              help="Roast severity level")
def report(target: str, output: str, lang: Optional[str], offline: bool, severity: str):
    """Generate a beautiful HTML roast report.\n
    \b
    Examples:
      burnbook report .
      burnbook report ./src --output my-report.html
    """
    print_banner()
    target_path = Path(target).resolve()

    click.echo(click.style("🔍 Analyzing codebase...", fg="yellow"))
    analyzer = Analyzer(target=target_path, language=lang, max_files=500)
    results = analyzer.analyze()

    if not offline:
        api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if api_key:
            click.echo(click.style("🤖 Generating AI roast commentary...", fg="magenta"))
            roaster = Roaster(api_key=api_key, severity=severity)
            results = roaster.roast(results)

    formatter = HTMLFormatter(severity=severity)
    content = formatter.render(results)
    Path(output).write_text(content)

    score = results.get("score", 0)
    badge = get_score_badge(score)
    label = get_score_label(score)

    click.echo(f"\n{badge} Score: {score}/100 — {label}")
    click.echo(click.style(f"\n📊 HTML report saved to: {output}", fg="green", bold=True))
    click.echo(click.style(f"   Open with: open {output}", fg="cyan"))


@cli.command()
def install_hook():
    """Install BurnBook as a pre-commit git hook.\n
    Runs burnbook roast on staged files before each commit.
    """
    hook_path = Path(".git/hooks/pre-commit")

    if not Path(".git").exists():
        click.echo(click.style("❌ Not a git repository!", fg="red"))
        sys.exit(1)

    hook_content = """#!/bin/sh
# BurnBook pre-commit hook
echo "🔥 BurnBook is judging your code..."
burnbook roast . --ci --ci-threshold 50 --no-banner --format console
if [ $? -ne 0 ]; then
    echo "❌ BurnBook says: Fix your code before committing, coward."
    exit 1
fi
echo "✅ BurnBook approves. Barely."
"""
    hook_path.write_text(hook_content)
    hook_path.chmod(0o755)
    click.echo(click.style("✅ Pre-commit hook installed!", fg="green"))
    click.echo("   BurnBook will now judge your code before every commit.")
    click.echo(click.style("   You've been warned. 🔥", fg="red"))


class _null_context:
    """Null context manager for non-console output."""
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def update(self, n=1):
        pass


def main():
    cli()


if __name__ == "__main__":
    main()
