from django.shortcuts import render


def index(request):
    return render(request, "chrome/index.html")


def room(request, room_name):
    # Assuming 'room_name' from the URL is actually the user's email
    user_email = room_name
    return render(request, "chrome/room.html", {"user_email": user_email})
