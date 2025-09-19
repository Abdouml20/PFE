# Crafty - Artisanal E-commerce Platform

Crafty is a Django-based e-commerce web application designed for selling artisanal and handcrafted products. The platform connects talented artists with customers looking for unique handcrafted items.

## Features

- **User Authentication**: Custom user model with role-based permissions (artist/customer)
- **Multi-language Support**: English and Arabic language support
- **Product Management**: Browse, search, and filter products by categories
- **Artist Profiles**: Dedicated artist profiles and portfolios
- **Shopping Cart**: Session-based shopping cart functionality
- **Order Management**: Complete checkout process and order history
- **Artist Dashboard**: For artists to manage their products
- **Responsive Design**: Mobile-friendly interface

## Tech Stack

- **Backend**: Django 5.1.5
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Authentication**: Django AllAuth
- **Forms**: Django Crispy Forms
- **Image Handling**: Pillow

## Project Structure

The project follows Django's MVT (Model-View-Template) architecture and is organized into the following apps:

- **users**: User authentication and profile management
- **products**: Product listing and details
- **artists**: Artist profiles and portfolios
- **categories**: Product categorization
- **orders**: Order processing and history
- **cart**: Shopping cart functionality

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/crafty.git
cd crafty
```

2. Create and activate a virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Run migrations:
```
python manage.py migrate
```

5. Create a superuser:
```
python manage.py createsuperuser
```

6. Run the development server:
```
python manage.py runserver
```

7. Access the application at http://127.0.0.1:8000/

## Environment Setup

For production, create a `.env` file in the project root with the following variables:
```
DEBUG=False
SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url
ALLOWED_HOSTS=your_domain.com
```

## Deployment

The application is configured for easy deployment to platforms like Heroku or PythonAnywhere. Make sure to:

1. Set environment variables
2. Configure static and media file storage
3. Set up a production database
4. Configure email settings

## License

This project is licensed under the MIT License - see the LICENSE file for details.
# Force redeploy - Fri Sep 19 09:05:46 PM CET 2025
