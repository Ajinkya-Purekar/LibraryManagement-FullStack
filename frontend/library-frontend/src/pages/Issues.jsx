import { useEffect, useState, useCallback } from 'react';
import {
  Container,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
  TablePagination
} from '@mui/material';
import { useAuth } from '../context/AuthContext';
import {
  getMyBooks,
  getMyHistory,
  requestReturn,
  getPendingIssues,
  approveIssue,
  rejectIssue,
  getPendingReturns,
  approveReturn,
  rejectReturn,
  getAdminHistory,
  getOverdueBooks
} from '../services/api';

function Issues() {
  const { user } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // 🔹 Pagination (BOTH USER & ADMIN)
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      let response;
      if (user.role === 'USER') {
        if (tabValue === 0) response = await getMyBooks();
        else response = await getMyHistory();
      } else {
        if (tabValue === 0) response = await getPendingIssues();
        else if (tabValue === 1) response = await getPendingReturns();
        else if (tabValue === 2) response = await getOverdueBooks();
        else if (tabValue === 3) response = await getAdminHistory();
      }
      setData(response.data);
      setError('');
    } catch (err) {
      console.error(err);
      setError('Failed to fetch data.');
    } finally {
      setLoading(false);
    }
  }, [tabValue, user]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const getStatus = (issue) => {
    if (issue.issue_rejected) return 'ISSUE_REJECTED';
    if (issue.return_approved) return 'RETURNED';
    if (issue.return_rejected) return 'RETURN_REJECTED';
    if (issue.return_requested) return 'PENDING_RETURN';
    if (issue.issue_requested) return 'PENDING_ISSUE';
    if (issue.issue_approved) return 'ISSUED';
    return 'UNKNOWN';
  };

  // USER actions
  const handleRequestReturn = async (id) => {
    try {
      await requestReturn(id);
      fetchData();
    } catch (err) {
      console.error(err);
      setError('Failed to request return.');
    }
  };

  // ADMIN actions
  const handleApproveIssue = async (id) => {
    try {
      await approveIssue(id);
      fetchData();
    } catch (err) {
      console.error(err);
      setError('Failed to approve issue.');
    }
  };

  const handleRejectIssue = async (id) => {
    try {
      await rejectIssue(id);
      fetchData();
    } catch (err) {
      console.error(err);
      setError('Failed to reject issue.');
    }
  };

  const handleApproveReturn = async (id) => {
    try {
      await approveReturn(id, 'Return approved');
      fetchData();
    } catch (err) {
      console.error(err);
      setError('Failed to approve return.');
    }
  };

  const handleRejectReturn = async (id) => {
    try {
      await rejectReturn(id, "Return rejected");
      fetchData();
    } catch (err) {
      console.error(err);
      setError("Failed to reject return.");
    }
  };

  // 🔹 PAGINATED DATA (USER + ADMIN)
  const paginatedData = data.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  const renderTableRows = () => {
    return paginatedData.map((issue) => (
      <TableRow key={issue.id}>
        <TableCell>{issue.user?.username || issue.user_id || 'N/A'}</TableCell>
        <TableCell>{issue.book?.title || issue.book_id || 'N/A'}</TableCell>
        <TableCell>{issue.issue_date || 'N/A'}</TableCell>
        <TableCell>{issue.return_date || 'N/A'}</TableCell>
        <TableCell>${issue.fine || 0}</TableCell>
        <TableCell>{getStatus(issue)}</TableCell>

        {user.role === 'USER' && tabValue === 0 && (
          <TableCell>
            {issue.issue_approved &&
              !issue.return_requested &&
              !issue.return_approved && (
                <Button onClick={() => handleRequestReturn(issue.id)}>
                  {issue.return_rejected ? 'Reapply Return' : 'Request Return'}
                </Button>
              )}
          </TableCell>
        )}

        {user.role === 'ADMIN' && tabValue < 2 && (
          <TableCell>
            {issue.issue_requested &&
              !issue.issue_approved &&
              !issue.issue_rejected && (
                <>
                  <Button onClick={() => handleApproveIssue(issue.id)}>
                    Approve
                  </Button>
                  <Button
                    color="error"
                    onClick={() => handleRejectIssue(issue.id)}
                  >
                    Reject
                  </Button>
                </>
              )}
            {issue.return_requested &&
              !issue.return_approved &&
              !issue.return_rejected && (
                <>
                  <Button onClick={() => handleApproveReturn(issue.id)}>
                    Approve Return
                  </Button>
                  <Button
                    color="error"
                    onClick={() => handleRejectReturn(issue.id)}
                  >
                    Reject Return
                  </Button>
                </>
              )}
          </TableCell>
        )}
      </TableRow>
    ));
  };

  return (
    <Container>
      <Typography variant="h4" gutterBottom>
        Issues
      </Typography>
      {error && <Alert severity="error">{error}</Alert>}

      {user.role === 'USER' ? (
        <Tabs
          value={tabValue}
          onChange={(e, newValue) => {
            setTabValue(newValue);
            setPage(0);
          }}
        >
          <Tab label="My Books" />
          <Tab label="History" />
        </Tabs>
      ) : (
        <Tabs
          value={tabValue}
          onChange={(e, newValue) => {
            setTabValue(newValue);
            setPage(0);
          }}
        >
          <Tab label="Pending Issues" />
          <Tab label="Pending Returns" />
          <Tab label="Overdue" />
          <Tab label="History" />
        </Tabs>
      )}

      {loading ? (
        <CircularProgress sx={{ mt: 2 }} />
      ) : (
        <>
          <Table sx={{ mt: 2 }}>
            <TableHead>
              <TableRow>
                <TableCell>User</TableCell>
                <TableCell>Book</TableCell>
                <TableCell>Issue Date</TableCell>
                <TableCell>Return Date</TableCell>
                <TableCell>Fine</TableCell>
                <TableCell>Status</TableCell>
                {((user.role === 'USER' && tabValue === 0) ||
                  (user.role === 'ADMIN' && tabValue < 2)) && (
                  <TableCell>Actions</TableCell>
                )}
              </TableRow>
            </TableHead>
            <TableBody>{renderTableRows()}</TableBody>
          </Table>

          {/* 🔹 PAGINATION FOR USER + ADMIN */}
          <TablePagination
            component="div"
            count={data.length}
            page={page}
            onPageChange={(e, newPage) => setPage(newPage)}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={(e) => {
              setRowsPerPage(parseInt(e.target.value, 10));
              setPage(0);
            }}
            rowsPerPageOptions={[5, 10, 20]}
          />
        </>
      )}
    </Container>
  );
}

export default Issues;
