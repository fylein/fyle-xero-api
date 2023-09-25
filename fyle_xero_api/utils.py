from rest_framework.serializers import ValidationError
from rest_framework.views import Response


def assert_valid(condition: bool, message: str) -> Response or None:
    """
    Assert conditions
    :param condition: Boolean condition
    :param message: Bad request message
    :return: Response or None
    """
    if not condition:
        raise ValidationError(detail={"message": message})


class LookupFieldMixin:
    lookup_field = "workspace_id"

    def filter_queryset(self, queryset):
        if self.lookup_field in self.kwargs:
            lookup_value = self.kwargs[self.lookup_field]
            filter_kwargs = {self.lookup_field: lookup_value}
            queryset = queryset.filter(**filter_kwargs)
        return super().filter_queryset(queryset)
