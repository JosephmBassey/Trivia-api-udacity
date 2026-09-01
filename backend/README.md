# Backend - Trivia API

Flask and SQLAlchemy API for browsing, creating, deleting, searching, and
playing with trivia questions.

## Setup

Requirements:

- Python 3
- PostgreSQL

From the `backend` directory:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create and seed the development database:

```bash
createdb trivia
psql trivia < trivia.psql
```

The PostgreSQL username, password, host, and database name are configured in
`models.py`.

## Run the server

From the `backend` directory:

```bash
export FLASK_APP=flaskr
flask run --reload
```

The API runs at `http://127.0.0.1:5000`.

## Run the tests

Create and seed the test database before running the suite:

```bash
dropdb --if-exists trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python3 test_flaskr.py
```

## API endpoints

All successful responses contain `"success": true`.

### GET /categories

Returns all categories.

Request parameters: none.

Curl example:

```bash
curl http://127.0.0.1:5000/categories
```

Expected errors: none for a valid request.

```json
{
  "success": true,
  "categories": {
    "1": "Science",
    "2": "Art"
  }
}
```

### GET /questions?page=1

Returns ten questions per page, the total number of questions, and all
categories.

Request parameters:

- `page`: optional positive integer; defaults to `1`.

Curl example:

```bash
curl "http://127.0.0.1:5000/questions?page=1"
```

Expected errors: `400` for an invalid page and `404` when the page has no
questions.

```json
{
  "success": true,
  "questions": [
    {
      "id": 20,
      "question": "What is the heaviest organ in the human body?",
      "answer": "The Liver",
      "category": 1,
      "difficulty": 4
    }
  ],
  "total_questions": 19,
  "categories": {
    "1": "Science"
  },
  "current_category": null
}
```

### POST /questions

Creates a question.

Request body:

```json
{
  "question": "What is the capital of France?",
  "answer": "Paris",
  "category": 3,
  "difficulty": 1
}
```

Curl example:

```bash
curl -X POST http://127.0.0.1:5000/questions \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the capital of France?",
    "answer": "Paris",
    "category": 3,
    "difficulty": 1
  }'
```

Response:

```json
{
  "success": true,
  "created": 24,
  "total_questions": 20
}
```

Expected errors: `400` when JSON is missing and `422` when required fields or
the category are invalid.

### DELETE /questions/{question_id}

Deletes a question by ID.

Request parameters:

- `question_id`: question ID in the URL.

Curl example:

```bash
curl -X DELETE http://127.0.0.1:5000/questions/24
```

```json
{
  "success": true,
  "deleted": 24,
  "total_questions": 19
}
```

Expected errors: `404` when the question does not exist.

### POST /questions/search

Returns questions containing the search term.

Request body:

```json
{
  "searchTerm": "title"
}
```

Curl example:

```bash
curl -X POST http://127.0.0.1:5000/questions/search \
  -H "Content-Type: application/json" \
  -d '{"searchTerm": "title"}'
```

```json
{
  "success": true,
  "questions": [
    {
      "id": 5,
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?",
      "answer": "Maya Angelou",
      "category": 4,
      "difficulty": 2
    },
    {
      "id": 6,
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?",
      "answer": "Edward Scissorhands",
      "category": 5,
      "difficulty": 3
    }
  ],
  "total_questions": 2,
  "current_category": null
}
```

Expected errors: `400` when JSON is missing and `422` when `searchTerm` is
missing.

### GET /categories/{category_id}/questions?page=1

Returns paginated questions belonging to one category.

Request parameters:

- `category_id`: category ID in the URL.
- `page`: optional positive integer; defaults to `1`.

Curl example:

```bash
curl "http://127.0.0.1:5000/categories/1/questions?page=1"
```

```json
{
  "success": true,
  "questions": [
    {
      "id": 20,
      "question": "What is the heaviest organ in the human body?",
      "answer": "The Liver",
      "category": 1,
      "difficulty": 4
    }
  ],
  "total_questions": 3,
  "current_category": "Science"
}
```

Expected errors: `400` for an invalid page and `404` for an unknown category
or empty page.

### POST /quizzes

Returns a random question that has not already been played. Use category ID
`0` to include every category.

Request body:

```json
{
  "previous_questions": [20, 21],
  "quiz_category": {
    "id": 1,
    "type": "Science"
  }
}
```

Curl example:

```bash
curl -X POST http://127.0.0.1:5000/quizzes \
  -H "Content-Type: application/json" \
  -d '{
    "previous_questions": [20, 21],
    "quiz_category": {
      "id": 1,
      "type": "Science"
    }
  }'
```

```json
{
  "success": true,
  "question": {
    "id": 22,
    "question": "Hematology is a branch of medicine involving the study of what?",
    "answer": "Blood",
    "category": 1,
    "difficulty": 4
  }
}
```

When no questions remain, `"question"` is `null`.

Expected errors: `400` when JSON is invalid, `422` when required values are
missing, and `404` for an unknown category.

## Errors

Errors are returned as JSON with status `400`, `404`, `422`, or `500`.

```json
{
  "success": false,
  "error": 404,
  "message": "Resource Not Found"
}
```
