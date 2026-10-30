# Inventory & Stock Management System

A beginner-friendly, clean, and professional Django project for managing inventory, suppliers, categories, and stock transactions.

## Tech Stack
- **Backend:** Django 5.x
- **API:** Django REST Framework (DRF)
- **Database:** MySQL (via `pymysql`)
- **Frontend:** HTML, CSS, Bootstrap 5, Chart.js

## Project Features (Viva Points)
1. **Simple Architecture:** Only 4 core models (Category, Supplier, Product, StockTransaction) to keep the project easy to understand and present.
2. **Dynamic Stock Calculation:** Stock In/Out is handled dynamically in the Views. When a transaction is created, the Product quantity is updated automatically without using complex signals.
3. **Data Integrity Validation:** Prevents "Stock Out" transactions if the requested quantity exceeds the available product stock.
4. **Interactive Dashboard:** Provides key metrics, low-stock alerts, and a Chart.js visualization of recent stock movements.
5. **REST API Integration:** A basic API for Products and Transactions to demonstrate backend-as-a-service capabilities.
6. **Premium UI/UX:** Clean, white-themed interface with indigo accents, utilizing Bootstrap 5 for responsiveness and modern cards/tables.
7. **Secure Authentication:** Standard Django Session authentication used for protecting the admin and dashboard views.

## Setup Instructions

### 1. Database Setup (MySQL)
Ensure you have MySQL (via XAMPP, WAMP, or standalone) running.
Create a database named `inventory_db`:
```sql
CREATE DATABASE inventory_db;
```

### 2. Environment Setup
Create a virtual environment and install dependencies:
```bash
python -m venv venv
venv\Scripts\activate
pip install django djangorestframework django-environ pymysql django-cors-headers
```

### 3. Environment Variables
Check the `.env` file in the root directory. Ensure the `DATABASE_URL` matches your MySQL setup.
Default:
```
DATABASE_URL=mysql://root:@127.0.0.1:3306/inventory_db
```
*(If you have a password, add it after `root:` like `root:mypassword@`)*

### 4. Migrations & Superuser
Run migrations to create database tables:
```bash
python manage.py makemigrations
python manage.py migrate
```

Create an admin user for login:
```bash
python manage.py createsuperuser
# Follow prompts to set username, email, and password (e.g., admin / admin)
```

### 5. Run the Server
Start the development server:
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` and log in with your superuser credentials.

## API Examples
The API requires session authentication by default (login via browser).

- **Products List:** `GET /api/products/`
- **Stock Transactions List:** `GET /api/transactions/`

## Important Django Concepts Used
- **Model relationships:** ForeignKey for Category->Product and Supplier->Product.
- **Form Validation:** Custom `clean()` method in `StockTransactionForm` to validate available stock.
- **QuerySet Aggregation & Annotation:** Using `Sum` and `F` objects in the dashboard view to calculate total stock value.
- **View Logic:** Standard function-based views with `@login_required` decorators for explicit flow control instead of hidden Signals.
