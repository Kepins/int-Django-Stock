from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        user = self.model(email=BaseUserManager.normalize_email(email), first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, first_name, last_name, password=None):
        user = self.create_user(email, first_name, last_name, password)
        user.is_admin = True
        user.save()
        return user
