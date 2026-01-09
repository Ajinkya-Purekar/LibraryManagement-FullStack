from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
#from datetime import date,timedelta


from app.database import get_db
from app.models.issue import Issue
from app.models.book import Book
from app.models.user import User
#from app. schemas.issue_schema import IssueAdminResponse, IssueCreate, IssueResponse, IssueReturnResponse
from app.core.security import get_current_user 

router = APIRouter(
    prefix = "/admin",
    tags = ["Admin Dashboard"]
)

# ==== DASHBOARD SUMMARY (COUNTS)  =================

@router.get("/dashboard/summary")
def admin_dashboard_summary(
    db:Session = Depends(get_db),
    current_user:User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ADMIN allowed"
        )
    
    total_users = db.query(User).count()
    total_books = db.query(Book).count()

    issued_books = db.query(Issue).filter(
        Issue.issue_approved == True,
        Issue.return_date == None
    ).count()


    pending_issue_requests = db.query(Issue).filter(
        Issue.issue_requested == True,
        Issue.issue_approved == False,
        Issue.issue_rejected == False
    ).count()

    pending_return_requests = db.query(Issue).filter(
        Issue.return_requested == True,
        Issue.return_approved == False
    ).count()

    return {
        "total_users" : total_users,
        "total_books" : total_books,
        "issued_books" : issued_books,
        "pending_issue_requests" : pending_issue_requests,
        "pending_return_approved" : pending_return_requests
    }



#  PENDING ISSUE REQUESTS  =================

@router.get("/dashboard/pending-issues")
def pending_issue_requests(
    db:Session = Depends(get_db),
    current_user : User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ADMIN allowed"
        )
    
    return db.query(Issue).filter(
        Issue.issue_requested == True,
        Issue.issue_approved == False,
        Issue.issue_rejected == False
    ).all()


#   PENDING RETURN REQUESTS ====================

@router.get("/dashboard/pending-returns")
def pending_return_requests(
    db : Session = Depends(get_db),
    current_user : User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ADMIN allowed"
        )
    
    return db.query(Issue).filter(
        Issue.return_requested == True,
        Issue.return_approved == False
    ).all()



#  BOOK INVENTORY OVERVIEW ==============

@router.get("/dashboard/books")
def book_inventory(
        db : Session = Depends(get_db),
        current_user : User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ADMIN allowed"
        )
    
    return db.query(Book).all()
