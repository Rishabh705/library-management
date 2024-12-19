# Library Management System

This is a simple library management system built with Flask and SQLite. It allows users to register, login, and perform CRUD operations on books and members in the library. Authentication is managed using tokens stored in the database.

## Features

- User Registration and Login
- Book Management (Add, Update, Delete, View)
- Member Management (Add, Update, Delete, View)
- Authentication via tokens
- API endpoints for interacting with the system

### Design Decisions

- **Flask and SQLite**: Chose Flask due to its simplicity and flexibility for building RESTful APIs, and SQLite for a lightweight, file-based database.
- **Token-Based Authentication**: Used token-based authentication for secure API access to manage books and members.
- **RESTful API Design**: Used RESTful design principles for the API, ensuring clear separation of concerns and scalability.

### Assumptions and Limitations

- The system is designed for a single user (admin), without support for multiple users managing the library concurrently.
- No email validation for members is currently in place.
- No role management is implemented (all users have the same permissions).

## Installation

### Prerequisites

- Python 3.x
- Flask
- SQLite

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/Rishabh705/library-management.git
   cd library-management
   ```

2. Create and activate a virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate 
    ```

3. Install required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Initialize the database by running the following command:

    ```bash
    python app.py
    ```

This will run the init_db() function to set up the necessary tables in the SQLite database.

## API Endpoints

### Authentication

#### Login
POST /login

Request Body:
``` bash
{
  "username": "your_username",
  "password": "your_password"
}
```

Response:
``` bash
{
  "message": "Login successful",
  "token": "generated_token"
}
```
#### Register

POST /register

Request Body:

``` bash
{
  "username": "your_username",
  "password": "your_password"
}
```


Response:
``` bash
{
  "message": "User registered successfully",
  "user_id": "user_id"
}
```

### Books

#### Add book

POST /books 

Request Body:
``` bash
{
  "title": "Book Title",
  "author": "Book Author",
  "year": 2021
}
```
Response:

``` bash
{
  "message": "Book added successfully"
}
```

#### Get all books

GET /books

Response:

``` bash
[
  {
    "id": "book_id",
    "title": "Book Title",
    "author": "Book Author",
    "year": 2021
  }
]
```

#### Update a book

PUT /books/<book_id>

Request Body:

``` bash
{
  "title": "Updated Book Title",
  "author": "Updated Author",
  "year": 2022
}
```

Response:
``` bash

{
  "message": "Book updated successfully"
}
```

#### Delete a book

DELETE /books/<book_id>

Response:

``` bash
{
  "message": "Book deleted successfully"
}
```

### Members

#### Add a member

POST /members

Request Body:

``` bash
{
  "name": "Member Name",
  "email": "member_email"
}
```

Response:

``` bash
{
  "message": "Member added successfully"
}
```


#### Get a member
GET /members


Response:

``` bash
[
  {
    "id": "member_id",
    "name": "Member Name",
    "email": "member_email"
  }
]
```

#### Update a member

PUT /members/<member_id>

Request Body:

``` bash
{
  "name": "Updated Name",
  "email": "updated_email"
}
```

Response:

``` bash
{
  "message": "Member updated successfully"
}
```

#### Delete a member

DELETE /members/<member_id>

Response:
``` bash
{
  "message": "Member deleted successfully"
}
```

## Database Structure
The database (library.db) has the following tables:

* users
    ``` bash
    id (INTEGER, PRIMARY KEY)
    username (TEXT, UNIQUE)
    password (TEXT)
    ```
* tokens
    ``` bash
    id (INTEGER, FOREIGN KEY to users)
    token (TEXT, UNIQUE)
    ```
* books
    ``` bash
    id (INTEGER, PRIMARY KEY)
    title (TEXT)
    author (TEXT)
    year (INTEGER)
    ```
* members
    ``` bash
    id (INTEGER, PRIMARY KEY)
    name (TEXT)
    email (TEXT)
    ```
Running the App
To run the app in development mode, use the following command:
``` bash
python app.py
```
The app will be available at http://127.0.0.1:5000/.