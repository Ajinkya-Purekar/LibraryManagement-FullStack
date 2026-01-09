from sqlalchemy import Column,Integer,String,Date,ForeignKey,Float,Boolean
from sqlalchemy.orm import relationship
from datetime import date
from app.database import Base


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer,primary_key=True)
    user_id = Column(Integer,ForeignKey("users.id"))
    book_id = Column(Integer,ForeignKey("books.id"))

    issue_date = Column(Date,nullable=True)
    return_date = Column(Date,nullable=True)

    issue_requested = Column(Boolean,default= False)
    issue_approved = Column(Boolean,default=False)
    issue_rejected = Column(Boolean,default=False)

    return_requested = Column(Boolean,default=False)
    return_approved = Column(Boolean,default=False)
    return_rejected = Column(Boolean,default=False)

    
    fine = Column(Float,default=0)

    return_remarks = Column(String(255),nullable=True)

    user = relationship("User")
    book = relationship("Book")
    