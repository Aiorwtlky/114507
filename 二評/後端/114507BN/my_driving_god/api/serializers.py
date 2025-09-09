from rest_framework import serializers
from .models import Personnel

class PersonnelSerializer(serializers.ModelSerializer):
    """
    這個 Serializer 會將 Personnel 模型物件轉換成 JSON 格式。
    """
    class Meta:
        model = Personnel
        fields = ['personnel_id', 'personnel_number', 'name', 'email', 'gender', 'license_number', 'is_active']