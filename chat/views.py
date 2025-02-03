from django.db.models import Q
from django.shortcuts import render, redirect
from .models import ChatRoom, Message
from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import json
from django.http import JsonResponse
import textwrap
from django.contrib.auth.models import User


def get_chatrooms_with_last_message(user):
    chat_rooms = ChatRoom.objects.filter(Q(creator=user) | Q(users=user))
    chat_rooms_with_last_message = []

    for room in chat_rooms:
        last_message = Message.objects.filter(chatroom=room).order_by('-timestamp').first()

        chat_rooms_with_last_message.append({
            'id': room.id,
            'room_name': room.name,
            'last_message': {
                'message': last_message.message if last_message else None,
                'timestamp': last_message.timestamp if last_message else None,
                'sender': last_message.sender.username if last_message and last_message.sender else None
            }
        })

    return chat_rooms_with_last_message

# Create your views here.
def index(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    chat_rooms = get_chatrooms_with_last_message(user)
    
    return render(request, 'index.html', context={'chat_rooms': chat_rooms, 'users': User.objects.exclude(id=user.id)})


def create_room(request):
    if request.method == 'POST':
        room_name = request.POST.get('roomName')
        selected_users = request.POST.getlist('users')  # Get list of users selected for the room

        chatroom, created = ChatRoom.objects.get_or_create(name=room_name, creator=request.user)

        # Add users to the room
        for user_id in selected_users:
            user = User.objects.get(id=user_id)
            chatroom.users.add(user)

        chatroom.save()

        return redirect('home')


def room(request, room_name):
    chatroom = ChatRoom.objects.filter(name=room_name).first()

    if not chatroom:
        return redirect('home')

    # Only allow access if the user created the room or is assigned to it
    if chatroom.creator != request.user and request.user not in chatroom.users.all():
        return redirect('home')  # Optionally show an error message

    chat_messages = Message.objects.filter(chatroom=chatroom)

    context = {
        'room_name': room_name,
        'chatroom': chatroom,
        'chat_messages': chat_messages,
        'current_user': request.user.username
    }

    return render(request, 'chat_room.html', context)



from django.http import HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO
from .models import Message  # Import the Message model
from django.utils import timezone

def generate_pdf(request, chatroom_id):
    # Fetch all messages for a specific chatroom
    messages = Message.objects.filter(chatroom_id=chatroom_id).order_by('timestamp')
    
    room_name = f"Chatroom {chatroom_id}"  # You can use the chatroom's name if you'd like
    
    # Create a PDF in memory
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    # Set up page
    p.setFont("Helvetica", 10)
    y_position = 800  # Starting Y position on the PDF page

    # Add title to the PDF
    p.drawString(100, y_position, f"Chat History - {room_name}")
    y_position -= 20  # Adjust space for title

    # Add the chat messages to the PDF
    for message in messages:
        sender = message.sender.username
        content = message.message
        timestamp = message.timestamp.strftime('%Y-%m-%d %H:%M:%S')  # Format the timestamp
        
        # Add each message to the PDF
        p.drawString(100, y_position, f"{timestamp} - {sender}: {content}")
        y_position -= 20  # Move down for the next message


        if message.image:
            image_path = message.image.path  # Get the file path of the image
            
            # Add the image to the PDF
            try:
                p.drawImage(image_path, 100, y_position - 100, width=150, height=150, preserveAspectRatio=True, anchor='c')
                y_position -= 160  # Move down after adding the image
            except Exception as e:
                p.drawString(100, y_position, "[Image could not be loaded]")
                y_position -= 20  # Move down if the image fails to load

        # Check if the page is full and add a new page if necessary
        if y_position < 40:
            p.showPage()  # Create a new page in the PDF
            p.setFont("Helvetica", 10)  # Reset font for new page
            y_position = 800  # Reset Y position

    # Save the PDF
    p.showPage()
    p.save()

    # Return the PDF as a response
    buffer.seek(0)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="chat_history_{chatroom_id}.pdf"'
    response.write(buffer.read())
    return response

from django.shortcuts import render
from django.http import JsonResponse
from .models import Message, ChatRoom
from django.contrib.auth.decorators import login_required

@login_required
def upload_image(request):
    print('FILES:', request.FILES)
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES.get('image')
        receiver = request.POST.get('receiver')

        try:
            receiver = User.objects.get(id=receiver)
            # Create a message and save the image
            message = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                message="Image uploaded",
                image=image
            )

            return JsonResponse({'image_url': message.image.url, 'message_id': message.id})
        except User.DoesNotExist:
            return JsonResponse({'error': 'Receiver not found'}, status=404)

    return JsonResponse({'error': 'No image uploaded'}, status=400)