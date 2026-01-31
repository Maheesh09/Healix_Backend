from fastapi import FastAPI

app = FastAPI(title="Healix Backend API")

@app.get("/")
def health_check():
    return {"status": "Healix backend running"}
