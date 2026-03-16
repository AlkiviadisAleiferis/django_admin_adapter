from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.exceptions import PermissionDenied


class PasswordChange(GenericAPIView):
    permission_classes = [] # will be set inside adapter

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        user_model_admin = self._admin_site._registry.get(request.user.__class__)

        if user_model_admin is None:
            raise PermissionDenied()

        # make sure no restriction has been enabled from get_queryset
        user = user_model_admin.get_object(request, request.user.pk)

        # make sure no permission restriction exists
        if user is None or not user_model_admin.has_change_permission(request, user):
            raise PermissionDenied()

        self.model_admin = user_model_admin

    def post(self, request, *args, **kwargs):
        form = self.model_admin.change_password_form(request.user, request.POST)

        old_password = request.POST.get("old_password")
        if not old_password:
            return Response(
                data={
                    "error_data": {
                        "old_password": [{"message": "The old password must be provided."}]
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif not request.user.check_password(old_password):
            return Response(
                data={
                    "error_data": {
                        "old_password": [{"message": "The password is incorrect."}]
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if form.is_valid():
            form.save()
            change_message = self.model_admin.construct_change_message(request, form, None)
            self.model_admin.log_change(request, request.user, change_message)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(
                data={
                    "error_data": form.errors.get_json_data(escape_html=False),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
