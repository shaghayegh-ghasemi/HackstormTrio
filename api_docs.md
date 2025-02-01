# API Documentation
Host Name: HackstormTrio.app


## Extract Location and Duration

**Endpoint:**  
`POST /api/subtitles`

**Description:**  
Extracts the location and duration of travel based on a query (uses OpenAi whisper).

**Request:**

- **Method:** `POST`
- **URL:** `/api/subtitlest`
- **Headers:**
  - `Content-Type: multipart/form-data`

**Request Example: Windows CMD**
```bash
curl -X POST http://127.0.0.1:5000/api/subtitles ^
     -H "Content-Type: application/json" ^
     -d "{\"url\": \"https://drive.google.com/file/d/1x2HlTWOH2_rJJWeEU7xl5na-mtfCqKV2/view?usp=drive_link\"}"


```

**Response Example:**

```json
{
    "duration": "5D4N",
    "location": "Montreal"
}
```

