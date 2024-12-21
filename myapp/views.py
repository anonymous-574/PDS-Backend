from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import *
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from .models import *
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import IsAuthenticated,AllowAny
import os
import torch
from transformers import BertForSequenceClassification, BertTokenizer

class user_login(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "message": "Login successful",
                "token": str(token.key)
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)

class user_signup(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username1 = request.data.get('username')
        email1 = request.data.get('email')
        password1 = request.data.get('password')
        confirm_password = request.data.get('confirm_password')

        if password1 != confirm_password:
            return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username1).exists() or User.objects.filter(email=email1).exists():
            return Response({"error": "Username or email already taken."}, status=status.HTTP_400_BAD_REQUEST)

        # Save user to Django's User model
        user = User.objects.create_user(username=username1, email=email1, password=password1)
        user.save()

        return Response({"message": "Registration successful."}, status=status.HTTP_201_CREATED)


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
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated
    def get(self,request):
        #texts = Input.objects.values_list('text', flat=True)

        if not request.user.is_authenticated:
            return Response({"error": "User is not authenticated."}, status=status.HTTP_401_UNAUTHORIZED)

        #give the latest text for currently logged in user
        #if user has many texts then give the latest one
        texts = Input_text.objects.filter(user=request.user).order_by('-id').values_list('text', flat=True).first()        
        if texts is None:
            return Response({"error": "No text available in database."}, status=status.HTTP_404_NOT_FOUND)
        emotion=predict_emotion_text(texts)
        output={'emotion' : emotion}
        return Response(output)

    def post(self,request):
        if not request.user.is_authenticated:
            return Response({"error": "User is not authenticated."}, status=status.HTTP_401_UNAUTHORIZED)
        serializer=InputSerializer_text(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)