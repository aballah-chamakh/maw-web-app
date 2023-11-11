from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):

        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email,username, password):

        user = self.create_user(
            email,
            username=username,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email,username, password):

        user = self.create_user(
            email,
            username=username,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    email = models.EmailField(
            verbose_name='email address',
            max_length=255,
            unique=True,
        )
    username = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    class Meta:
        ordering = ['id']

    def get_full_name(self):

        return self.username

    def get_short_name(self):

        return self.username

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):

        return True

    def has_module_perms(self, app_label):

        return True

    @property
    def is_staff(self):

        return self.staff

    @property
    def is_admin(self):

        return self.admin

    @property
    def is_active(self):

        return self.active



class CompanyProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    logo = models.ImageField(default='company_logos/logo_2.png',upload_to='company_logos/')
    api_base_url = models.URLField(max_length=100)
    api_key = models.CharField(max_length=100)
    loading_state = models.ForeignKey('CompanyOrderState',on_delete=models.SET_NULL,related_name='company_order_loading_state',null=True)
    post_submit_state = models.ForeignKey('CompanyOrderState',on_delete=models.SET_NULL,related_name='company_order_post_submit_state',null=True)
    
    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"company : {self.user.username}"

class CompanyOrderState(models.Model):
    company = models.ForeignKey(CompanyProfile,on_delete=models.CASCADE)
    state_id = models.IntegerField()
    state_name = models.CharField(max_length=100)

    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"company => state_name : {self.company.user.username} state_id : {self.state_id}" 
    
