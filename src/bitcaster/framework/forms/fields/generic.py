from django import forms


class HintFieldMixin:
    def __init__(self, *, max_length=None, min_length=None, strip=True, empty_value='', **kwargs):
        self.hint = kwargs.pop('hint', '')
        super().__init__(max_length=max_length, min_length=min_length, strip=strip, empty_value=empty_value, **kwargs)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        if self.hint:
            attrs['placeholder'] = self.hint
            attrs['data-hint'] = self.hint
            attrs['onfocus'] = 'this.placeholder = ""'
            attrs['onblur'] = 'this.placeholder = this.dataset.hint'
        return attrs


class CharField(HintFieldMixin, forms.CharField):
    pass
