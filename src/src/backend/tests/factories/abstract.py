import datetime
import factory
from dateutil.relativedelta import relativedelta
from factory import fuzzy
from factory.django import DjangoModelFactory


class AlterCreatedAtFactory(DjangoModelFactory):
    class Meta:
        abstract = True

    @factory.post_generation
    def alter_created_at(self, create, extracted, **kwargs):
        if not create:
            return
        new_created_at = kwargs.get("date")
        if new_created_at is not None:
            if isinstance(new_created_at, datetime.datetime):
                self.created_at = new_created_at
            else:
                self.created_at = datetime.datetime.strptime(new_created_at, "%Y/%m/%d")
            self.save()
