"""Сервис для аутентификации Google"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
import logging

logger = logging.getLogger(__name__)
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]
CLIENT_SECRETS_FILE = 'credentials.json'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

class GoogleAuthService:
    """Сервис для аутентификации Google"""

    def __init__(self):
        self.credentials_cache: dict[int, Credentials] = {}


    def _create_oauth_flow(self) -> Flow:
        """Создаёт флоу

        Returns:
            флоу для дальнейшего создания URL.
        """
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI,
        )

        return flow

    def get_authorization_url(self, user_id: str) -> str:
        """Создаёт URL для авторизации

        Args:
            user_id: идентификатор пользователя.

        Returns
            Ссылка для авторизации.
        """
        try:
            flow = self._create_oauth_flow()

            authorization_url, _ = flow.authorization_url(
                access_type="offline",
                include_granted_scopes="true",
                prompt="consent",
            )

            logger.info(
                "Generated auth URL for user %s",
                user_id
            )
            return authorization_url
        except Exception as err:
            logger.error(
                "Error generating auth URL for user %s: %s",
                user_id,
                err
            )
            raise
    def exchange_code_for_token(
        self,
        code: str,
        user_id: str
    ) -> Credentials:
        try:
            flow = self._create_oauth_flow()
            flow.fetch_token(code=code)
            creds = flow.credentials

            logger.info("Code exchanged")
            return creds
        except Exception as err:
            logger.error("Error exchanging: %s", err)
            raise
