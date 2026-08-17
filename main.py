from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.core.config import settings
from app.api import projects, buildings, scoring, standard_clauses, templates, auth, reports, uploads
from app.core.database import engine, Base
from app.core.security import get_current_user

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="基于T/CNAEC 1304—2022《民用建筑无障碍设施评价标准》的评价系统"
)

# CORS配置（明确来源列表，避免 "*" + credentials 的危险组合）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)

# AUTH_REQUIRED 开启时，业务接口统一要求 JWT 认证
protected_dependencies = [Depends(get_current_user)] if settings.AUTH_REQUIRED else []
app.include_router(projects.router, dependencies=protected_dependencies)
app.include_router(buildings.router, dependencies=protected_dependencies)
app.include_router(scoring.router, dependencies=protected_dependencies)
app.include_router(standard_clauses.router, dependencies=protected_dependencies)
app.include_router(templates.router, dependencies=protected_dependencies)
app.include_router(reports.router, dependencies=protected_dependencies)
app.include_router(uploads.router, dependencies=protected_dependencies)

# 静态文件服务 - 前端文件
frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "public")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")



@app.get("/")
def root():
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "message": "无障碍设施评价系统API",
        "version": settings.VERSION,
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}