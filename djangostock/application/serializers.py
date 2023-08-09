from rest_framework import serializers

from .models import User, Currency, Country, Stock


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        read_only_fields = ["id", "last_login", "is_admin", "is_active", "create_date", "modify_date"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, user, validated_data):
        user.first_name = validated_data.get("first_name", user.first_name)
        user.last_name = validated_data.get("last_name", user.last_name)
        if "password" in validated_data:
            user.set_password(validated_data.get("password"))
        user.save()
        return user


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = "__all__"


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"


class StockSerializer(serializers.ModelSerializer):
    exchange = serializers.CharField(source="exchange_name")
    type = serializers.CharField(source="type_of_stock")

    currency = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Currency.objects.all(),
    )
    country = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Country.objects.all(),
    )

    class Meta:
        model = Stock
        fields = [
            "name",
            "symbol",
            "last_update_date",
            "exchange",
            "type",
            "currency",
            "country",
        ]
