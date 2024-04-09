from django.contrib import admin

# Register your models here.
from .models import Reviews
from .models import UsersCsfd
from .models import UsersFdb
from .models import UsersImdb
from .models import UsersRottentomatoes


admin.site.register(Reviews)
admin.site.register(UsersCsfd)
admin.site.register(UsersFdb)
admin.site.register(UsersImdb)
admin.site.register(UsersRottentomatoes)