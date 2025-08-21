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
  "rose": { ... }
}
```

### 2. Update the roster with an auction sentence

`POST /update_auction`

**Body:**

```json
{
  "input_text": "dzeko teamX 150",
  "session_id": "..."
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

### 3. Get the current roster

`GET /rose?session_id=...`

**Response:**

```json
{
  "rose": { ... }
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
