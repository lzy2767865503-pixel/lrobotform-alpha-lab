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

Report a suspected vulnerability privately to the repository owner through the
GitHub profile rather than opening an issue that exposes credentials, personal
data, or operational details.
