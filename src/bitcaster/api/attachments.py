from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import parsers, serializers
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_409_CONFLICT,
)

from django.utils.translation import gettext_lazy as _

from bitcaster.auth.constants import Grant
from bitcaster.exceptions import AttachmentsNotSupportedError
from bitcaster.models import Application, Attachment

from .base import SecurityMixin


class AttachmentUploadSerializer(serializers.ModelSerializer[Attachment]):
    class Meta:
        model = Attachment
        fields = ("document",)


class AttachmentResponseSerializer(serializers.ModelSerializer[Attachment]):
    class Meta:
        model = Attachment
        fields = ("correlation_id", "filename", "mime_type", "size")
        read_only_fields = ("correlation_id", "filename", "mime_type", "size")


class AttachmentView(SecurityMixin, GenericAPIView[Attachment]):
    serializer_class = AttachmentUploadSerializer
    parser = (parsers.MultiPartParser,)
    http_method_names = ["get", "post", "put"]
    required_grants = [Grant.APPLICATION_ADMIN]

    @extend_schema(
        request=AttachmentUploadSerializer,
        responses={201: AttachmentResponseSerializer},
        description=_(
            "Upload a new document to be used as an attachment for a notification. "
            "Requires the application, project, and organization slugs. "
            "An optional correlation_id can be provided to link the attachment to a specific trigger."
        ),
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        application = get_object_or_404(
            Application,
            slug=self.kwargs["app"],
            project__slug=self.kwargs["prj"],
            project__organization__slug=self.kwargs["org"],
        )
        try:
            self.verify_attachment_support(application)
        except AttachmentsNotSupportedError:
            return Response(
                {"detail": _("This application does not support attachments.")}, status=HTTP_400_BAD_REQUEST
            )

        correlation_id = kwargs.get("correlation_id")
        if (
            correlation_id
            and Attachment.objects.filter(application=application, correlation_id=correlation_id).exists()
        ):
            return Response(
                {"detail": _("Attachment with this correlation ID already exists.")}, status=HTTP_409_CONFLICT
            )

        serializer = AttachmentUploadSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_file = serializer.validated_data["document"]
            attachment = Attachment.objects.create(
                application=application,
                correlation_id=correlation_id,
                document=uploaded_file,
                mime_type=uploaded_file.content_type,
                size=uploaded_file.size,
            )

            response_serializer = AttachmentResponseSerializer(attachment)
            return Response(response_serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=AttachmentUploadSerializer,
        responses={200: AttachmentResponseSerializer},
        description=_("Replace an existing attachment file with a new document using its correlation_id."),
    )
    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        application = get_object_or_404(
            Application,
            slug=self.kwargs["app"],
            project__slug=self.kwargs["prj"],
            project__organization__slug=self.kwargs["org"],
        )
        try:
            self.verify_attachment_support(application)
        except AttachmentsNotSupportedError:
            return Response(
                {"detail": _("This application does not support attachments.")}, status=HTTP_400_BAD_REQUEST
            )

        correlation_id = kwargs.get("correlation_id")
        if not correlation_id:
            return Response(
                {"detail": _("Updating an attachment requires its correlation ID.")}, status=HTTP_400_BAD_REQUEST
            )

        attachment = get_object_or_404(Attachment, application=application, correlation_id=correlation_id)
        serializer = AttachmentUploadSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_file = serializer.validated_data["document"]
            attachment.document = uploaded_file
            attachment.mime_type = uploaded_file.content_type
            attachment.save()

            response_serializer = AttachmentResponseSerializer(attachment)
            return Response(response_serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={200: AttachmentResponseSerializer(many=True)},
        description=_("List all current attachments stored for a specific application."),
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        application = get_object_or_404(
            Application,
            slug=self.kwargs["app"],
            project__slug=self.kwargs["prj"],
            project__organization__slug=self.kwargs["org"],
        )
        attachments = Attachment.objects.filter(application=application)
        serializer = AttachmentResponseSerializer(attachments, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    def verify_attachment_support(self, application: Application) -> None:
        if not application.advanced_configuration.get("support_attachment"):
            raise AttachmentsNotSupportedError
