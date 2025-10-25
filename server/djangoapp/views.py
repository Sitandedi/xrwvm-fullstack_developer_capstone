# Uncomment the required imports before adding the code

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import logging
import json

from .populate import initiate
from .models import CarMake, CarModel
from .restapis import get_request, analyze_review_sentiments, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.


@csrf_exempt
def login_user(request):
    """Handle user login requests."""
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']

    user = authenticate(username=username, password=password)
    data = {"userName": username}

    if user is not None:
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}

    return JsonResponse(data)


def logout_request(request):
    """Handle user logout requests."""
    logout(request)  # Terminate user session
    data = {"userName": ""}  # Return empty username
    return JsonResponse(data)


@csrf_exempt
def registration(request):
    """Handle user registration requests."""
    context = {}
    data = json.loads(request.body)

    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']

    username_exist = False

    try:
        User.objects.get(username=username)
        username_exist = True
    except User.DoesNotExist:
        logger.debug("%s is a new user", username)

    if not username_exist:
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email
        )
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
        return JsonResponse(data)

    data = {"userName": username, "error": "Already Registered"}
    return JsonResponse(data)


def get_dealerships(request, state="All"):
    """Return list of dealerships (all or by state)."""
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = f"/fetchDealers/{state}"

    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})


def get_dealer_reviews(request, dealer_id):
    """Return all reviews for a dealer."""
    if not dealer_id:
        return JsonResponse({"status": 400, "message": "Bad Request"})

    endpoint = f"/fetchReviews/dealer/{dealer_id}"
    reviews = get_request(endpoint)

    for review_detail in reviews:
        try:
            response = analyze_review_sentiments(review_detail['review'])
            if response and 'sentiment' in response:
                review_detail['sentiment'] = response['sentiment']
            else:
                review_detail['sentiment'] = 'unknown'
        except Exception:
            review_detail['sentiment'] = 'error'

    return JsonResponse({"status": 200, "reviews": reviews})


def get_dealer_details(request, dealer_id):
    """Return details for a given dealer."""
    if not dealer_id:
        return JsonResponse({"status": 400, "message": "Bad Request"})

    endpoint = f"/fetchDealer/{dealer_id}"
    dealership = get_request(endpoint)
    return JsonResponse({"status": 200, "dealer": dealership})


@csrf_exempt
def add_review(request):
    """Submit a new review for a dealer."""
    if request.user.is_anonymous:
        return JsonResponse({"status": 403, "message": "Unauthorized"})

    if request.method != "POST":
        return JsonResponse({"status": 405, "message": "Method Not Allowed"})

    try:
        data = json.loads(request.body)
        print("Received review data:", data)
    except json.JSONDecodeError:
        return JsonResponse({"status": 400, "message": "Invalid JSON"})

    try:
        response = post_review(data)
        print("Backend /insert_review response:", response)

        if response is None:
            return JsonResponse({"status": 500, "message": "No response from backend"})

        if isinstance(response, dict) and response.get("status") in ["success", "ok", 200, 201]:
            return JsonResponse({
                "status": 200,
                "message": "Review posted successfully",
                "backend_response": response
            })

        return JsonResponse({
            "status": 400,
            "message": "Backend failed to post review",
            "backend_response": response
        })

    except Exception as e:
        print("Error posting review:", str(e))
        return JsonResponse({
            "status": 500,
            "message": f"Error posting review: {str(e)}"
        })


def get_cars(request):
    """Return all cars, populating if empty."""
    count = CarMake.objects.count()
    print(count)
    if count == 0:
        initiate()

    car_models = CarModel.objects.select_related('car_make')
    cars = [
        {"CarModel": car_model.name, "CarMake": car_model.car_make.name}
        for car_model in car_models
    ]
    return JsonResponse({"CarModels": cars})
