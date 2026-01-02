from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """
    Custom authentication backend that allows users to login with either
    their email address or username.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user with email or username.
        
        Args:
            username: Can be either email or username
            password: User's password
        
        Returns:
            User object if authentication succeeds, None otherwise
        """
        if username is None or password is None:
            return None
        
        try:
            # Try to fetch user by email or username
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
            
            # Check password
            if user.check_password(password):
                return user
                
        except User.DoesNotExist:
            # Run the default password hasher once to reduce timing
            # difference between existing and non-existing users
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # This shouldn't happen if email is unique, but handle it
            return None
        
        return None
    
    def get_user(self, user_id):
        """
        Get user by ID.
        Required by Django's authentication system.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
