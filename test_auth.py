from src.auth.google_auth_service import GoogleAuthService

service = GoogleAuthService()

print(service.get_authorization_url("user"))
