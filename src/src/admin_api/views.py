import logging

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger()


class DummyExtraView(GenericAPIView):
    def get(self, request, *args, **kwargs):
        return Response(
            data={
                "data": "simple data text",
            },
            status=status.HTTP_200_OK,
        )
