from rest_framework import serializers

from .models import AccessDatabase, AccessPrivilege, AccessTableData, ImportError, ImportJob


class ImportErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportError
        fields = ["id", "job", "row_number", "field_name", "error_message", "raw_value"]
        read_only_fields = ["id"]


class ImportJobSerializer(serializers.ModelSerializer):
    errors = ImportErrorSerializer(many=True, read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ImportJob
        fields = [
            "id",
            "file_name",
            "file_type",
            "target_model",
            "status",
            "total_rows",
            "success_rows",
            "error_rows",
            "error_log",
            "created_by",
            "created_by_name",
            "errors",
            "created_at",
            "completed_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "completed_at",
            "created_by",
            "status",
            "total_rows",
            "success_rows",
            "error_rows",
            "error_log",
        ]

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name()


class ImportJobListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ImportJob
        fields = [
            "id",
            "file_name",
            "file_type",
            "target_model",
            "status",
            "total_rows",
            "success_rows",
            "error_rows",
            "created_by_name",
            "created_at",
        ]

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name()


class AccessPrivilegeSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()
    granted_by_name = serializers.SerializerMethodField()

    class Meta:
        model = AccessPrivilege
        fields = [
            "id",
            "database",
            "user",
            "user_email",
            "privilege_level",
            "granted_by",
            "granted_by_name",
            "granted_at",
        ]
        read_only_fields = ["id", "granted_by", "granted_at"]

    def get_user_email(self, obj):
        return obj.user.email

    def get_granted_by_name(self, obj):
        return obj.granted_by.get_full_name()


class AccessTableDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessTableData
        fields = ["id", "database", "table_name", "row_index", "data", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def merge_rows(self, validated_data):
        return validated_data

    def sort_data(self, data, column, ascending=True):
        reverse = not ascending
        return sorted(data, key=lambda x: str(x.get("data", {}).get(column, "")), reverse=reverse)

    def filter_data(self, data, column, value):
        return [row for row in data if str(row.get("data", {}).get(column, "")).lower() == str(value).lower()]

    def find_replace(self, data, column, find, replace):
        results = []
        for row in data:
            row_copy = dict(row)
            row_data = dict(row_copy.get("data", {}))
            if column in row_data and str(find).lower() in str(row_data[column]).lower():
                row_data[column] = str(row_data[column]).replace(find, replace)
                row_copy["data"] = row_data
            results.append(row_copy)
        return results

    def fill_down(self, data, column):
        results = []
        last_value = ""
        for row in data:
            row_copy = dict(row)
            row_data = dict(row_copy.get("data", {}))
            if column in row_data:
                if row_data[column]:
                    last_value = row_data[column]
                else:
                    row_data[column] = last_value
                    row_copy["data"] = row_data
            results.append(row_copy)
        return results

    def copy_column(self, data, source_column, target_column):
        results = []
        for row in data:
            row_copy = dict(row)
            row_data = dict(row_copy.get("data", {}))
            row_data[target_column] = row_data.get(source_column, "")
            row_copy["data"] = row_data
            results.append(row_copy)
        return results


class AccessDatabaseSerializer(serializers.ModelSerializer):
    privileges = AccessPrivilegeSerializer(many=True, read_only=True)
    uploaded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = AccessDatabase
        fields = [
            "id",
            "name",
            "description",
            "file",
            "uploaded_by",
            "uploaded_by_name",
            "status",
            "total_tables",
            "total_records",
            "privileges",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "uploaded_by",
            "status",
            "total_tables",
            "total_records",
            "created_at",
            "updated_at",
        ]

    def get_uploaded_by_name(self, obj):
        return obj.uploaded_by.get_full_name()


class AccessDatabaseListSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = AccessDatabase
        fields = [
            "id",
            "name",
            "description",
            "file",
            "uploaded_by",
            "uploaded_by_name",
            "status",
            "total_tables",
            "total_records",
            "created_at",
        ]

    def get_uploaded_by_name(self, obj):
        return obj.uploaded_by.get_full_name()
