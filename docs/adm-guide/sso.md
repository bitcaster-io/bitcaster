---
tags:
   - SSO
---

# Social Login (SSO)

Social Login is managed via **django-allauth** and can be configured at <https://SERVER_ADDRESS/admin/social/socialprovider/>

1. Navigate to <https://SERVER_ADDRESS/admin/social/socialprovider/add/>
2. Select a provider from the list (e.g., `google`, `github`, `microsoft`).
3. Fill in the **Client ID** and **Secret** fields.
4. If the provider requires an extra key (like Twitter), fill in the **Key** field.
5. Use the **Extra Configuration** JSON field for any provider-specific parameters (e.g., `server_url` for Keycloak).
6. Ensure `enabled` is checked before saving.

## Supported Providers

### Google
Requires a Google Cloud Project with OAuth 2.0 credentials.
The redirect URI must be: `http://<your-domain>/social/google/login/callback/`

### GitHub
Requires a GitHub OAuth App.
Redirect URI: `http://<your-domain>/social/github/login/callback/`

### Microsoft (Azure AD)
Requires an application registered in the Azure Portal.
Redirect URI: `http://<your-domain>/social/microsoft/login/callback/`

### Keycloak (OpenID Connect)
Managed via the **Keycloak** provider.
Set **Client ID** and **Secret**, then add the server URL in **Extra Configuration**:
```json
{
  "server_url": "https://<keycloak-url>/auth/realms/<realm>/.well-known/openid-configuration"
}
```

---

## Passkeys (WebAuthn)
Bitcaster now supports **Passkeys**. This allows users to log in without passwords using biometric sensors (TouchID, FaceID) or security keys (YubiKey).

To enable Passkeys:
1. Log in to Bitcaster.
2. Navigate to your Security settings (usually at `/mfa/list/`).
3. Click on **Add Passkey** and follow the browser prompts.
4. Once registered, you can log in directly using the "Login with Passkey" option from the login page.

---

## Global Configuration

Parameters available at <https://SERVER_ADDRESS/admin/constance/config/>:

| Parameter                      | Default | Description |
|--------------------------------| -- | --- |
| `SOCIAL_AUTH_CREATE_USER`      | `True` | If enabled, new users are automatically created on first SSO login. |
| `SOCIAL_AUTH_ACCEPTED_USERS`   | `''` | Regex list (comma separated) of emails allowed to log in. |
| `NEW_USER_DEFAULT_GROUP`       | `Users` | The Django Group assigned to new SSO users. |
