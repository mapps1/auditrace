# Security Policy

## Supported Versions

Security fixes are applied to the latest published minor version.

| Version | Supported |
|---|---|
| 0.1.x | Yes |
| < 0.1.0 | No |

## Reporting a Vulnerability

Do not open public issues for suspected vulnerabilities.

Report privately with:

- affected version
- impact summary
- proof of concept or reproduction steps
- suggested remediation (if available)

Preferred channel: open a GitHub security advisory draft in the repository security tab.

If security advisories are unavailable in your environment, open a private maintainer contact through the repository owner profile and include "[SECURITY]" in the subject.

## Response Expectations

- Initial acknowledgement target: 3 business days.
- Triage target: 7 business days.
- Fix timeline depends on severity and exploitability.

## Scope Notes

High-priority classes include:

- signature/key handling vulnerabilities
- integrity verification bypasses
- unsafe default logging behavior that leaks sensitive content
- report forgery or misleading integrity status

## Disclosure

After remediation, maintainers may publish:

- affected versions
- severity and impact
- mitigation steps and upgrade guidance
