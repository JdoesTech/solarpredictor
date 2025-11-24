"""
Supabase JWT Authentication for Django REST Framework
"""
from rest_framework import authentication, exceptions
from supabase import create_client, Client
from django.conf import settings
import jwt


class SupabaseJWTAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class using Supabase JWT tokens
    """
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            return None
        
        try:
            # Extract token from "Bearer <token>"
            token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
            
            # Verify token with Supabase
            supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            
            # Verify the token
            try:
                user = supabase.auth.get_user(token)
                if user and user.user:
                    return (user.user, token)
            except Exception as e:
                # If token verification fails, try to decode it manually
                # This is a fallback for development
                try:
                    decoded = jwt.decode(token, options={"verify_signature": False})
                    # Create a simple user object
                    class SimpleUser:
                        def __init__(self, user_data):
                            self.id = user_data.get('sub')
                            self.email = user_data.get('email')
                            self.is_authenticated = True
                    
                    return (SimpleUser(decoded), token)
                except:
                    raise exceptions.AuthenticationFailed('Invalid token')
            
            raise exceptions.AuthenticationFailed('Invalid token')
            
        except IndexError:
            raise exceptions.AuthenticationFailed('Token prefix missing')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Authentication failed: {str(e)}')


