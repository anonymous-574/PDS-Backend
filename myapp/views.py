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

import os
import tempfile
import gdown
from transformers import BertForSequenceClassification, BertTokenizer

class default(APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        return Response({"message": "Working"}, status=status.HTTP_200_OK)
    
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





# Function to extract file ID from Google Drive link
def extract_file_id(file_link):
    """Extract the file ID from a Google Drive file link."""
    if "drive.google.com" in file_link:
        return file_link.split("/d/")[1].split("/")[0]
    raise ValueError("Invalid Google Drive file link.")

# Function to download a file to a temporary directory
def download_file_to_temp(file_url, temp_dir, filename):
    """Download a file from Google Drive into a temporary directory."""
    try:
        file_id = extract_file_id(file_url)
        download_url = f"https://drive.google.com/uc?id={file_id}"
        output_path = os.path.join(temp_dir, filename)  # Save file with the correct name
        gdown.download(download_url, output_path, quiet=False)
        print(f"Downloaded: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error downloading file: {e}")
        return None

# Google Drive file links
file_links = {
    "model.safetensors": "https://drive.google.com/file/d/1Qn_jFELPZpdxS8qf7_fUYv2tpPphR6qB/view?usp=sharing",
    "vocab.txt": "https://drive.google.com/file/d/1V864oJjOyxBnTreW-K7crQlljdsUNyo4/view?usp=sharing",
    "tokenizer_config.json": "https://drive.google.com/file/d/1ginzFZIhaffP71xy--H0Kj0h8p-aGSmV/view?usp=sharing",
    "config.json": "https://drive.google.com/file/d/1_X1VuweCAoRyu7K5qomWdjgP-urpxQ94/view?usp=sharing",
    "special_tokens_map.json": "https://drive.google.com/file/d/14NaUBLsDxxjWiRwNN6Dtz1HKlghjilY0/view?usp=sharing",
}

class InputView_Text(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "User is not authenticated."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            # Create a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                print(f"Temporary directory created at {temp_dir}")

                # Download all files to the temporary directory
                for filename, file_url in file_links.items():
                    download_file_to_temp(file_url, temp_dir, filename)

                # Verify downloaded files
                print("Downloaded files:")
                for file_name in os.listdir(temp_dir):
                    print(file_name)

                # Load the model and tokenizer from the temporary directory
                model_path = os.path.join(temp_dir, "model.safetensors")
                if not os.path.exists(model_path):
                    raise FileNotFoundError("Model file not found in temporary directory.")

                model = BertForSequenceClassification.from_pretrained(temp_dir, local_files_only=True)
                tokenizer = BertTokenizer.from_pretrained(temp_dir, local_files_only=True)

                model.eval()
                print("Successfully loaded model and tokenizer.")

                # Retrieve the latest text for the current user
                texts = Input_text.objects.order_by('-id').values_list('text', flat=True).first()
                if texts is None:
                    return Response({"error": "No text available in the database."}, status=status.HTTP_404_NOT_FOUND)

                # Tokenize the input text
                inputs = tokenizer(texts, padding="max_length", truncation=True, max_length=128, return_tensors="pt")

                # Perform inference
                with torch.no_grad():
                    outputs = model(**inputs)

                logits = outputs.logits
                predicted_class = torch.argmax(logits, dim=1).item()

                # Map predicted class to emotion label
                labels = ['sadness', 'joy', 'love', 'anger', 'fear', 'surprise']
                emotion = labels[predicted_class]

                output = {'emotion': emotion}
                return Response(output)

        except Exception as e:
            print(f"Error: {e}")
            return Response({"error": "Error loading model or processing text."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self,request):
        if not request.user.is_authenticated:
            return Response({"error": "User is not authenticated."}, status=status.HTTP_401_UNAUTHORIZED)
        serializer=InputSerializer_text(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)