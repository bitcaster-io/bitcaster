# MediaFile

A `MediaFile` is an image stored in the `mediafiles` storage, scoped to an Organization, Project and optionally an Application, with auto-detected dimensions, size and MIME type.

## Purpose

The `MediaFile` represents an uploaded image used as media (e.g. an image embedded in a notification). It inherits scope fields from `Scoped3Mixin` (organization, project, application): the project and application are optional, and on save/clean the scope is normalized upward so that the project is derived from the application and the organization from the project. The custom `ImageFieldWithExtra` automatically fills `width`, `height`, `size` and `mime_type` from the uploaded file. Records are created when an image is uploaded within an organization/project/application scope. Uniqueness of the `slug` is enforced per scope level: unique together (`slug`, `organization`, `project`, `application`), (`slug`, `organization`, `project`) and (`slug`, `organization`).

## Connections

- `organization` -> `Organization` (on_delete=CASCADE, related_name="%(class)s_set" i.e. `mediafile_set`, blank=True)
- `project` -> `Project` (ChainedForeignKey, chained on `organization`, on_delete=CASCADE, related_name="%(class)s_set" i.e. `mediafile_set`, null=True, blank=True) - Project this record belong to
- `application` -> `Application` (ChainedForeignKey, chained on `project`, on_delete=CASCADE, related_name="%(class)s_set` i.e. `mediafile_set`, null=True, blank=True)
- Unique together: (`slug`, `organization`, `project`, `application`), (`slug`, `organization`, `project`) and (`slug`, `organization`)
- `natural_key` varies by scope level: application-scoped records use the application natural key, project-scoped records use (`None`, *project natural key), organization-scoped records use (`None`, `None`, *organization natural key)

## Fields

| Field | Type | Null | Default | Meaning |
|-------|------|------|---------|---------|
| organization | ForeignKey -> Organization | No | - | Organization |
| project | ChainedForeignKey -> Project | Yes | None | Project this record belong to |
| application | ChainedForeignKey -> Application | Yes | None | - |
| name | CharField(255) | No | - | Name |
| slug | SlugField(255) | No | "" | Record slug (auto-generated from name on save if blank) |
| image | ImageField(storage="mediafiles") | No | - | Media file |
| size | PositiveIntegerField | Yes | 0 | Image size in bytes |
| width | PositiveIntegerField | Yes | 0 | Image width in pixels |
| height | PositiveIntegerField | Yes | 0 | Image height in pixels |
| mime_type | CharField(100) | No | "" | Mime type |
| file_type | CharField(100) | No | "" | - |
| version | IntegerVersionField | No | - | Version number of the record |
| last_updated | DateTimeField | No | - | Record last update time (auto_now) |
| created | DateTimeField | No | - | Record creation time (auto_now_add) |
