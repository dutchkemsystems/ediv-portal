from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.password_validation import validate_password
from .models import User, Privilege, RolePrivilege, Module


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'role', 'role_display',
                  'phone_number', 'is_active', 'mfa_enabled', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_role_display(self, obj):
        return obj.get_role_display()


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


class CreateSchoolStaffSerializer(serializers.Serializer):
    """Create a Principal, Vice-Principal, Teacher, or Non-Teaching staff sub-login.

    Allowed callers:
      - SYSADMIN, TG, PS  → can create any school staff, must supply school_id
      - PRI, VP           → can create teachers/non-teaching for their own school only
    """
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=20, required=False, default='')
    role = serializers.ChoiceField(
        choices=['PRI', 'VP', 'TCH', 'SA_OFF'],
        help_text='PRI, VP, TCH, or SA_OFF'
    )
    school_id = serializers.IntegerField(required=False, help_text='Required for SYSADMIN/TG/PS')

    # Optional: allow caller to set the initial password (else auto-generated)
    initial_password = serializers.CharField(max_length=128, required=False, write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value

    def validate(self, attrs):
        request = self.context['request']
        user = request.user
        role = attrs['role']

        from apps.schools.models import School

        if user.role in ('SYSADMIN', 'TG', 'PS'):
            # Admin-level caller: must provide school_id
            school_id = attrs.get('school_id')
            if not school_id:
                raise serializers.ValidationError({'school_id': 'Required for admin users.'})
            try:
                school = School.objects.get(id=school_id)
            except School.DoesNotExist:
                raise serializers.ValidationError({'school_id': 'School not found.'})
        elif user.role in ('PRI', 'VP'):
            # School-level caller: only their own school
            if role not in ('TCH', 'SA_OFF'):
                raise serializers.ValidationError(
                    {'role': 'Principals/Vice-Principals can only create Teacher or Non-Teaching accounts.'}
                )
            school = School.objects.filter(principal=user).first() or School.objects.filter(vice_principal=user).first()
            if not school:
                raise serializers.ValidationError({'school': 'You are not assigned to any school.'})
        else:
            raise PermissionDenied('You do not have permission to create staff accounts.')

        attrs['school'] = school
        return attrs

    def create(self, validated_data):
        import secrets
        school = validated_data.pop('school')
        validated_data.pop('school_id', None)

        initial_password = validated_data.pop('initial_password', None)
        temp_password = initial_password if initial_password else secrets.token_urlsafe(12)

        user = User.objects.create_user(
            email=validated_data['email'],
            password=temp_password,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=validated_data['role'],
            phone_number=validated_data.get('phone_number', ''),
        )

        from apps.staff.models import Staff
        prefix = school.code[:3]
        staff_count = Staff.objects.filter(school=school).count() + 1
        staff_id = f"{prefix}/STF/{staff_count:04d}"
        employee_number = f"EDIV/{prefix}/{staff_count:04d}"

        staff = Staff.objects.create(
            user=user,
            staff_id=staff_id,
            employee_number=employee_number,
            school=school,
            category='TEACHING' if validated_data['role'] == 'TCH' else 'ADMINISTRATIVE',
            designation=validated_data['role'],
            employment_type='PERMANENT',
            qualification='Bachelors',
            date_of_birth='2000-01-01',
            gender='M',
            marital_status='SINGLE',
            state_of_origin='Lagos',
            lga_of_origin='Lagos Island',
            residential_address='Lagos',
            emergency_contact_name='N/A',
            emergency_contact_phone='N/A',
            bank_name='N/A',
            bank_account_number='N/A',
            bank_account_name='N/A',
            date_joined='2024-01-01',
        )

        return {
            'user': user,
            'staff': staff,
            'temp_password': temp_password,
            'school': school,
        }


class DeleteSchoolStaffSerializer(serializers.Serializer):
    """Delete a school staff user account (Principal, VP, Teacher, etc.).

    Allowed callers: SYSADMIN, TG, PS only.
    """
    user_id = serializers.IntegerField()

    def validate_user_id(self, value):
        try:
            target_user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('User not found.')
        return value

    def validate(self, attrs):
        request = self.context['request']
        caller = request.user

        if caller.role not in ('SYSADMIN', 'TG', 'PS'):
            raise PermissionDenied('Only Admin/TG/PS can delete staff accounts.')

        target_user = User.objects.get(id=attrs['user_id'])

        # Cannot delete other admins
        if target_user.role in ('SYSADMIN', 'TG', 'PS'):
            raise serializers.ValidationError({'detail': 'Cannot delete admin-level accounts via this endpoint.'})

        # Cannot delete yourself
        if target_user.id == caller.id:
            raise serializers.ValidationError({'detail': 'Cannot delete your own account.'})

        attrs['target_user'] = target_user
        return attrs

    def save(self):
        target_user = self.validated_data['target_user']
        target_user.is_active = False
        target_user.save(update_fields=['is_active'])
        return target_user


class CreateStaffSerializer(serializers.Serializer):
    """Create a staff member (teaching or non-teaching) with full record."""
    # User fields
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=20, required=False, default='')

    # Staff fields
    category = serializers.ChoiceField(choices=['TEACHING', 'NON_TEACHING', 'ADMINISTRATIVE'])
    designation = serializers.ChoiceField(choices=[
        'PRINCIPAL', 'VICE_PRINCIPAL', 'HEAD_TEACHER', 'SENIOR_TEACHER', 'TEACHER',
        'LIBRARIAN', 'LABORATORY_ATTENDANT', 'BURSAR', 'SECRETARY', 'CLERK',
        'GARDENER', 'SECURITY', 'CLEANER', 'DRIVER', 'TECHNICIAN',
    ])
    employment_type = serializers.ChoiceField(choices=['PERMANENT', 'CONTRACT', 'TEMPORARY', 'VOLUNTEER'])
    qualification = serializers.ChoiceField(choices=[
        'PhD', 'Masters', 'Bachelors', 'HND', 'OND', 'NCE', 'SSCE', 'OTHER',
    ])
    date_of_birth = serializers.DateField()
    gender = serializers.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')])
    marital_status = serializers.ChoiceField(choices=['SINGLE', 'MARRIED', 'DIVORCED', 'WIDOWED'])
    state_of_origin = serializers.CharField(max_length=50)
    lga_of_origin = serializers.CharField(max_length=50)
    residential_address = serializers.CharField()
    emergency_contact_name = serializers.CharField(max_length=200)
    emergency_contact_phone = serializers.CharField(max_length=20)
    bank_name = serializers.CharField(max_length=100)
    bank_account_number = serializers.CharField(max_length=20)
    bank_account_name = serializers.CharField(max_length=200)
    date_joined = serializers.DateField()

    # Optional staff fields
    school_id = serializers.IntegerField(required=False, help_text='Required for SYSADMIN/TG/PS')
    department_id = serializers.IntegerField(required=False)
    pension_pin = serializers.CharField(max_length=20, required=False, default='')
    tax_id = serializers.CharField(max_length=20, required=False, default='')
    grade_level = serializers.CharField(max_length=20, required=False, default='')
    step = serializers.IntegerField(required=False, default=1)
    salary = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=0)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value

    def validate(self, attrs):
        request = self.context['request']
        user = request.user

        from apps.schools.models import School

        if user.role in ('SYSADMIN', 'TG', 'PS'):
            school_id = attrs.get('school_id')
            if not school_id:
                raise serializers.ValidationError({'school_id': 'Required for admin users.'})
            try:
                school = School.objects.get(id=school_id)
            except School.DoesNotExist:
                raise serializers.ValidationError({'school_id': 'School not found.'})
        else:
            school = School.objects.filter(principal=user).first() or School.objects.filter(vice_principal=user).first()
            if not school:
                raise serializers.ValidationError({'school': 'You are not assigned to any school.'})

        attrs['school'] = school
        return attrs

    def create(self, validated_data):
        import secrets
        from apps.schools.models import School
        from apps.staff.models import Staff

        school = validated_data.pop('school')
        validated_data.pop('school_id', None)

        # Create User account
        temp_password = secrets.token_urlsafe(12)
        user_role = 'TCH' if validated_data['category'] == 'TEACHING' else 'SA_OFF'

        user = User.objects.create_user(
            email=validated_data['email'],
            password=temp_password,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=user_role,
            phone_number=validated_data.get('phone_number', ''),
        )

        # Generate staff_id and employee_number
        prefix = school.code[:3]
        staff_count = Staff.objects.filter(school=school).count() + 1
        staff_id = f"{prefix}/STF/{staff_count:04d}"
        employee_number = f"EDIV/{prefix}/{staff_count:04d}"

        # Create Staff record
        staff = Staff.objects.create(
            user=user,
            staff_id=staff_id,
            employee_number=employee_number,
            school=school,
            category=validated_data['category'],
            designation=validated_data['designation'],
            employment_type=validated_data['employment_type'],
            qualification=validated_data['qualification'],
            date_of_birth=validated_data['date_of_birth'],
            gender=validated_data['gender'],
            marital_status=validated_data['marital_status'],
            state_of_origin=validated_data['state_of_origin'],
            lga_of_origin=validated_data['lga_of_origin'],
            residential_address=validated_data['residential_address'],
            emergency_contact_name=validated_data['emergency_contact_name'],
            emergency_contact_phone=validated_data['emergency_contact_phone'],
            bank_name=validated_data['bank_name'],
            bank_account_number=validated_data['bank_account_number'],
            bank_account_name=validated_data['bank_account_name'],
            date_joined=validated_data['date_joined'],
            pension_pin=validated_data.get('pension_pin', ''),
            tax_id=validated_data.get('tax_id', ''),
            grade_level=validated_data.get('grade_level', ''),
            step=validated_data.get('step', 1),
            salary=validated_data.get('salary', 0),
        )

        # Link department if provided
        dept_id = validated_data.get('department_id')
        if dept_id:
            from apps.departments.models import Department
            try:
                dept = Department.objects.get(id=dept_id)
                staff.department = dept
                staff.save(update_fields=['department'])
            except Department.DoesNotExist:
                pass

        return {
            'user': user,
            'staff': staff,
            'temp_password': temp_password,
        }


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
