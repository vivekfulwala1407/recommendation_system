# Django Recommendation System

A Django-based social media platform with intelligent post recommendation system using Computer Vision (ViT) and personalized feed algorithms.

## Features

- **User Authentication**: Signup, signin, password reset
- **AI-Powered Image Recognition**: Automatic categorization using Vision Transformer (ViT)
- **Smart Recommendations**: Personalized feed based on user interactions
- **Category Mapping**: Pizza, coffee → food; cars, bikes → vehicles; etc.
- **Interaction Tracking**: Like, comment, share functionality
- **Dual Database**: MySQL for user data, MongoDB for post metadata

## Prerequisites

- Python 3.8+
- MySQL Server
- MongoDB
- Git

## Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/vivekfulwala1407/recommendation_system.git
cd recommendation_system
python -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. MySQL Database Setup

**Install MySQL:**
- Windows: Download from [MySQL official site](https://dev.mysql.com/downloads/installer/)
- macOS: `brew install mysql`
- Linux: `sudo apt-get install mysql-server`

**Create Database:**
```sql
mysql -u root -p
CREATE DATABASE db;
EXIT;
```

**Update settings.py (if needed):**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'db',
        'USER': 'root',
        'PASSWORD': 'YOUR_PASSWORD',  # Change to your password
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 4. MongoDB Setup (Localhost)

**Install MongoDB:**
- Windows: Download from [MongoDB official site](https://www.mongodb.com/try/download/community)
- macOS: `brew install mongodb/brew/mongodb-community`
- Linux: Follow [MongoDB installation guide](https://docs.mongodb.com/manual/administration/install-on-linux/)

**Start MongoDB:**
```bash
# Windows (as service)
net start MongoDB

# macOS
brew services start mongodb/brew/mongodb-community

# Linux
sudo systemctl start mongod
```

**Verify MongoDB is running:**
```bash
mongo
# Should connect to MongoDB shell on localhost:27017
```

### 5. Django Setup

```bash
# Make migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Run server
python manage.py runserver
```

Server will run at: `http://127.0.0.1:8000/`

## API Endpoints

### Authentication
- `POST /auth/signup/` - User registration
- `POST /auth/signin/` - User login
- `POST /auth/forgot-password/` - Password reset request
- `POST /auth/reset-password/<token>/` - Reset password
- `POST /auth/token/refresh/` - Refresh JWT token

### Posts
- `GET /api/posts/` - List all posts
- `POST /api/posts/create/` - Create new post
- `GET /api/posts/<id>/` - Get specific post
- `PUT /api/posts/<id>/` - Update post
- `DELETE /api/posts/<id>/` - Delete post
- `POST /api/posts/<id>/interact/` - Like/comment/share post
- `GET /api/feed/` - Get personalized feed

## Testing Guide

### 1. Create Multiple Users

```bash
# Using API or Django admin
POST /auth/signup/
{
    "username": "user1",
    "email": "user1@example.com",
    "password": "testpass123",
    "confirm_password": "testpass123"
}

# Create multiple users:
# user1, user2, user3, testuser
```

### 2. Create Posts with Different Categories

Upload images for different categories to test AI recognition:

**Food Category:**
- Pizza images
- Coffee images
- Burger images

**Vehicle Category:**
- Car images
- Bike images
- Truck images

**Animal Category:**
- Dog images
- Cat images
- Bird images

**Create posts using:**
```bash
POST /api/posts/create/
Content-Type: multipart/form-data

{
    "title": "My Pizza Post",
    "image": <image_file>
}
```

### 3. Create Testing User for Feed Testing

```bash
# Create testuser
POST /auth/signup/
{
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "testpass123",
    "confirm_password": "testpass123"
}

# Login as testuser
POST /auth/signin/
{
    "username": "testuser",
    "password": "testpass123"
}
```

### 4. Test Interaction System

**Step 1: Initial Feed (New User)**
```bash
GET /api/feed/
Authorization: Bearer <testuser_token>

# Should return random diverse posts from all categories
```

**Step 2: Interact with Food Posts**
```bash
# Like a pizza post
POST /api/posts/<pizza_post_id>/interact/
{
    "action": "like"
}

# Like a coffee post
POST /api/posts/<coffee_post_id>/interact/
{
    "action": "like"
}

# Share a burger post
POST /api/posts/<burger_post_id>/interact/
{
    "action": "share"
}
```

**Step 3: Check Updated Feed**
```bash
GET /api/feed/
# Should now return ~70% food-related posts (pizza, coffee, burgers)
# and ~30% diverse content from other categories
```

**Step 4: Interact with Vehicle Posts**
```bash
# Like a car post
POST /api/posts/<car_post_id>/interact/
{
    "action": "like"
}

# Comment on a bike post
POST /api/posts/<bike_post_id>/interact/
{
    "action": "comment"
}
```

**Step 5: Check Feed Changes**
```bash
GET /api/feed/
# Should now show mixed content:
# - Food posts (pizza, coffee, burgers)
# - Vehicle posts (cars, bikes)
# - Some diverse content from other categories
# All shuffled and not in sequential order
```

### 5. Test Feed Shuffling

```bash
# Call feed API multiple times to verify shuffling
GET /api/feed/
GET /api/feed/
GET /api/feed/

# Each call should return different order of posts
# while maintaining 70% interest-based, 30% diverse ratio
```

### 6. Test Unlike/Uninteract

```bash
# Unlike previously liked post
POST /api/posts/<post_id>/interact/
{
    "action": "like"
}
# This will toggle the like (unlike if already liked)

# Check response includes updated counts:
{
    "message": "Post unliked",
    "likes": 2,
    "comments": 0,
    "shares": 1,
    "user_action": {"like": 0}
}
```

## How Recommendation System Works

1. **New User**: Gets random diverse feed from all categories
2. **After Interactions**: 
   - User likes pizza → Increases interest in "food" category
   - System recommends other food items (coffee, burgers, etc.)
   - 70% recommendations from interested categories
   - 30% diverse content for discovery
3. **Category Mapping**: Specific items map to broader categories
   - pizza, coffee, burgers → food
   - cars, bikes, trucks → vehicles  
   - dogs, cats, birds → animals

## Database Structure

**MySQL Tables:**
- `users` - User authentication and profiles
- `posts` - Post content and engagement metrics

**MongoDB Collections:**
- `post_metadata` - AI-generated tags and categories

## Tech Stack

- **Backend**: Django, Django REST Framework
- **AI/ML**: Transformers (HuggingFace), PyTorch, ViT
- **Databases**: MySQL, MongoDB
- **Authentication**: JWT (Simple JWT)
- **Image Processing**: Pillow, OpenCV