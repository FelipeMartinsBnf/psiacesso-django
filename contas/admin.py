from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Adicionamos o campo 'role' aos fieldsets do UserAdmin para que ele
# apareça na tela de criação e edição de usuários no admin.
# A sintaxe 'UserAdmin.fieldsets + (...)' adiciona nosso novo fieldset.
UserAdmin.fieldsets += (
    ('Campos Customizados', {'fields': ('role',)}),
)