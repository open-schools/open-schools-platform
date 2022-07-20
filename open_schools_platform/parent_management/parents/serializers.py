from rest_framework import serializers

from open_schools_platform.parent_management.parents.models import ParentProfile


class ParentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentProfile
        fields = ('id', 'name', 'user')
