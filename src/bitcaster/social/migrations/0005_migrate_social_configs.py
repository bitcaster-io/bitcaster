from django.db import migrations


def migrate_configs(apps, schema_editor):
    SocialProvider = apps.get_model("social", "SocialProvider")

    provider_mapping = {
        "GOOGLE_OAUTH2": "google",
        "AZUREAD_OAUTH2": "microsoft",
        "AZUREAD_TENANT_OAUTH2": "microsoft",
        "FACEBOOK": "facebook",
        "GITHUB": "github",
        "GITHUB_ENTERPRISE": "github",
        "GITHUB_ORG": "github",
        "GITHUB_TEAM": "github",
        "GITLAB": "gitlab",
        "LINKEDIN_OAUTH2": "linkedin_oauth2",
        "TWITTER": "twitter",
        "KEYCLOAK": "openid_connect",
        "WSO2": "wso2",
        "OAUTH2": "wso2",
    }

    legacy_keys = {
        "google": "GOOGLE_OAUTH2",
        "microsoft": "AZUREAD_OAUTH2",
        "facebook": "FACEBOOK",
        "github": "GITHUB",
        "gitlab": "GITLAB",
        "linkedin_oauth2": "LINKEDIN_OAUTH2",
        "twitter": "TWITTER",
        "openid_connect": "KEYCLOAK",
        "wso2": "OAUTH2",
    }

    for obj in SocialProvider.objects.all():
        old_provider = obj.provider
        new_provider = provider_mapping.get(old_provider, old_provider.lower().replace("_", ""))

        conf = obj.configuration
        suffix = legacy_keys.get(new_provider, new_provider.upper())

        # Try to find client_id
        client_id = (
            conf.get("client_id")
            or conf.get(f"SOCIAL_AUTH_{suffix}_KEY")
            or conf.get("APP_ID")
            or conf.get("CONSUMER_KEY")
        )

        # Try to find secret
        secret = (
            conf.get("secret")
            or conf.get(f"SOCIAL_AUTH_{suffix}_SECRET")
            or conf.get("API_SECRET")
            or conf.get("CONSUMER_SECRET")
        )

        new_conf = {}
        if client_id:
            new_conf["client_id"] = client_id
        if secret:
            new_conf["secret"] = secret

        # Preserve other important keys if they exist (like URLs for WSO2/Keycloak)
        for key, value in conf.items():
            if key not in new_conf and not key.startswith("SOCIAL_AUTH_"):
                new_conf[key] = value

        # Handle special cases where keys start with SOCIAL_AUTH_ but are not credentials
        if new_provider == "wso2":
            for key in [
                "SOCIAL_AUTH_WSO2_AUTHORIZATION_URL",
                "SOCIAL_AUTH_WSO2_ACCESS_TOKEN_URL",
                "SOCIAL_AUTH_WSO2_USERINFO_URL",
            ]:
                if key in conf:
                    new_conf[key] = conf[key]

        obj.provider = new_provider
        obj.configuration = new_conf
        obj.save()


def reverse_migrate(apps, schema_editor):
    # Reverse migration is hard because we lost the original provider IDs
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("social", "0004_alter_socialprovider_configuration_and_more"),
    ]

    operations = [
        migrations.RunPython(migrate_configs, reverse_migrate),
    ]
