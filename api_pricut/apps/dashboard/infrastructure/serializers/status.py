from apps.utils import ERROR_MESSAGES
from rest_framework import serializers
from typing import Dict, Any


class StatusSerializer(serializers.Serializer):
    """Serializer for the status of the static info."""

    status = serializers.BooleanField(
        required=True,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
        },
    )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the data provided in the request body."""

        # Validate the data provided in the request body
        unknown_fields = set(self.initial_data) - set(self.fields)

        if unknown_fields:
            raise serializers.ValidationError(
                code="invalid_data",
                detail={
                    field: ERROR_MESSAGES["invalid_field"]
                    for field in unknown_fields
                },
            )

        return attrs
