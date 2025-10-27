from rest_framework import serializers
from shifts.models import (
    Center, Month, Shift
)


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
        

class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = '__all__'