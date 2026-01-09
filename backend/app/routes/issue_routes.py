from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session,joinedload
from datetime import date

from app.database import get_db
from app.models.issue import Issue
from app.models.book import Book
from app.models.user import User
from app.schemas.issue_schema import  IssueAdminResponse, IssueReturnResponse, IssueUserResponse, RejectReturnRequest
from app.core.security import get_current_user

router = APIRouter(
    prefix="/issues",
    tags=["Issue Management"]
)

# =====================================================
# USER APIs
# =====================================================

# -------- REQUEST ISSUE (USER) --------
@router.post("/request-issue/{book_id}")
def request_issue(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "USER":
        raise HTTPException(status_code=403, detail="Only USER allowed")

    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book.available_copies <= 0:
        raise HTTPException(status_code=400, detail="No copies available")

    existing = db.query(Issue).filter(
        Issue.user_id == current_user.id,
        Issue.book_id == book_id,
        Issue.return_date == None
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Book already issued or requested")

    issue = Issue(
        user_id=current_user.id,
        book_id=book_id,
        issue_requested=True
    )

    db.add(issue)
    db.commit()

    return {"message": "Issue request sent to Admin"}


# -------- REQUEST RETURN (USER) --------
@router.put("/request-return/{issue_id}")
def request_return(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "USER":
        raise HTTPException(status_code=403, detail="Only USER allowed")

    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue or issue.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Issue not found")

    if issue.return_requested:
        raise HTTPException(status_code=400, detail="Return already requested")
    if issue.return_approved:
        raise HTTPException(status_code=400, detail="Return already approved")

    # Reset rejection if resubmitting
    issue.return_requested = True
    issue.return_rejected = False
    issue.return_remarks = None

    db.commit()

    return {"message": "Return request sent to Admin"}


# -------- USER CURRENTLY ISSUED BOOKS --------
@router.get("/my-books", response_model=list[IssueUserResponse])
def my_books(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "USER":
        raise HTTPException(status_code=403, detail="Only USER allowed")

    return db.query(Issue)\
    .options(joinedload(Issue.user), joinedload(Issue.book))\
    .filter(
        Issue.user_id == current_user.id,
        Issue.issue_approved == True,
        Issue.return_date == None
    ).all()



# -------- USER ISSUE & RETURN HISTORY --------
@router.get("/my-history", response_model=list[IssueUserResponse])
def my_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "USER":
        raise HTTPException(status_code=403, detail="Only USER allowed")

    return db.query(Issue)\
    .options(joinedload(Issue.user), joinedload(Issue.book))\
    .filter(Issue.user_id == current_user.id)\
    .order_by(Issue.issue_date.desc())\
    .all()



# =====================================================
# ADMIN APIs
# =====================================================

# -------- PENDING ISSUE REQUESTS --------
@router.get("/admin/pending-issues", response_model=list[IssueAdminResponse])
def pending_issue_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only ADMIN allowed")

    return db.query(Issue)\
    .options(joinedload(Issue.user), joinedload(Issue.book))\
    .filter(Issue.issue_requested == True)\
    .order_by(Issue.issue_date.desc())\
    .all()



# -------- APPROVE ISSUE --------
@router.put("/admin/approve-issue/{issue_id}")
def approve_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only ADMIN allowed")

    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    if issue.issue_approved:
        raise HTTPException(status_code=400, detail="Issue already approved")
    if issue.issue_rejected:
        raise HTTPException(status_code=400, detail="Issue already rejected")
    if not issue.issue_requested:
        raise HTTPException(status_code=400, detail="No pending issue request")

    book = db.query(Book).filter(Book.id == issue.book_id).first()
    if not book or book.available_copies <= 0:
        raise HTTPException(status_code=400, detail="No copies available")

    issue.issue_requested = False
    issue.issue_approved = True
    issue.issue_date = date.today()
    book.available_copies -= 1

    db.commit()
    db.refresh(issue)

    return {"message": "Issue approved successfully"}


# -------- REJECT ISSUE --------
@router.put("/admin/reject-issue/{issue_id}")
def reject_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only ADMIN allowed")

    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    if issue.issue_approved:
        raise HTTPException(status_code=400, detail="Cannot reject an approved issue")
    if issue.issue_rejected:
        raise HTTPException(status_code=400, detail="Issue already rejected")
    if not issue.issue_requested:
        raise HTTPException(status_code=400, detail="No pending issue request")

    issue.issue_requested = False
    issue.issue_rejected = True

    db.commit()
    db.refresh(issue)

    return {"message": "Issue rejected successfully"}


# -------- PENDING RETURN REQUESTS --------
@router.get("/admin/pending-returns", response_model=list[IssueAdminResponse])
def pending_return_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only ADMIN allowed")

    return db.query(Issue)\
    .options(joinedload(Issue.user), joinedload(Issue.book))\
    .filter(
        Issue.return_requested == True,
        Issue.return_approved == False
    ).all()



# -------- APPROVE RETURN --------
@router.put("/admin/approve-return/{issue_id}",response_model=IssueReturnResponse)
def approve_return(
    issue_id: int,
    remarks:str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only ADMIN allowed")

    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    if issue.return_approved:
        raise HTTPException(status_code=400, detail="Return already approved")
    if issue.return_rejected:
        raise HTTPException(status_code=400, detail="Return already rejected")
    if not issue.return_requested:
        raise HTTPException(status_code=400, detail="No pending return request")

    today = date.today()
    issue.return_date = today
    issue.return_approved = True
    issue.return_requested = False
    issue.return_remarks = remarks

    # Fine logic
    days = (today - issue.issue_date).days
    issue.fine = max(0, (days - 7) * 10)

    # Update book stock
    book = db.query(Book).filter(Book.id == issue.book_id).first()
    if book:
        book.available_copies += 1

    db.commit()
    db.refresh(issue)

    return issue


# -------- REJECT RETURN -----------------------
@router.put("/admin/reject-return/{issue_id}", response_model=IssueReturnResponse)
def reject_return(
    issue_id: int,
    payload: RejectReturnRequest,   
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only ADMIN allowed")

    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    if issue.return_approved:
        raise HTTPException(status_code=400, detail="Return already approved")
    if issue.return_rejected:
        raise HTTPException(status_code=400, detail="Return already rejected")
    if not issue.return_requested:
        raise HTTPException(status_code=400, detail="No pending return request")

    issue.return_rejected = True
    issue.return_requested = False
    issue.return_remarks = payload.reason

    db.commit()
    db.refresh(issue)

    return issue


# -------- ADMIN ISSUE & RETURN HISTORY --------
@router.get("/admin/history", response_model=list[IssueAdminResponse])
def admin_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Issue)\
        .options(joinedload(Issue.user), joinedload(Issue.book))\
        .filter(
            or_(
                Issue.issue_approved == True,
                Issue.issue_rejected == True,
                Issue.return_approved == True,
                Issue.return_rejected == True,
            )
        )\
        .order_by(Issue.issue_date.desc())\
        .all()


# -------- ADMIN OVERDUE BOOKS --------
@router.get("/admin/overdue", response_model=list[IssueAdminResponse])
def overdue_books(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only ADMIN allowed")

    today = date.today()
    allowed_days = 7
    fine_per_day = 10

    overdue_issues = db.query(Issue)\
    .options(joinedload(Issue.user), joinedload(Issue.book))\
    .filter(
        Issue.issue_approved == True,
        Issue.return_date == None,
        Issue.issue_date != None,
        func.datediff(today, Issue.issue_date) > allowed_days
    ).all()


    for issue in overdue_issues:
        overdue_days = (today - issue.issue_date).days - allowed_days
        issue.fine = overdue_days * fine_per_day
        issue.return_remarks = f"Overdue by {overdue_days} days"

    db.commit()
    return overdue_issues
