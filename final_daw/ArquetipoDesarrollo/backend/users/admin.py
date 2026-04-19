from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = ('email', 'nombre', 'is_staff', 'is_active')
    
    fieldsets = (
        ('Usuario y Constraseña', {
            'fields': ('email', 'password')
        }),
        ('Información Personal', {
            'fields': ('nombre', 'apellidos', 'foto_perfil')
        }),
        ('Estado y Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    #Hago que las fechas solo sean de lectura
    readonly_fields = ('last_login', 'date_joined')