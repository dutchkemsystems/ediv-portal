from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Privilege, RolePrivilege, Module


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'role',
                  'phone_number', 'is_active', 'mfa_enabled', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return obj.get_full_name()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'phone_number', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': 'Passwords do not match.'})
        return attrs


class MFAEnableSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)


class MFALoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    mfa_code = serializers.CharField(max_length=6)


class MFAVerifySerializer(serializers.Serializer):
    temp_token = serializers.CharField()
    mfa_code = serializers.CharField(max_length=6)


class PrivilegeSerializer(serializers.ModelSerializer):
    role_display = serializers.SerializerMethodField()
    module_display = serializers.SerializerMethodField()

    class Meta:
        model = Privilege
        fields = ['id', 'role', 'role_display', 'module', 'module_display',
                  'can_view', 'can_create', 'can_edit', 'can_delete', 'can_approve', 'can_export',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_role_display(self, obj):
        return dict(User.Role.choices).get(obj.role, obj.role)

    def get_module_display(self, obj):
        return dict(Module.choices).get(obj.module, obj.module)


class PrivilegeListSerializer(serializers.ModelSerializer):
    role_display = serializers.SerializerMethodField()
    module_display = serializers.SerializerMethodField()

    class Meta:
        model = Privilege
        fields = ['id', 'role', 'role_display', 'module', 'module_display',
                  'can_view', 'can_create', 'can_edit', 'can_delete']

    def get_role_display(self, obj):
        return dict(User.Role.choices).get(obj.role, obj.role)

    def get_module_display(self, obj):
        return dict(Module.choices).get(obj.module, obj.module)


class RolePrivilegeSerializer(serializers.ModelSerializer):
    role_display = serializers.SerializerMethodField()
    privileges = serializers.SerializerMethodField()

    class Meta:
        model = RolePrivilege
        fields = ['id', 'role', 'role_display', 'description', 'privileges', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_role_display(self, obj):
        return dict(User.Role.choices).get(obj.role, obj.role)

    def get_privileges(self, obj):
        privileges = Privilege.objects.filter(role=obj.role)
        return PrivilegeSerializer(privileges, many=True).data
