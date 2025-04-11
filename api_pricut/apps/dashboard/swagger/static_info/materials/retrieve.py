from apps.exceptions import DatabaseConnectionAPIError
from apps.utils import StaticInfoErrorMessages
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
)
from drf_spectacular.plumbing import build_array_type


# Error messages
MATERIAL_NOT_FOUND = StaticInfoErrorMessages.MATERIAL_NOT_FOUND.value


data_schema = {
    "type": "object",
    "properties": {
        "base_info": {
            "type": "object",
            "properties": {
                "code": {"type": "string"},
                "name": {"type": "string"},
                "category": {"type": "string"},
            },
        },
        "descriptions": {
            "type": "object",
            "properties": {
                "description_text": {"type": "string"},
                "about_text": {"type": "string"},
                "common_uses_text": {"type": "string"},
                "features_highlights": {
                    "type": "array",
                    "items": {"type": "object"},
                },
            },
        },
        "images": {
            "type": "object",
            "properties": {
                "banner_image": {"type": "string", "format": "uri"},
                "description_image": {"type": "string", "format": "uri"},
                "about_image": {"type": "string", "format": "uri"},
                "uses_image": {"type": "string", "format": "uri"},
                "texture_image": {"type": "string", "format": "uri"},
            },
        },
        "thicknesses": {
            "type": "array",
            "items": {"type": "object"},
        },
    },
}


ListMaterialSchema = extend_schema(
    operation_id="list_materials",
    tags=["Dashboard"],
    responses={
        200: OpenApiResponse(
            description="**(OK)** The organized information on the requested materials is returned.",
            response=build_array_type(schema=data_schema),
            examples=[
                OpenApiExample(
                    name="response_ok",
                    summary="Retrieve static information",
                    description="The information about the materials available in the platform is returned.",
                    value=[
                        {
                            "base_info": {
                                "name": "Aluminio",
                                "code": "aluminio",
                                "category": "metales",
                            },
                            "descriptions": {
                                "description_text": "Descripción del material.",
                                "about_text": "Acerca del material.",
                                "common_uses_text": "Usos comunes del material.",
                                "features_highlights": [
                                    {
                                        "title": "Titulo",
                                        "image": "https://image.png",
                                    },
                                    {
                                        "title": "Titulo",
                                        "image": "https://image.png",
                                    },
                                    {
                                        "title": "Titulo",
                                        "image": "https://image.png",
                                    },
                                ],
                            },
                            "images": {
                                "banner_image": "https://image.png",
                                "description_image": "https://image.png",
                                "about_image": "https://image.png",
                                "uses_image": "https://image.png",
                                "texture_image": "https://image.png",
                            },
                            "thicknesses": [
                                {
                                    "value": 1.50,
                                    "fiber_laser": True,
                                    "co2_laser": True,
                                    "router_cnc": False,
                                },
                                {
                                    "value": 2.50,
                                    "fiber_laser": True,
                                    "co2_laser": True,
                                    "router_cnc": True,
                                },
                                {
                                    "value": 3.50,
                                    "fiber_laser": True,
                                    "co2_laser": False,
                                    "router_cnc": False,
                                },
                            ],
                        },
                        {
                            "base_info": {
                                "name": "Triplex",
                                "code": "triplex",
                                "category": "maderas",
                            },
                            "descriptions": {
                                "description_text": "Descripción del material.",
                                "about_text": "Acerca del material.",
                                "common_uses_text": "Usos comunes del material.",
                                "features_highlights": [
                                    {
                                        "title": "Titulo",
                                        "image": "https://image.png",
                                    },
                                    {
                                        "title": "Titulo",
                                        "image": "https://image.png",
                                    },
                                    {
                                        "title": "Titulo",
                                        "image": "https://image.png",
                                    },
                                ],
                            },
                            "images": {
                                "banner_image": "https://image.png",
                                "description_image": "https://image.png",
                                "about_image": "https://image.png",
                                "uses_image": "https://image.png",
                                "texture_image": "https://image.png",
                            },
                            "thicknesses": [
                                {
                                    "value": 1.50,
                                    "fiber_laser": True,
                                    "co2_laser": True,
                                    "router_cnc": False,
                                },
                                {
                                    "value": 2.50,
                                    "fiber_laser": True,
                                    "co2_laser": True,
                                    "router_cnc": True,
                                },
                                {
                                    "value": 3.50,
                                    "fiber_laser": True,
                                    "co2_laser": False,
                                    "router_cnc": False,
                                },
                            ],
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
                    name="materials_not_found",
                    summary="Materials not found",
                    description="No existing materials were found in the database.",
                    value={
                        "code": MATERIAL_NOT_FOUND["code"],
                        "detail": MATERIAL_NOT_FOUND["detail"],
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
