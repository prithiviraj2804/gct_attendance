import asyncio
from json import JSONDecodeError
import os

from fastapi.concurrency import asynccontextmanager
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from jose import JWTError
from sqlalchemy.exc import (DataError, IntegrityError, InterfaceError,
                            OperationalError, ProgrammingError,
                            SQLAlchemyError)
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.database import Base, master_db_engine
from logs.logging import logger

from app.core.settings import settings
from app.utils.exception_handler import (authentication_error_handler,
                                         data_error_handler,
                                         database_exception_handler,
                                         global_exception_handler,
                                         http_exception_handler,
                                         integrity_error_handler,
                                         interface_error_handler,
                                         json_decode_error_handler,
                                         jwt_error_handler,
                                         operational_error_handler,
                                         permission_error_handler,
                                         programming_error_handler,
                                         timeout_error_handler,
                                         type_error_handler,
                                         validation_exception_handler,
                                         value_error_handler)

ENV = settings.environment

# Disable documentation if in production
if ENV == "production":
    app = FastAPI(docs_url=None, redoc_url=None, root_path=settings.base_path)
else:
    app = FastAPI(title=settings.app_name, version="0.1.0",
                  swagger_ui_parameters={"persistAuthorization": True},
                  root_path=settings.base_path
                  )

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(DataError, data_error_handler)
app.add_exception_handler(OperationalError, operational_error_handler)
app.add_exception_handler(ProgrammingError, programming_error_handler)
app.add_exception_handler(InterfaceError, interface_error_handler)
app.add_exception_handler(asyncio.TimeoutError, timeout_error_handler)
app.add_exception_handler(PermissionError, permission_error_handler)
app.add_exception_handler(HTTPException, authentication_error_handler)
app.add_exception_handler(ValueError, value_error_handler)
app.add_exception_handler(TypeError, type_error_handler)
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(JWTError, jwt_error_handler)
app.add_exception_handler(JSONDecodeError, json_decode_error_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# @app.get("/")
# async def read_root(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})

# Root endpoint to serve the HTML file
@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", "r") as file:
        return HTMLResponse(content=file.read(), media_type="text/html")

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with master_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info('[*] Postgresql Database connected ✅')
    yield

app.router.lifespan_context = lifespan


# Serve index.html for the root route and any unmatched route
# @app.get("/{full_path:path}")
# async def serve_react_app(full_path: str):
#     if full_path == "":
#         full_path = "index.html"
        
#     file_path = os.path.join("templates", full_path)
#     # Check if the file exists in the static folder (for JS, CSS, etc.)
#     if os.path.exists(file_path):
#         return FileResponse(file_path)
#     # Default to index.html for unmatched paths (React will handle routing)
#     return FileResponse(os.path.join("templates", "index.html"))

# # Catch-all route for frontend
# @app.get("/{full_path:path}")
# async def serve_frontend(full_path: str):
#     # Exclude API and static file paths from the catch-all route
#     if full_path.startswith("api/") or full_path.startswith("static/"):
#         raise HTTPException(status_code=404, detail="Not Found")
#     return FileResponse("templates/index.html")



from app.api.attendance.routers import router as attendance_router
from app.api.auth.routers import role_router,user_router
app.include_router(user_router,prefix="/api")
app.include_router(role_router,prefix="/api")
app.include_router(attendance_router,prefix="/api")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
