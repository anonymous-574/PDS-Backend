from rest_framework import serializers
from .models import *
#serialiser converts the response to json (which react can read)

class InputSerializer_text(serializers.ModelSerializer):
    class Meta:
        model=Input_text
        fields=['text']

class InputSerializer_image(serializers.ModelSerializer):
    class Meta:
        model=Input_image
        fields=['image']
