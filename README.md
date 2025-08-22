# Fantasta Backend

FastAPI backend for managing fantasy football auctions with NLP parsing (LangChain + OpenAI) and multi-user storage via Redis.

## 🚀 Setup & Start

1. **Clone the repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Redis** and setup the URL in the `.env` file
   ```python
   REDIS_URL = "redis://your-redis-url:6379/0"
   ```
4. **Configure your OpenAI key** in `.env` file:
   ```python
   OPENAI_API_KEY = "your-openai-key"
   ```
5. **Start the server**:
   ```bash
   uvicorn app.main:app --reload
   ```

## 📚 API Routes

### 1. Initialize a session

`POST /init_session`

**Body:**

```json
{
  "team_names": ["Team1", "Team2", ..., "Team8"],
  "budget": 500
}
```

**Response:**

```json
{
  "session_id": "...",
  "rosters": { ... }
}
```

### 2. Update the roster with an auction sentence

`POST /update_action`

**Body:**

```json
{
  "input_text": "dzeko teamX 150",
  "session_id": "...",
  "current": "forwards"
}
```

**Response:**

```json
{
  "player": "Edin Dzeko",
  "team": "TeamX",
  "price": 150,
  "status": "updated"
}
```

### 4. Get the list of available players for a role

`GET /players_list?session_id=your-session-id`

**Query Parameters:**

- `session_id`: The rosters session id to fetch players for (required)

**Response:**

```json
{
  "goalkeepers": [
    { "name": "Player1", "price": 123 },
    { "name": "Player2", "price": 12 }
  ],
  "defenders": [
    { "name": "Player1", "price": 123 },
    { "name": "Player2", "price": 12 }
  ],
  "midfielders": [
    { "name": "Player1", "price": 123 },
    { "name": "Player2", "price": 12 }
  ],
  "forwards": [
    { "name": "Player1", "price": 123 },
    { "name": "Player2", "price": 12 }
  ]
}
```

## 🧩 Main Components

- **FastAPI**: REST API
- **LangChain + OpenAI**: NLP parsing of auction sentences
- **Redis**: Multi-session roster storage
- **openpyxl**: Excel export/import (optional)

## 🛠 Notes

- Each session is identified by a `session_id`.
- Rosters are saved in Redis and can be exported to Excel.
- To test the API, use Swagger UI at `http://localhost:8000/docs`.

---

## 📝 TODO

- Next step: implement an endpoint to export an Excel file with the rosters for each session/team.

For questions or contributions, open an issue or contact us!
