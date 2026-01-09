from sqlalchemy import Column, ForeignKey,Integer,String
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.category import Category

class Book(Base):
    __tablename__ = "books"


    id = Column(Integer,primary_key=True)
    title = Column(String(100),nullable=False)
    author = Column(String(100),nullable=False)
    isbn = Column(String(20),unique=True,nullable=False)

    total_copies = Column(Integer,nullable=False)
    available_copies = Column(Integer,nullable=False)
    
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    category = relationship("Category")