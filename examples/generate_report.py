"""Generate a framework report from the command line API."""

from __future__ import annotations

from auditrace.reports.generator import generate_report


def main() -> None:
	path = generate_report(framework="eu-ai-act", output_format="html")
	print(f"Generated report: {path}")


if __name__ == "__main__":
	main()
