# Security Policy

## Public Repository Boundary

This repository must never contain:

- Google, Cloudflare, AWS, OpenAI, or other API credentials;
- production Form URLs or response endpoints;
- customer orders or contact records;
- payment proofs or financial identifiers;
- participant responses or consent records;
- private keys, access tokens, cookies, or session data;
- live form-submission automation.

The checked-in Apps Script adapter reads schema only. The browser demo runs
locally and does not make network requests.

## Reporting

Use the repository's private vulnerability-reporting form:

https://github.com/lzy2767865503-pixel/lrobotform-alpha-lab/security/advisories/new

Do not open a public issue for an unpatched vulnerability or include
credentials, participant data, personal information, or operational details.
