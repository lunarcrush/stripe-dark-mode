# Security

This extension runs inside a financial dashboard, so the bar is: no network, no remote code, no data collection, minimum permissions.

- Report a vulnerability to support@lunarcrush.com with "Security" in the subject. Please do not open a public issue for security reports.
- Scope: anything that lets the extension read, exfiltrate, or alter Dashboard data, escalate permissions, or execute remote code.
- Guarantees we hold ourselves to: no `fetch`/XHR to any origin (the only fetch is `chrome.runtime.getURL("theme.css")` in developer mode), no `eval`/remote scripts, no new permissions without a CHANGELOG entry and a version bump, and content scripts that exit on any page that is not the Dashboard or embedded in it.
