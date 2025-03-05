import asyncio
from json import JSONDecodeError

from fastapi.concurrency import asynccontextmanager
import uvicorn
from fastapi import FastAPI, HTTPException
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

app.mount("/public", StaticFiles(directory="./public"), name="static")

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with master_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info('[*] Postgresql Database connected ✅')
    yield

app.router.lifespan_context = lifespan



from app.api.attendance.routers import router as attendance_router
from app.api.auth.routers import router as auth_router
app.include_router(attendance_router)
app.include_router(auth_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
