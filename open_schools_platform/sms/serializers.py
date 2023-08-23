from rest_framework import serializers


class BaseSmsSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["ok", "ok/error"], required=True)


class ChildBalanceSmsSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["RUB", "SMS"])
    balance = serializers.IntegerField()
    credit = serializers.IntegerField()


class BalanceSmsSerializer(BaseSmsSerializer):
    balance = serializers.ListField(child=ChildBalanceSmsSerializer())


class ChildMessageSmsSerializer(serializers.Serializer):
    client_id = serializers.CharField()
    smsc_id = serializers.IntegerField()
    status = serializers.CharField()
    msg_cost = serializers.FloatField()
    sms_count = serializers.IntegerField()


class MessageSmsSerializer(BaseSmsSerializer):
    messages = serializers.ListField(child=ChildMessageSmsSerializer())
