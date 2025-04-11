from datetime import timedelta


ACCESS_TOKEN_LIFETIME = timedelta(hours=3)


AUTH_PERMISSIONS = {
    "jwt_auth": "authentication.add_jwt",
}
