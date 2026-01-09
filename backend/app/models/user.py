from sqlalchemy import Column, Integer, String, Enum
from app.database import Base
import enum


class RoleEnum(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class User(Base):
    __tablename__ = "users"


    id = Column(Integer, primary_key=True, index= True)

    #Auth
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255),nullable=False)

    username = Column(String(50),unique=True,nullable=False)
    role = Column(Enum(RoleEnum),default=RoleEnum.USER)