"""OAuth2 Integration for Daur-AI v2.0"""
import logging
import json
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
from urllib.parse import urlencode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests not available")


class OAuthProvider(Enum):
    GOOGLE = "google"
    GITHUB = "github"
    FACEBOOK = "facebook"
    MICROSOFT = "microsoft"


class GoogleOAuth:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"
    
    def get_authorization_url(self, scope: str = "openid email profile") -> str:
        state = secrets.token_urlsafe(32)
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": scope,
            "state": state
        }
        return f"{self.auth_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str) -> Optional[Dict]:
        if not REQUESTS_AVAILABLE:
            logger.error("requests not available")
            return None
        
        try:
            data = {
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,
                "grant_type": "authorization_code"
            }
            
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            
            logger.info("Google token exchanged successfully")
            return response.json()
        except Exception as e:
            logger.error(f"Error exchanging code: {e}")
            return None
    
    def get_user_info(self, access_token: str) -> Optional[Dict]:
        if not REQUESTS_AVAILABLE:
            return None
        
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(self.userinfo_url, headers=headers)
            response.raise_for_status()
            
            user_info = response.json()
            logger.info(f"Google user info retrieved: {user_info.get('email')}")
            return user_info
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None


class GitHubOAuth:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_url = "https://github.com/login/oauth/authorize"
        self.token_url = "https://github.com/login/oauth/access_token"
        self.userinfo_url = "https://api.github.com/user"
    
    def get_authorization_url(self, scope: str = "user:email") -> str:
        state = secrets.token_urlsafe(32)
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": scope,
            "state": state
        }
        return f"{self.auth_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str) -> Optional[Dict]:
        if not REQUESTS_AVAILABLE:
            return None
        
        try:
            data = {
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri
            }
            
            headers = {"Accept": "application/json"}
            response = requests.post(self.token_url, data=data, headers=headers)
            response.raise_for_status()
            
            logger.info("GitHub token exchanged successfully")
            return response.json()
        except Exception as e:
            logger.error(f"Error exchanging code: {e}")
            return None
    
    def get_user_info(self, access_token: str) -> Optional[Dict]:
        if not REQUESTS_AVAILABLE:
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            response = requests.get(self.userinfo_url, headers=headers)
            response.raise_for_status()
            
            user_info = response.json()
            logger.info(f"GitHub user info: {user_info.get('login')}")
            return user_info
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None


class FacebookOAuth:
    def __init__(self, app_id: str, app_secret: str, redirect_uri: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri
        self.auth_url = "https://www.facebook.com/v12.0/dialog/oauth"
        self.token_url = "https://graph.facebook.com/v12.0/oauth/access_token"
        self.userinfo_url = "https://graph.facebook.com/me"
    
    def get_authorization_url(self, scope: str = "email,public_profile") -> str:
        state = secrets.token_urlsafe(32)
        params = {
            "client_id": self.app_id,
            "redirect_uri": self.redirect_uri,
            "scope": scope,
            "state": state,
            "response_type": "code"
        }
        return f"{self.auth_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str) -> Optional[Dict]:
        if not REQUESTS_AVAILABLE:
            return None
        
        try:
            params = {
                "client_id": self.app_id,
                "client_secret": self.app_secret,
                "redirect_uri": self.redirect_uri,
                "code": code
            }
            
            response = requests.get(self.token_url, params=params)
            response.raise_for_status()
            
            logger.info("Facebook token exchanged successfully")
            return response.json()
        except Exception as e:
            logger.error(f"Error exchanging code: {e}")
            return None
    
    def get_user_info(self, access_token: str) -> Optional[Dict]:
        if not REQUESTS_AVAILABLE:
            return None
        
        try:
            params = {
                "access_token": access_token,
                "fields": "id,name,email,picture"
            }
            response = requests.get(self.userinfo_url, params=params)
            response.raise_for_status()
            
            user_info = response.json()
            logger.info(f"Facebook user: {user_info.get('name')}")
            return user_info
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None


class OAuth2Manager:
    def __init__(self):
        self.providers: Dict[str, Any] = {}
        self.sessions: Dict[str, Dict] = {}
    
    def register_provider(self, provider_type: OAuthProvider, **config):
        if provider_type == OAuthProvider.GOOGLE:
            self.providers["google"] = GoogleOAuth(**config)
        elif provider_type == OAuthProvider.GITHUB:
            self.providers["github"] = GitHubOAuth(**config)
        elif provider_type == OAuthProvider.FACEBOOK:
            self.providers["facebook"] = FacebookOAuth(**config)
        
        logger.info(f"OAuth provider registered: {provider_type.value}")
    
    def get_authorization_url(self, provider: str) -> Optional[str]:
        if provider not in self.providers:
            logger.error(f"Provider not registered: {provider}")
            return None
        
        return self.providers[provider].get_authorization_url()
    
    def handle_callback(self, provider: str, code: str) -> Optional[Dict]:
        if provider not in self.providers:
            return None
        
        token_data = self.providers[provider].exchange_code_for_token(code)
        if not token_data:
            return None
        
        user_info = self.providers[provider].get_user_info(
            token_data.get("access_token")
        )
        
        if not user_info:
            return None
        
        return {
            "provider": provider,
            "user_info": user_info,
            "token_data": token_data,
            "timestamp": datetime.now().isoformat()
        }
    
    def create_session(self, user_id: int, provider: str, user_info: Dict) -> str:
        session_id = secrets.token_urlsafe(32)
        self.sessions[session_id] = {
            "user_id": user_id,
            "provider": provider,
            "user_info": user_info,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(hours=24)
        }
        
        logger.info(f"OAuth session created: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        session = self.sessions.get(session_id)
        
        if not session:
            return None
        
        if datetime.now() > session["expires_at"]:
            del self.sessions[session_id]
            return None
        
        return session
    
    def revoke_session(self, session_id: str) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"OAuth session revoked: {session_id}")
            return True
        return False
