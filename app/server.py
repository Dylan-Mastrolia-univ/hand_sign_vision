from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import base64

from cnn_model import SignModel


MODEL_PATH = "best_scratch.keras"
CLASSES_PATH = "classes.json"  


app = FastAPI(title="Handsign Live Inference")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


model = SignModel(MODEL_PATH,CLASSES_PATH)

class PredictIn(BaseModel):
    image: str 

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict")
async def predict(payload: PredictIn):
    data = payload.image
    try:
        if "," in data:
            data = data.split(",", 1)[1]
        image_bytes = base64.b64decode(data)
    except Exception:
        raise HTTPException(status_code=400, detail="Image base64 invalide.")

    out = model.predict_from_bytes(image_bytes, topk=3)
    return JSONResponse(out)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

