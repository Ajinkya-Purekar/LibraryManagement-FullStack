from pydantic import BaseModel

class UserDashboardResponse(BaseModel):
    currentlyIssued : int
    pendingIssueRequests : int
    pendingReturnRequests : int
    overdueBooks : int
    totalFine : float