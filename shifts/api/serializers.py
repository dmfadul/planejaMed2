from rest_framework import serializers
from shifts.models import Center, Month


class CenterSerializer(serializers.ModelSerializer):
    abbr = serializers.CharField(source='abbreviation')

    class Meta:
        model = Center
        # fields = ['id', 'name', 'abbr', 'hospital', 'is_active']
        fields = ['abbr']


class MonthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Month
        fields = '__all__'