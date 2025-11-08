# 🤝 Roamio × Ralendar Integration Guide

> **For Ralendar Team**  
> This document outlines the integration requirements between Roamio (travel journal platform) and Ralendar (calendar & reminder system).

---

## 📋 Table of Contents

1. [Integration Overview](#integration-overview)
2. [Authentication & User System](#authentication--user-system)
3. [API Endpoints Required](#api-endpoints-required)
4. [Data Models](#data-models)
5. [Integration Flow](#integration-flow)
6. [Security & Best Practices](#security--best-practices)
7. [Testing & Deployment](#testing--deployment)

---

## 🎯 Integration Overview

### What Roamio Does
- Records travel events (景点、餐厅、活动等)
- Manages event details (time, location, description)
- Stores event data in database

### What Ralendar Does
- Displays events on calendar
- Sends email reminders
- Provides map navigation (Baidu Maps integration)

### Integration Points
```
Roamio (Event Creation) 
    ↓
    API Call → Ralendar (Create Calendar Event + Set Reminder)
    ↓
Ralendar (Email Notification at scheduled time)
```

---

## 🔐 Authentication & User System

### Shared Database Strategy

Both systems share the **same PostgreSQL database** for user authentication:

```python
# Database Configuration (Both Projects)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'roamio_db',
        'USER': 'roamio_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Shared SECRET_KEY

**CRITICAL**: Both projects must use the **same `SECRET_KEY`** for JWT tokens to work across systems.

```python
# settings.py (Both Roamio & Ralendar)
SECRET_KEY = 'your-shared-secret-key-here'  # MUST BE IDENTICAL
```

### JWT Token Authentication

Users log in once (via Roamio or Ralendar), and the JWT token works for both systems:

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Token Payload:**
```json
{
  "user_id": 123,
  "username": "traveler",
  "email": "user@example.com",
  "exp": 1699999999
}
```

---

## 🔌 API Endpoints Required

### 1. Create Event in Ralendar

**Endpoint:** `POST /api/v1/events/`

**Request Headers:**
```http
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Visit Eiffel Tower",
  "description": "Romantic evening at the Eiffel Tower",
  "start_time": "2025-12-25T18:00:00Z",
  "end_time": "2025-12-25T20:00:00Z",
  "location": {
    "name": "Eiffel Tower",
    "address": "Champ de Mars, 5 Avenue Anatole France, 75007 Paris",
    "latitude": 48.8584,
    "longitude": 2.2945
  },
  "reminder": {
    "enabled": true,
    "minutes_before": 60,
    "email": "user@example.com"
  },
  "source_app": "roamio",
  "source_event_id": 456
}
```

**Response (Success - 201 Created):**
```json
{
  "id": 789,
  "title": "Visit Eiffel Tower",
  "start_time": "2025-12-25T18:00:00Z",
  "end_time": "2025-12-25T20:00:00Z",
  "location": {
    "name": "Eiffel Tower",
    "latitude": 48.8584,
    "longitude": 2.2945
  },
  "reminder_scheduled": true,
  "calendar_url": "https://ralendar.com/calendar?event_id=789",
  "map_url": "https://ralendar.com/map?event_id=789",
  "created_at": "2025-11-08T12:00:00Z"
}
```

**Response (Error - 400 Bad Request):**
```json
{
  "error": "Invalid time format",
  "detail": "start_time must be in ISO 8601 format"
}
```

---

### 2. Update Event in Ralendar

**Endpoint:** `PATCH /api/v1/events/{event_id}/`

**Request:**
```json
{
  "title": "Updated: Visit Eiffel Tower at Night",
  "start_time": "2025-12-25T20:00:00Z"
}
```

**Response (200 OK):**
```json
{
  "id": 789,
  "title": "Updated: Visit Eiffel Tower at Night",
  "start_time": "2025-12-25T20:00:00Z",
  "reminder_rescheduled": true
}
```

---

### 3. Delete Event in Ralendar

**Endpoint:** `DELETE /api/v1/events/{event_id}/`

**Response (204 No Content):**
```
(Empty response body)
```

---

### 4. Get Event Details

**Endpoint:** `GET /api/v1/events/{event_id}/`

**Response (200 OK):**
```json
{
  "id": 789,
  "title": "Visit Eiffel Tower",
  "start_time": "2025-12-25T18:00:00Z",
  "end_time": "2025-12-25T20:00:00Z",
  "location": {
    "name": "Eiffel Tower",
    "latitude": 48.8584,
    "longitude": 2.2945
  },
  "reminder": {
    "enabled": true,
    "scheduled_time": "2025-12-25T17:00:00Z",
    "sent": false
  }
}
```

---

## 📊 Data Models

### Roamio: TripEvent Model

```python
class TripEvent(models.Model):
    trip = models.ForeignKey('Trip', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Basic Info
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Time
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    
    # Location
    location_name = models.CharField(max_length=200, blank=True)
    location_address = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    
    # Reminder
    reminder_enabled = models.BooleanField(default=False)
    reminder_minutes_before = models.IntegerField(default=60)
    
    # Integration
    source_app = models.CharField(max_length=50, default='roamio')
    ralendar_event_id = models.IntegerField(null=True, blank=True)
    synced_to_ralendar = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Ralendar: Event Model (Expected)

```python
class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Basic Info
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Time
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    
    # Location
    location_name = models.CharField(max_length=200, blank=True)
    location_address = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    
    # Reminder
    reminder_enabled = models.BooleanField(default=False)
    reminder_minutes_before = models.IntegerField(default=60)
    reminder_sent = models.BooleanField(default=False)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Source Tracking
    source_app = models.CharField(max_length=50, default='ralendar')
    source_event_id = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

---

## 🔄 Integration Flow

### Scenario 1: User Creates Event in Roamio

```mermaid
sequenceDiagram
    participant User
    participant Roamio
    participant RalendarAPI
    participant Celery
    participant Email

    User->>Roamio: Create event (with reminder)
    Roamio->>Roamio: Save to database
    Roamio->>RalendarAPI: POST /api/v1/events/
    RalendarAPI->>RalendarAPI: Create event
    RalendarAPI->>Celery: Schedule reminder task
    RalendarAPI-->>Roamio: Return event_id
    Roamio->>Roamio: Save ralendar_event_id
    Roamio-->>User: Event created ✓
    
    Note over Celery: Wait until reminder time
    
    Celery->>Email: Send reminder email
    Email-->>User: 📧 Reminder: Visit Eiffel Tower in 1 hour
```

### Scenario 2: User Updates Event in Roamio

```mermaid
sequenceDiagram
    participant User
    participant Roamio
    participant RalendarAPI
    participant Celery

    User->>Roamio: Update event time
    Roamio->>Roamio: Update database
    Roamio->>RalendarAPI: PATCH /api/v1/events/{id}/
    RalendarAPI->>RalendarAPI: Update event
    RalendarAPI->>Celery: Reschedule reminder
    RalendarAPI-->>Roamio: Updated ✓
    Roamio-->>User: Event updated ✓
```

### Scenario 3: User Deletes Event in Roamio

```mermaid
sequenceDiagram
    participant User
    participant Roamio
    participant RalendarAPI
    participant Celery

    User->>Roamio: Delete event
    Roamio->>RalendarAPI: DELETE /api/v1/events/{id}/
    RalendarAPI->>Celery: Cancel reminder task
    RalendarAPI->>RalendarAPI: Delete event
    RalendarAPI-->>Roamio: Deleted ✓
    Roamio->>Roamio: Delete from database
    Roamio-->>User: Event deleted ✓
```

---

## 🛡️ Security & Best Practices

### 1. CORS Configuration

Ralendar must allow requests from Roamio:

```python
# settings.py (Ralendar)
CORS_ALLOWED_ORIGINS = [
    'https://app7508.acapp.acwing.com.cn',  # Roamio production
    'http://localhost:8080',                 # Roamio development
]

CORS_ALLOW_CREDENTIALS = True
```

### 2. JWT Token Validation

```python
# Ralendar API View
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class EventViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def create(self, request):
        # request.user is automatically authenticated
        event = Event.objects.create(
            user=request.user,
            **request.data
        )
        return Response(...)
```

### 3. Rate Limiting

Protect your API from abuse:

```python
# settings.py (Ralendar)
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '100/hour',  # 100 requests per hour per user
    }
}
```

### 4. Error Handling

Always return meaningful error messages:

```python
# Bad ❌
return Response({"error": "Error"}, status=400)

# Good ✅
return Response({
    "error": "Invalid time range",
    "detail": "end_time must be after start_time",
    "field": "end_time"
}, status=400)
```

---

## 🧪 Testing & Deployment

### Testing Checklist

- [ ] **Authentication**: JWT tokens work across both systems
- [ ] **Create Event**: Roamio can create events in Ralendar
- [ ] **Update Event**: Time changes trigger reminder rescheduling
- [ ] **Delete Event**: Reminders are properly canceled
- [ ] **Email Delivery**: Reminders are sent at correct time
- [ ] **Map Integration**: Location data is correctly passed
- [ ] **Error Handling**: Invalid requests return proper error messages
- [ ] **Rate Limiting**: API throttling works as expected

### Test API Endpoints

Use this script to test Ralendar API:

```bash
#!/bin/bash

# 1. Get JWT token (login)
TOKEN=$(curl -X POST https://ralendar.com/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}' \
  | jq -r '.access')

# 2. Create event
curl -X POST https://ralendar.com/api/v1/events/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Event",
    "start_time": "2025-12-25T18:00:00Z",
    "reminder": {
      "enabled": true,
      "minutes_before": 60
    }
  }'

# 3. Get event
curl -X GET https://ralendar.com/api/v1/events/1/ \
  -H "Authorization: Bearer $TOKEN"

# 4. Update event
curl -X PATCH https://ralendar.com/api/v1/events/1/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Test Event"}'

# 5. Delete event
curl -X DELETE https://ralendar.com/api/v1/events/1/ \
  -H "Authorization: Bearer $TOKEN"
```

### Deployment Steps

1. **Database Migration**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Collect Static Files**
   ```bash
   python manage.py collectstatic --noinput
   ```

3. **Start Celery Worker** (for reminders)
   ```bash
   celery -A ralendar worker -l info
   celery -A ralendar beat -l info  # Scheduler
   ```

4. **Configure Nginx**
   ```nginx
   server {
       listen 80;
       server_name ralendar.com;
       
       location /api/ {
           proxy_pass http://127.0.0.1:8001;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

5. **Test Integration**
   - Create test event in Roamio
   - Verify event appears in Ralendar
   - Wait for reminder time
   - Confirm email is sent

---

## 📞 Contact & Support

### Roamio Team
- **Backend Lead**: [Your Name]
- **Email**: roamio@example.com
- **GitHub**: https://github.com/ppshuX/roamio

### API Documentation
- **Roamio API Docs**: https://app7508.acapp.acwing.com.cn/api/docs/
- **Ralendar API Docs**: (To be provided by Ralendar team)

### Communication
- **Slack Channel**: #roamio-ralendar-integration
- **Weekly Sync**: Every Monday 10:00 AM

---

## 📝 Appendix

### A. Email Template for Reminders

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Event Reminder</title>
</head>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto;">
        <h2 style="color: #4CAF50;">📅 Event Reminder</h2>
        
        <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="margin-top: 0;">{{ event.title }}</h3>
            <p><strong>Time:</strong> {{ event.start_time|date:"Y-m-d H:i" }}</p>
            <p><strong>Location:</strong> {{ event.location_name }}</p>
            <p><strong>Description:</strong> {{ event.description }}</p>
        </div>
        
        <div style="margin: 20px 0;">
            <a href="{{ calendar_url }}" 
               style="background: #4CAF50; color: white; padding: 12px 24px; 
                      text-decoration: none; border-radius: 4px; display: inline-block;">
                View in Calendar
            </a>
            
            <a href="{{ map_url }}" 
               style="background: #2196F3; color: white; padding: 12px 24px; 
                      text-decoration: none; border-radius: 4px; display: inline-block; 
                      margin-left: 10px;">
                Navigate
            </a>
        </div>
        
        <p style="color: #666; font-size: 12px; margin-top: 30px;">
            This reminder was sent by Ralendar on behalf of Roamio.
        </p>
    </div>
</body>
</html>
```

### B. Baidu Maps Integration

```javascript
// Frontend: Open Baidu Maps for navigation
function navigateToLocation(latitude, longitude, locationName) {
  const baiduUrl = `https://api.map.baidu.com/marker?location=${latitude},${longitude}&title=${encodeURIComponent(locationName)}&content=Event Location&output=html&src=roamio`;
  window.open(baiduUrl, '_blank');
}
```

### C. Celery Task Example

```python
# tasks.py (Ralendar)
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import Event

@shared_task
def send_event_reminder(event_id):
    """Send email reminder for an event"""
    try:
        event = Event.objects.get(id=event_id)
        
        # Check if already sent
        if event.reminder_sent:
            return f"Reminder already sent for event {event_id}"
        
        # Send email
        send_mail(
            subject=f'Reminder: {event.title}',
            message=f'Your event "{event.title}" starts at {event.start_time}',
            from_email='noreply@ralendar.com',
            recipient_list=[event.user.email],
            html_message=render_reminder_email(event),
        )
        
        # Mark as sent
        event.reminder_sent = True
        event.reminder_sent_at = timezone.now()
        event.save()
        
        return f"Reminder sent for event {event_id}"
        
    except Event.DoesNotExist:
        return f"Event {event_id} not found"

def schedule_reminder(event):
    """Schedule a reminder task"""
    reminder_time = event.start_time - timedelta(minutes=event.reminder_minutes_before)
    send_event_reminder.apply_async((event.id,), eta=reminder_time)
```

---

## ✅ Quick Start Summary

1. **Setup shared database** with same credentials
2. **Use same SECRET_KEY** in both projects
3. **Implement 4 API endpoints**: Create, Update, Delete, Get
4. **Configure CORS** to allow Roamio domain
5. **Setup Celery** for reminder scheduling
6. **Test integration** with provided scripts
7. **Deploy and monitor** 🚀

---

**Last Updated**: 2025-11-08  
**Version**: 1.0  
**Status**: Ready for Implementation ✅

