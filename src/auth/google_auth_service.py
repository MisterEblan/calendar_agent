from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
import logging

logger = logging.getLogger(__name__)

class GoogleAuthService:
    """Сервис для аутентификации Google"""

    def __init__(self):
        self.credentials_cache: dict[int, Credentials] = {}
        
        self.SCOPES = [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events'
        ]
        
        self.CLIENT_SECRETS_FILE = 'credentials_web.json'
        
        self.REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

    def _create_oauth_flow(self) -> Flow:
        """Создаёт флоу

        Returns:
            флоу для дальнейшего создания URL.
        """
        flow = Flow.from_client_secrets_file(
            self.CLIENT_SECRETS_FILE,
            scopes=self.SCOPES,
            redirect_uri=self.REDIRECT_URI,
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
                access_type='online',
                include_granted_scopes='true',
                prompt='consent',
                state=user_id,
                # response_type="code"
            )
            
            logger.info(f"Generated auth URL for user {user_id}")
            return authorization_url
            
        except Exception as e:
            logger.error(f"Error generating auth URL for user {user_id}: {e}")
            raise
