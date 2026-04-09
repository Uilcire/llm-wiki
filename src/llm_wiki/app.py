from fastapi import FastAPI
from llm_wiki.api.routes import router


app = FastAPI(title="LLM Wiki")
app.include_router(router)


@app.get('/health') 
async def health(): 
    return {"status" : "ok"}