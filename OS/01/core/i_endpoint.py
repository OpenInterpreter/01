@app.post("/i/")
async def i(request: Request):
    message = await request.json()
    message = to_lmc(message)
    r.lpush("to_main", message)