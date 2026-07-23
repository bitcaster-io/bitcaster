# Should match when a sensitive field is in list_display (tuple form).
class SensitiveFieldTupleAdmin(ModelAdmin):
    # ruleid: bitcaster-admin-sensitive-fields-in-list-display
    list_display = ("name", "secret")


# Should match when a sensitive field is in list_display (list form).
class SensitiveFieldListAdmin(ModelAdmin):
    # ruleid: bitcaster-admin-sensitive-fields-in-list-display
    list_display = ["name", "token"]


# Should match a compound sensitive name.
class CompoundSensitiveAdmin(ModelAdmin):
    # ruleid: bitcaster-admin-sensitive-fields-in-list-display
    list_display = ("name", "api_key")


# Should match 'password' in list_display.
class PasswordFieldAdmin(ModelAdmin):
    # ruleid: bitcaster-admin-sensitive-fields-in-list-display
    list_display = ("password",)


# Should match multiple sensitive fields.
class MultipleSensitiveAdmin(ModelAdmin):
    # ruleid: bitcaster-admin-sensitive-fields-in-list-display
    list_display = ("name", "secret", "token", "api_key")


# Should match with BitcasterModelAdmin base class.
class BitcasterSensitiveAdmin(BitcasterModelAdmin):
    # ruleid: bitcaster-admin-sensitive-fields-in-list-display
    list_display = ("name", "secret")


# Should match case-insensitively.
class CaseInsensitiveSensitiveAdmin(ModelAdmin):
    # ruleid: bitcaster-admin-sensitive-fields-in-list-display
    list_display = ("name", "Secret")


# Should match when sensitive field is the first item.
class FirstItemSensitiveAdmin(ModelAdmin):
    # ruleid: bitcaster-admin-sensitive-fields-in-list-display
    list_display = ("key", "name")


# Should not match when no sensitive fields are present.
class SafeAdmin(ModelAdmin):
    # ok: bitcaster-admin-sensitive-fields-in-list-display
    list_display = ("name", "email", "is_active")


# Should not match when fields are non-sensitive.
class NonSensitiveCompoundAdmin(ModelAdmin):
    # ok: bitcaster-admin-sensitive-fields-in-list-display
    list_display = ("name", "slug")


# Should not match when the class is not an admin.
class SomeModel:
    # ok: bitcaster-admin-sensitive-fields-in-list-display
    list_display = ("name", "secret")
