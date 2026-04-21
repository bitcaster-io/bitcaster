---
tags:
   - SSO
---

# Social Login

Social Login can be configured at <https://SERVER_ADDRESS/admin/social/socialprovider/>

1. Navigate to <https://SERVER_ADDRESS/admin/social/socialprovider/add/>
2. Select one of the supported provider and add related configuration as
   per [Python Social Auth](https://python-social-auth.readthedocs.io/).
3. Be sure `enabled` is checked before saving the form

## Supported backends

### Azure AD

see <https://python-social-auth.readthedocs.io/en/latest/backends/azuread.html#microsoft-azure-active-directory>

#### Tenant support

see <https://python-social-auth.readthedocs.io/en/latest/backends/azuread.html#tenant-support>


### Facebook

see <https://python-social-auth.readthedocs.io/en/latest/backends/facebook.html#oauth2>


### GitLab

see <https://python-social-auth.readthedocs.io/en/latest/backends/gitlab.html>

### GitHub

see <https://python-social-auth.readthedocs.io/en/latest/backends/github.html#github-for-organizations>

#### GitHub Enterprise

see <https://python-social-auth.readthedocs.io/en/latest/backends/github.html#github-enterprise>

#### GitHub Organizations

see <https://python-social-auth.readthedocs.io/en/latest/backends/github.html#github-for-organizations>

#### GitHub Team

see <https://python-social-auth.readthedocs.io/en/latest/backends/github.html#github-team>

![Image title](_screenshots/sso_github.png)

### Google

see <https://python-social-auth.readthedocs.io/en/latest/backends/google.html#google-oauth2>

Sample Configuration:

![Image title](_screenshots/sso_google.png)


### LinkedIn

see <https://python-social-auth.readthedocs.io/en/latest/backends/linkedin.html#linkedin-oauth2>

### Keycloak

see <https://python-social-auth.readthedocs.io/en/latest/backends/keycloak.html>

### WSO2

see <https://python-social-auth.readthedocs.io/en/latest/backends/wso2.html>

### Twitter

see <https://python-social-auth.readthedocs.io/en/latest/backends/twitter_oauth2.html>

### Generic OAuth

see <https://python-social-auth.readthedocs.io/en/latest/backends/oauth.html#oauth2>




## Global configuration

Some global parameters for Social Auth can be configured in the Bitcaster Admin interface at <https://SERVER_ADDRESS/admin/constance/config/>

| Parameter | Default | Description |
| --- | --- | --- |
| `SOCIAL_AUTH_CREATE_USER` | `True` | If true, not existing users will be automatically created. If false, only already existing users can log in via SSO. |
| `SOCIAL_AUTH_ACCEPTED_USERS` | `""` | A comma separated list of emails that are allowed to log in. It supports regular expressions (e.g., `.*@example.com`). |
| `NEW_USER_DEFAULT_GROUP` | `DEFAULT_GROUP_NAME` | The Django Group that will be assigned to any new user created via SSO. |
| `NEW_USER_IS_STAFF` | `False` | If true, any new user created (via SSO or otherwise) will be marked as staff. |
