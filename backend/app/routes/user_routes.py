from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.core.security import get_current_user
from app.database import get_db
from app.models.issue import Issue
from app.models.user import User
from app.schemas.dashboard_schema import UserDashboardResponse

router = APIRouter(
    prefix="/user",
    tags=["User Dashboard"]
)

@router.get("/dashboard",response_model=UserDashboardResponse)
def user_dashboard(
    db : Session = Depends(get_db),
    current_user : User = Depends(get_current_user)
):
    today = date.today()

    issues = db.query(Issue).filter(
        Issue.user_id == current_user.id
    ).all()


    currently_issued = [
        i for i in issues
        if i.issue_approved and i.return_date is None
    ]

    pending_issue = [
        i for i in issues
        if i.issue_requested and not i.issue_approved and not i.issue_rejected
    ]

    pending_return = [
        i for i in issues
        if i.return_requested and not i.return_approved and not i.return_rejected
    ]

    overdue = [
        i for i in currently_issued
        if (today - i.issue_date).days > 7
    ]


    total_fine =  sum(i.fine for i in currently_issued)

    return UserDashboardResponse(
        currentlyIssued=len(currently_issued),
        pendingIssueRequests=len(pending_issue),
        pendingReturnRequests=len(pending_return),
        overdueBooks=len(overdue),
        totalFine=total_fine
    )
