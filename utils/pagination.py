from rest_framework.pagination import LimitOffsetPagination


class CustomOffSetPagination(LimitOffsetPagination):
    default_limit = 25
    max_limit = 100


def paginate(instances, serializator, request, **kwargs):
    paginator = CustomOffSetPagination()
    paginated_order = paginator.paginate_queryset(instances, request)

    serializer = serializator(paginated_order, many=True, **kwargs)

    return paginator.get_paginated_response(serializer.data)
