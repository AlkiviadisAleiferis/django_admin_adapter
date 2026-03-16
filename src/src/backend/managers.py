from django.db import models


class RelatedNamesManager(models.Manager):
    def __init__(self, select_related_names=None, prefetch_related_names=None):
        super().__init__()
        if select_related_names is not None:
            self.select_related_names = select_related_names
        if prefetch_related_names is not None:
            self.prefetch_related_names = prefetch_related_names

    def get_queryset(self):
        qs = super().get_queryset()

        if hasattr(self, "prefetch_related_names"):
            qs = qs.prefetch_related(*self.prefetch_related_names)

        if hasattr(self, "select_related_names"):
            qs = qs.select_related(*self.select_related_names)

        return qs
