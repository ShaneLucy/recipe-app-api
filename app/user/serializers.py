from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 5
            }
        }

    def create(self, validated_data):
        """Create a new user with encypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)


class AuthTokenSerializer(serializers.Serializer):
    """Serialiser for the user authentication object"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    # validating inputs, 'attributes' are passed from serializer
    def validate(self, attributes):
        """Validate and authenticate the user"""
        email = attributes.get('email')
        password = attributes.get('password')
        # perform validation
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        # if validation fails raise an exception
        if not user:
            message = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(message, code='authentication')

        # if validation passes return the authenticated user
        attributes['user'] = user
        return attributes
