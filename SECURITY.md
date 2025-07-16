# Security Policy

## Supported Versions

The table below lists which versions of the project currently receive security updates.

| Version | Supported          |
| ------- | ------------------ |
|   0.4.x | :white_check_mark: |
| < 0.4.1 | :x:                |

I recommend all users upgrade to the latest minor version to receive the latest security patches.

## Reporting a Vulnerability

Security is a top priority for this project.
If you discover a vulnerability, please report it **privately** via GitHub [Security Advisories](https://github.com/Vianpyro/Authentication-Service/security/advisories).
This ensures responsible disclosure and protects users while I work on a fix.

I aim to respond to all reports **as soon as possible** and will issue out-of-band security releases if needed.
You will be notified via GitHub once your advisory is triaged, accepted, resolved, or closed.

If your report leads to a confirmed vulnerability, I would be happy to **publicly acknowledge** your contribution (with your permission) in the project's changelog or a dedicated section in the repository.

## Scope

All security-related concerns are welcome, especially those involving:

- Authentication and session management
- Authorization bypass or privilege escalation
- SQL injection, XSS, CSRF, or other injection attacks
- 2FA/MFA bypass
- RLS policy bypass
- Information disclosure (e.g. sensitive data leaks)
- Misuse of encryption, hashing, or secrets
- Resource exhaustion or DoS vulnerabilities
- Insecure defaults or misconfigurations

Please do **not** report issues like:
- Minor typos or documentation errors
- Non-security bugs (report those via standard GitHub issues)

## Acknowledgments

I appreciate and acknowledge all security researchers and users who responsibly disclose vulnerabilities. If you'd like to be credited, please let me know when reporting.

## Bug Bounty

At this time, I do **not** offer a monetary or private bug bounty program.

## Security Patch Policy

I only maintain security updates for the **latest minor version** of each release line. Users should keep their deployments up to date to receive fixes promptly.
