from fastapi import FastAPI, Request
import uvicorn
import redis

app = FastAPI()

# Set up Redis connection
r = redis.Redis(host='localhost', port=6379, db=0)

@app.post("/i/")
async def i(request: Request):
    message = await request.json()
    
    client_host = request.client.host  # Get the client's IP address

    message = f"""

    Another interpreter sent this message to you: {message}
    To respond, send a POST request to {client_host}/i/.

    """.strip()

    r.lpush("to_main", {
        "role": "computer",
        "type": "message",
        "content": message
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)