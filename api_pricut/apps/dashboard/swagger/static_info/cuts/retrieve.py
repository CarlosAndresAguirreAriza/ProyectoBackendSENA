from apps.utils import StaticInfoErrorMessages
from apps.exceptions import DatabaseConnectionAPIError
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
)
from drf_spectacular.plumbing import build_array_type


# Error messages
CUT_NOT_FOUND = StaticInfoErrorMessages.CUT_NOT_FOUND.value


data_schema = {
    "type": "object",
    "properties": {
        "base_info": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "code": {"type": "string"},
            },
        },
        "descriptions": {
            "type": "object",
            "properties": {
                "main_text": {"type": "string"},
                "card_text": {"type": "string"},
                "about_text": {"type": "string"},
                "common_uses_text": {"type": "string"},
            },
        },
        "images": {
            "type": "object",
            "properties": {
                "banner_image": {"type": "string", "format": "uri"},
                "card_image": {"type": "string", "format": "uri"},
                "main_image": {"type": "string", "format": "uri"},
                "about_image": {"type": "string", "format": "uri"},
                "uses_image": {"type": "string", "format": "uri"},
            },
        },
    },
}


ListCutSchema = extend_schema(
    operation_id="get_cut",
    tags=["Dashboard"],
    responses={
        200: OpenApiResponse(
            description="**(OK)** The requested information about the cutting technique is returned.",
            response=build_array_type(schema=data_schema),
            examples=[
                OpenApiExample(
                    name="response_ok",
                    summary="Retrieve cutting technique information",
                    description="The information about the cutting technique available in the platform is returned.",
                    value=[
                        {
                            "base_info": {
                                "name": "Router CNC",
                                "code": "router_cnc",
                            },
                            "descriptions": {
                                "about_text": "Descripción de la técnica de corte.",
                                "common_uses_text": "Descripción de la tarjeta servicio.",
                                "main_text": "Acerca de la técnica de corte.",
                                "card_text": "Usos comunes de la técnica de corte.",
                            },
                            "images": {
                                "banner_image": "https://image.png",
                                "main_image": "https://image.png",
                                "card_image": "https://image.png",
                                "about_image": "https://image.png",
                                "uses_image": "https://image.png",
                            },
                        },
                        {
                            "base_info": {
                                "name": "Láser de fibra",
                                "code": "laser_fibra",
                            },
                            "descriptions": {
                                "about_text": "Descripción de la técnica de corte.",
                                "common_uses_text": "Descripción de la tarjeta servicio.",
                                "main_text": "Acerca de la técnica de corte.",
                                "card_text": "Usos comunes de la técnica de corte.",
                            },
                            "images": {
                                "banner_image": "https://image.png",
                                "main_image": "https://image.png",
                                "card_image": "https://image.png",
                                "about_image": "https://image.png",
                                "uses_image": "https://image.png",
                            },
                        },
                        {
                            "base_info": {
                                "name": "Láser de CO2",
                                "code": "laser_co2",
                            },
                            "descriptions": {
                                "about_text": "Descripción de la técnica de corte.",
                                "common_uses_text": "Descripción de la tarjeta servicio.",
                                "main_text": "Acerca de la técnica de corte.",
                                "card_text": "Usos comunes de la técnica de corte.",
                            },
                            "images": {
                                "banner_image": "https://image.png",
                                "main_image": "https://image.png",
                                "card_image": "https://image.png",
                                "about_image": "https://image.png",
                                "uses_image": "https://image.png",
                            },
                        },
                    ],
                )
            ],
        ),
        404: OpenApiResponse(
            description="**(NOT_FOUND)** Some resources necessary for this process were not found in the database.",
            response={
                "properties": {
                    "code": {"type": "string"},
                    "detail": {"type": "string"},
                }
            },
            examples=[
                OpenApiExample(
                    name="cuts_not_found",
                    summary="Cutting technique not found",
                    description="No cutting technique was found in the database.",
                    value={
                        "code": CUT_NOT_FOUND["code"],
                        "detail": CUT_NOT_FOUND["detail"],
                    },
                ),
            ],
        ),
        500: OpenApiResponse(
            description="**(INTERNAL_SERVER_ERROR)** An unexpected error occurred.",
            response={
                "properties": {
                    "detail": {"type": "string"},
                    "code": {"type": "string"},
                }
            },
            examples=[
                OpenApiExample(
                    name="database_connection_error",
                    summary="Database connection error",
                    description="The connection to the database could not be established.",
                    value={
                        "code": DatabaseConnectionAPIError.default_code,
                        "detail": DatabaseConnectionAPIError.default_detail,
                    },
                ),
            ],
        ),
    },
)
