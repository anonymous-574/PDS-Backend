# VibeBoost Backend  

The backend for **VibeBoost** is built using Django. It handles the API integrations, emotion detection model, and core logic to provide personalized recommendations based on user emotions.  

## 🌟 Features  
- Integration with the BERT-based emotion detection model to classify emotions.  
- API endpoints for:  
  - Receiving user input and detecting emotions.    
- Secure and scalable architecture to support the frontend.  

## 🛠️ Tech Stack  
- **Backend Framework**: Django  
- **Database**: SQLite (can be replaced with MySQL or PostgreSQL)  
- **ML Model**: BERT-based emotion classifier  

## 🚀 Project Structure  
```plaintext
VibeBoost-Backend/  
├── manage.py             # Django project manager  
├── VibeBoost/            # Main project directory  
│   ├── settings.py       # Project settings  
│   ├── urls.py           # Project URLs  
│   ├── wsgi.py           # WSGI configuration  
│   └── asgi.py           # ASGI configuration  
├── myapp/                # App for API endpoints  
│   ├── models.py         # Database models  
│   ├── views.py          # API views  
│   ├── urls.py           # App-specific URLs  
│   ├── serializers.py    # Data serialization  
│   └── apps.py           # App configuration   
└── README.md             # Documentation
```
## 📖 How to Run the Backend
1. Clone this repository:
   ```bash
   git clone https://github.com/anonymous-574/VibeBoost-Backend.git
   cd VibeBoost-Backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv  
   source venv/bin/activate  # For Windows: venv\Scripts\activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Apply migrations and start the server:
   ```bash
   python manage.py migrate  
   python manage.py runserver
   ```
5. Access the API at **http://127.0.0.1:8000/**.
## 📂 ML Model Files
The pretrained BERT-based model files required for emotion detection can be downloaded from the following link:
- [Emotion Detection Model](https://drive.google.com/drive/folders/17b0f3rmlguwcs95_Gw3nWqUg-1hfxSS-?usp=sharing).
  

