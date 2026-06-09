# Marketplace

Open Schools Platform includes a built-in Marketplace that allows third-party developers to extend the platform's functionality with mini-apps. These applications are securely integrated using OAuth2 and granular permission scopes.

## Features

- **Mini-apps ecosystem:** Extend the platform's functionality with custom applications.
- **Granular OAuth2 Scopes:** Applications request exactly the permissions they need (e.g., `read:organizations`, `write:circles`, `read:tickets`, `read:analytics`).
- **Seamless Context Switching:** Iframe context fully remounts when the user switches between organizations, enforcing strong context isolation. Mini-apps handle session invalidation securely.
- **Jira Service Management Integration:** The entire lifecycle of an application (publishing, updating, secret regeneration, deletion, restoration) is securely managed through Jira Webhooks.
- **Consent Modal:** Users are explicitly asked to grant permissions before installing any mini-app, with localized and user-friendly scope descriptions.

## Developer Integration

Developers interact with the Marketplace by submitting their app details (name, redirect URIs, required/optional scopes) via Jira Service Management. Once the request is approved by the platform administrator, the platform automatically generates the `client_id` and `client_secret` required for the standard OAuth2 authorization code flow.

For SRE and DevOps engineers, ensure that `JIRA_WEBHOOK_SECRET` is set in the `.env` file and configured in Jira Automation rules under the `Authorization: Bearer <secret>` header to securely validate all webhook requests.
