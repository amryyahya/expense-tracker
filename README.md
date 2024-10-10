# Expense Tracker API

This project is a simple **Expense Tracker API** built with **Flask**. It supports user authentication, including registration, login, and token-based authorization with JWT. Users can manage their expenses, filter by dates, categories, and amounts, as well as manage categories.

## Table of Contents

- [Installation](#installation)
- [Endpoints](#endpoints)
  - [User Endpoints](#user-endpoints)
  - [Expense Endpoints](#expense-endpoints)
  - [Category Endpoints](#category-endpoints)
- [Usage](#usage)
- [License](#license)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/amryyahya/expense-tracker-api.git
    cd expense-tracker-api
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the application:
    ```bash
    python3 run.py
    ```

4. Set up your `.env` file with your environment variables.

## Endpoints

### User Endpoints

- **Check Email**  
  **POST** `/check-email`
  - Request Body: 
    ```json
    {
      "email": "user@example.com"
    }
    ```
  - Response: 
    ```json
    {
      "exist": true/false
    }
    ```

- **Check Username**  
  **POST** `/check-username`
  - Request Body: 
    ```json
    {
      "username": "exampleuser"
    }
    ```
  - Response: 
    ```json
    {
      "exist": true/false
    }
    ```

- **Register**  
  **POST** `/register`
  - Request Body:
    ```json
    {
      "username": "exampleuser",
      "email": "user@example.com",
      "displayName": "User Name",
      "password": "password123"
    }
    ```
  - Response:
    ```json
    {
      "msg": "User registered successfully"
    }
    ```

- **Login**  
  **POST** `/login`
  - Request Body:
    ```json
    {
      "username": "exampleuser",
      "password": "password123"
    }
    ```
  - Response:
    ```json
    {
      "access_token": "your-access-token",
      "refresh_token": "your-refresh-token"
    }
    ```

- **Refresh Token**  
  **POST** `/refresh`
  - Requires: Refresh Token
  - Response:
    ```json
    {
      "access_token": "new-access-token"
    }
    ```

- **Logout**  
  **POST** `/logout`
  - Requires: Access Token
  - Response:
    ```json
    {
      "msg": "Token revoked"
    }
    ```

### Expense Endpoints

- **Get Expenses**  
  **GET** `/expenses`
  - Query Parameters:
    - `page` (optional): Pagination page number
    - `limit` (optional): Number of records per page
    - `start_date`, `end_date` (optional): Filter by date range
    - `min_amount`, `max_amount` (optional): Filter by amount range
    - `category` (optional): Filter by category
    - `sort_by` (optional): Field to sort by (default: date)
    - `order` (optional): Sort order (`asc` or `desc`)
  - Requires: Access Token
  - Response:
    ```json
    {
      "expenses": []
    }
    ```

- **Add Expense**  
  **POST** `/expenses`
  - Request Body:
    ```json
    {
      "amount": 100,
      "category": "Food",
      "description": "Grocery Shopping",
      "date": "2023-01-01T12:00:00"
    }
    ```
  - Requires: Access Token
  - Response:
    ```json
    {
      "status": "expense record added"
    }
    ```

- **Delete Expense**  
  **DELETE** `/expenses`
  - Request Body:
    ```json
    {
      "_id": "expense-id"
    }
    ```
  - Requires: Access Token
  - Response:
    ```json
    {
      "status": "expense record deleted"
    }
    ```

### Category Endpoints

- **Get All Categories**  
  **GET** `/categories`
  - Requires: Access Token
  - Response:
    ```json
    {
      "categories": []
    }
    ```

- **Add Category**  
  **POST** `/categories`
  - Request Body:
    ```json
    {
      "name": "New Category"
    }
    ```
  - Requires: Access Token
  - Response:
    ```json
    {
      "status": "new category added"
    }
    ```

- **Delete Category**  
  **DELETE** `/categories`
  - Request Body:
    ```json
    {
      "name": "Category Name"
    }
    ```
  - Requires: Access Token
  - Response:
    ```json
    {
      "status": "category deleted"
    }
    ```

## Usage

1. Register a user using the `/register` endpoint.
2. Log in to get an access and refresh token.
3. Use the access token to interact with the expenses and categories routes.
