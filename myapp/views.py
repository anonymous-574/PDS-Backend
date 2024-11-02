from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import *
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from .models import *
from django.conf import settings
import os
import torch
from transformers import BertForSequenceClassification, BertTokenizer

model_dir = "./ml_model"
try:
    model = BertForSequenceClassification.from_pretrained(model_dir)
    tokenizer = BertTokenizer.from_pretrained(model_dir)
    model.eval()
    print("Success In loading model")
except Exception as e:
    model, tokenizer = None, None
    print(f"Error loading model or tokenizer: {e}")


def predict_emotion_text(text):
    inputs = tokenizer(text, padding="max_length", truncation=True, max_length=128, return_tensors="pt")  
    with torch.no_grad():
        outputs = model(**inputs)  
    logits = outputs.logits  
    predicted_class = torch.argmax(logits, dim=1).item()    
    labels = ['sadness', 'joy', 'love', 'anger', 'fear', 'surprise'] 
    predicted_label = labels[predicted_class]
    return predicted_label

class InputView_Text(APIView):
    def get(self,request):
        #texts = Input.objects.values_list('text', flat=True)

        #give the latest text
        texts = Input_text.objects.order_by('-id').values_list('text', flat=True).first()
        if texts is None:
            return Response({"error": "No text available in database."}, status=status.HTTP_404_NOT_FOUND)
        emotion=predict_emotion_text(texts)
        output={'emotion' : emotion}
        return Response(output)

    def post(self,request):
        serializer=InputSerializer_text(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



import numpy as np
import cv2
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import Image
from io import BytesIO


try:
    model2 = load_model('./ml_model/final_model.h5')
except Exception as e:
    print(f"Error in Loading {e}")


def predict_emotion_img(image):
    img = Image.open(BytesIO(image)).convert('L')
    img = img.resize((48, 48))   
    img = img_to_array(img) / 255.0
    img = np.expand_dims(img, axis=0)  
    prediction = model2.predict(img)
    predicted_class = np.argmax(prediction, axis=1)[0]
    class_labels = ['angry','disgust','fear','happy','neutral','sad','surprise']

    return class_labels[predicted_class]

class InputView_Image(APIView):
    def get(self,request):
        #give the latest image
        latest_image = Input_image.objects.latest('id')
        image_data = latest_image.image.read()
        if image_data is None:
            return Response({"error": "No image available in database."}, status=status.HTTP_404_NOT_FOUND)
        emotion = predict_emotion_img(image_data)
        output={'emotion' : emotion}
        return Response(output)
    
    def post(self , request):
        serializer=InputSerializer_image(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

