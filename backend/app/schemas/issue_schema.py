from pydantic import BaseModel
from typing import Optional
from datetime import date

# ---------------- Base model with status flags ----------------
class IssueBase(BaseModel):
    id: int
    issue_date: Optional[date]
    return_date: Optional[date]
    fine: float

    # Status flags
    issue_requested: bool
    issue_approved: bool
    issue_rejected: bool
    return_requested: bool
    return_approved: bool
    return_rejected: bool

    class Config:
        from_attributes = True  # ORM support


# ---------------- Nested models ----------------
class UserBase(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class BookBase(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True


# ---------------- USER view ----------------
class IssueUserResponse(IssueBase):
    user: Optional[UserBase]  # include user info
    book: Optional[BookBase]  # include book info


# ---------------- ADMIN view ----------------
class IssueAdminResponse(IssueBase):
    user: Optional[UserBase]
    book: Optional[BookBase]


# ---------------- Approve/Reject return response ----------------
class IssueReturnResponse(IssueBase):
    user_id: int
    book_id: int
    return_remarks: Optional[str]

    class Config:
        from_attributes = True

# ---------------- Reject return request payload ----------------
class RejectReturnRequest(BaseModel):
    reason: Optional[str] = None
