from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=200)
    phone_number = serializers.CharField(max_length=13)
    first_name = serializers.CharField(max_length=200)
    last_name = serializers.CharField(max_length=200)

    class Meta:
        model = Profile
        exclude = ['packages', 'user']

    def update(self, instance, validated_data):
        instance = super().update(instance=instance, validated_data=validated_data)
        instance.user.phone_number = validated_data.get('phone_number', instance.user.phone_number)
        instance.user.email = validated_data.get('email', instance.user.email)
        instance.user.first_name = validated_data.get('first_name', instance.user.first_name)
        instance.user.last_name = validated_data.get('last_name', instance.user.last_name)
        return instance.save()
