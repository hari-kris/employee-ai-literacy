import asyncio
import os

from dotenv import load_dotenv

load_dotenv()  # must run before app.scorer is imported so the API key is in the environment

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates

from app.exporter import to_csv
from app.parser import extract_text
from app.scorer import score_resume

app = FastAPI(title="Employee AI Literacy Scorer")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/score")
async def score(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    results: list[tuple[str, str | float]] = []

    for upload in files:
        filename = upload.filename or "unknown"
        content = await upload.read()

        try:
            text = extract_text(filename, content)
        except ValueError as exc:
            results.append((filename, f"parse_error: {exc}"))
            continue

        try:
            _, score = await asyncio.to_thread(score_resume, filename, text)
            results.append((filename, score))
        except Exception as exc:
            results.append((filename, f"api_error: {exc}"))

    if not results:
        raise HTTPException(status_code=400, detail="No processable files found")

    csv_text = to_csv(results)

    return StreamingResponse(
        iter([csv_text]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ai_literacy_scores.csv"},
    )
