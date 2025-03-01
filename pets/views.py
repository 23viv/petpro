from django.shortcuts import render, redirect
from django.http import JsonResponse
from pymongo import MongoClient
from groq import Groq
from django.conf import settings  
from langchain.prompts import PromptTemplate

# MongoDB setup
client = MongoClient()
db = client['Userdata']
users_collection = db['users']
pets_collection = db['pets']
chat_history_collection = db['chat_history']

# Initialize Groq client with API key
groq_client = Groq(api_key=settings.GROQ_API_KEY)  
groq_client1 = Groq(api_key=settings.GROQ_API_KEY1)

# Home View
def home(request):
    if 'user' not in request.session:
        return redirect('login')

    username = request.session['user']
    return render(request, "home.html", {"username": username})

# Welcome View
def welcome(request):
    return render(request, "welcome.html")

# Signup View
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        # Check if user exists
        if users_collection.find_one({"email": email}):
            return JsonResponse({"error": "User already exists! Please log in."})

        # Save new user
        users_collection.insert_one({"username": username, "email": email, "password": password})
        return redirect('login')

    return render(request, 'signup.html')

# Login View
def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Authenticate user
        user = users_collection.find_one({"email": email, "password": password})
        if user:
            request.session['user'] = user['username']
            return redirect('home')
        else:
            return JsonResponse({"error": "Invalid email or password."})

    return render(request, 'login.html')

# Chatbot View
def chatbot(request):
    if 'user' not in request.session:
        return redirect('login')

    username = request.session['user']
    user_pets = list(pets_collection.find({"owner": username}))
    chat_history = list(chat_history_collection.find({"username": username}))

    # Pet info for context
    pet_info = ""
    if user_pets:
        pet_names = ', '.join([pet['petname'] for pet in user_pets])
        pet_breeds = ', '.join([pet['breed'] for pet in user_pets if pet.get('breed')])
        pet_info = f"User has pets: {pet_names}. Breeds: {pet_breeds if pet_breeds else 'Unknown breeds'}."

    if request.method == 'POST':
        user_message = request.POST['message']

        # API request to Groq's model
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Act as a friendly and knowledgeable veterinarian and be clear with informations"},
                {"role": "system", "content": pet_info},
                {"role": "user", "content": user_message},
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1
        )

        ai_response = completion.choices[0].message.content
        chat_entry = {"username": username, "user_message": user_message, "vet_response": ai_response}
        chat_history_collection.insert_one(chat_entry)
        chat_history.append(chat_entry)

    return render(request, "chatbot.html", {"username": username, "chat_history": chat_history})

# Pet Profile View
def pet_profile(request):
    if 'user' not in request.session:
        return redirect('login')

    username = request.session['user']
    user_pets = list(pets_collection.find({"owner": username}, {"_id": 0, "petname": 1, "pet_type": 1, "breed": 1, "age": 1}))

    if request.method == "POST":
        petname = request.POST.get("petname")
        pet_type = request.POST.get("pet_type")
        breed = request.POST.get("breed")
        age = request.POST.get("age")

        if petname and pet_type and age:
            pets_collection.insert_one({
                "owner": username,
                "petname": petname,
                "pet_type": pet_type,
                "breed": breed if breed else "Unknown",
                "age": int(age)
            })
            return redirect('pet_profile')

    return render(request, "pet_profile.html", {
        "username": username,
        "user_pets": user_pets
    })

# Function to generate diet plan using Groq API
def generate_diet_plan(pet_type, breed, age, weight, health_condition):
    # Define a structured prompt template
    prompt = PromptTemplate(
        input_variables=["pet_type", "breed", "age", "weight", "health_condition"],
        template=(
            "You are an expert pet nutritionist. Generate a complete daily diet plan for a {pet_type} of breed {breed}, "
            "age {age} years, weighing {weight} kg, with the following health conditions: {health_condition}. "
            "Include meal times, portion sizes, and a breakdown of nutritional values."
        )
    )

    # Format the prompt
    formatted_prompt = prompt.format(
        pet_type=pet_type, breed=breed, age=age, weight=weight, health_condition=health_condition
    )

    # Use Groq API for response
    completion = groq_client1.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an expert pet nutritionist. When generating a pet diet plan, structure the output with 'Daily Calorie Needs' on the first line, followed by separate lines for Protein, Fats, Carbohydrates, Vitamins and Minerals, Water, and Exercise. At the end, provide a list of specific food ingredients with quantities to meet these nutritional needs."},
            {"role": "user", "content": formatted_prompt}
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1
    )

    return completion.choices[0].message.content  # Extract response content

# Django view to handle diet plan generation
def diet_view(request):
    if request.method == "POST":
        pet_type = request.POST.get("pet_type")
        breed = request.POST.get("breed")
        age = request.POST.get("age")
        weight = request.POST.get("weight")
        health_condition = request.POST.get("health_condition", "None")

        # Generate AI-based diet plan
        diet_plan = generate_diet_plan(pet_type, breed, age, weight, health_condition)

        return JsonResponse({"diet_plan": diet_plan})

    return render(request, "diet_plan.html")
