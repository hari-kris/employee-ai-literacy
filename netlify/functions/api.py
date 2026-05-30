"""
Netlify serverless function handler for the /score endpoint.
Wrapped with Mangum so FastAPI runs on AWS Lambda (Netlify Functions).
Files are scored in parallel to stay within the 10-second function timeout.
"""
import asyncio
import os
import sys

# Ensure the project root is on the path so 'app.*' can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from mangum import Mangum

from app.exporter import to_csv
from app.parser import extract_text
from app.scorer import score_resume

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)


async def _process(upload: UploadFile) -> tuple[str, str | float]:
    filename = upload.filename or "unknown"
    content = await upload.read()

    try:
        text = extract_text(filename, content)
    except ValueError as exc:
        return (filename, f"parse_error: {exc}")

    try:
        _, score = await asyncio.to_thread(score_resume, filename, text)
        return (filename, score)
    except Exception as exc:
        return (filename, f"api_error: {exc}")


@app.post("/score")
async def score(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    # Process all files in parallel to avoid Lambda timeout
    results = await asyncio.gather(*[_process(f) for f in files])

    csv_text = to_csv(list(results))
    return StreamingResponse(
        iter([csv_text]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ai_literacy_scores.csv"},
    )


handler = Mangum(app, lifespan="off")
