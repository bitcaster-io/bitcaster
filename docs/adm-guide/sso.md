---
tags:
   - SSO
---

# Social Login (SSO)

Social Login is managed via **django-allauth** and can be configured at <https://SERVER_ADDRESS/admin/social/socialprovider/>

1. Navigate to <https://SERVER_ADDRESS/admin/social/socialprovider/add/>
2. Select a provider from the list — all registered `django-allauth` providers are available dynamically (e.g., `google`, `github`, `microsoft`, `openid_connect`).
3. Fill in the **Client ID** and **Secret** fields.
4. If the provider requires an extra key (like Twitter), fill in the **Key** field.
5. Use the **Extra Configuration** JSON field for any provider-specific parameters (e.g., `server_url` for Keycloak).
6. Ensure `enabled` is checked before saving.

## Dynamic Provider Support

Providers are no longer hardcoded — any `django-allauth` provider registered in the system can be used. The provider list in the admin UI is built dynamically from the allauth registry.

### OpenID Connect (OIDC) Multi-Tenancy

Bitcaster supports multiple OpenID Connect tenants (e.g., separate Keycloak realms or different OIDC providers) simultaneously. Each provider configuration is uniquely identified by the combination of **Client ID** and **Provider** type, allowing you to register distinct OIDC realms with their own credentials.

To configure an OIDC provider:
1. Select `openid_connect` as the provider.
2. Set **Client ID** and **Secret** from your OIDC provider.
3. Add the server URL in **Extra Configuration** as in following example:
```json
{
  "server_url": "https://<keycloak-url>/auth/realms/<realm>/.well-known/openid-configuration"
}
```
4. Repeat for additional OIDC tenants with different Client IDs.

### Redirect URIs

The callback URL uses the `SocialProvider` primary key (visible in the admin list):
`http://<your-domain>/social/<pk>/login/callback/`

The pk is assigned automatically when you create the provider record.

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
