from django import forms

from bitcaster.forms import unfold
from bitcaster.models import Project


class ProjectBaseForm(forms.ModelForm["Project"]):
    slug = forms.SlugField(required=False, widget=unfold.UnfoldAdminTextInputWidget)

    class Meta:
        model = Project
        exclude = ("config", "locked")  # noqa: DJ006

    def full_clean(self) -> None:
        return super().full_clean()


class ProjectAddForm(ProjectBaseForm):
    class Meta:
        model = Project
        exclude = ("channels", "locked")  # noqa: DJ006


class ProjectChangeForm(ProjectBaseForm):
    class Meta:
        model = Project
        fields = ("name", "slug", "organization", "owner", "from_email", "subject_prefix", "environments", "locked")
