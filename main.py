import os
import uuid
import asyncio
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from agent import screen_all

app = FastAPI(title="CV Screener")
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
    request,
    "index.html"
)
    

@app.post("/screen")
async def screen(
    job_description: str = Form(...),
    cvs: list[UploadFile] = File(...),
    cover_letters: list[UploadFile] = File(default=[]),
):
    session_id = uuid.uuid4().hex
    session_dir = UPLOAD_DIR / session_id
    session_dir.mkdir()

    saved_cvs = []
    for cv in cvs:
        path = session_dir / f"cv_{cv.filename}"
        path.write_bytes(await cv.read())
        saved_cvs.append(str(path))

    # Match cover letters to CVs by filename stem (e.g. john_cv.pdf + john_cl.pdf)
    cl_map = {}
    for cl in cover_letters:
        path = session_dir / f"cl_{cl.filename}"
        path.write_bytes(await cl.read())
        cl_map[cl.filename] = str(path)

    candidates = []
    for cv_path in saved_cvs:
        cv_name = Path(cv_path).name.replace("cv_", "")
        # Try to find a matching cover letter by stem
        cl_path = None
        for cl_name, cl_file_path in cl_map.items():
            if Path(cl_name).stem.lower() in Path(cv_name).stem.lower() or \
               Path(cv_name).stem.lower() in Path(cl_name).stem.lower():
                cl_path = cl_file_path
                break
        candidates.append({"cv": cv_path, "cover_letter": cl_path})

    try:
        reviews = await screen_all(job_description, candidates)
        return JSONResponse([r.model_dump() for r in reviews])
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    finally:
        # Clean up uploaded files
        import shutil
        shutil.rmtree(session_dir, ignore_errors=True)