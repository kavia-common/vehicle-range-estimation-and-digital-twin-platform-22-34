# Shim: FastAPI template may not include pydantic-settings; provide a minimal BaseSettings using pydantic v2
from pydantic import BaseModel

class BaseSettings(BaseModel):
    class Config:
        extra = "ignore"

    def __init__(self, **data):
        import os
        # Load env onto defaults if present
        for k in list(self.__fields__):
            env_v = os.getenv(k)
            if env_v is not None:
                # naive casting
                field = self.__fields__[k]
                typ = field.annotation
                try:
                    if typ in (int,):
                        env_v = int(env_v)
                    elif typ in (float,):
                        env_v = float(env_v)
                    elif typ in (bool,):
                        env_v = env_v.lower() in ("1","true","yes","y")
                except Exception:
                    pass
                data.setdefault(k, env_v)
        super().__init__(**data)
