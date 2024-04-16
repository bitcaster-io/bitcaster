from . import base


def get_factory_for_model(_model) -> type[base.TAutoRegisterModelFactory]:
    class Meta:
        model = _model

    bases = (base.AutoRegisterModelFactory,)
    if _model in base.factories_registry:
        return base.factories_registry[_model]  # noqa

    return type(f"{_model._meta.model_name}Factory", bases, {"Meta": Meta})  # noqa
