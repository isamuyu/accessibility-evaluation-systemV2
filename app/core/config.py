from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "无障碍设施评价系统"
    VERSION: str = "1.0.0"
    
    # 数据库
    DATABASE_URL: str = "sqlite:///./accessibility.db"
    
    # 安全
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1天
    # 是否强制所有业务接口需要 JWT 认证（开发环境默认关闭，生产环境应开启）
    AUTH_REQUIRED: bool = False
    # 允许的跨域来源（不要用 "*" 配 allow_credentials=True）
    CORS_ORIGINS: str = "http://localhost:8001,http://127.0.0.1:8001"
    
    # 文件存储
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # 评价配置
    DEFAULT_STANDARD_VERSION: str = "2022"
    Q5_MAX_SCORE: float = 20.0
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()