import { useEffect, useState } from 'react';
import { Container, Typography, Grid, Card, CardContent } from '@mui/material';
import { useAuth } from '../context/AuthContext';
import { getUserDashboard, getAdminSummary } from '../services/api';

function Dashboard() {
  const { user } = useAuth();
  const [data, setData] = useState({});

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = user.role === 'ADMIN' ? await getAdminSummary() : await getUserDashboard();
        setData(response.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchData();
  }, [user]);

  return (
    <Container>
      <Typography variant="h4" gutterBottom>Dashboard</Typography>
      <Grid container spacing={2}>
        {user.role === 'USER' ? (
          <>
            <Grid item xs={12} sm={6}><Card><CardContent><Typography>Currently Issued: {data.currentlyIssued}</Typography></CardContent></Card></Grid>
            <Grid item xs={12} sm={6}><Card><CardContent><Typography>Pending Issues: {data.pendingIssueRequests}</Typography></CardContent></Card></Grid>
            <Grid item xs={12} sm={6}><Card><CardContent><Typography>Pending Returns: {data.pendingReturnRequests}</Typography></CardContent></Card></Grid>
            <Grid item xs={12} sm={6}><Card><CardContent><Typography>Overdue Books: {data.overdueBooks}</Typography></CardContent></Card></Grid>
            <Grid item xs={12}><Card><CardContent><Typography>Total Fine: ${data.totalFine}</Typography></CardContent></Card></Grid>
          </>
        ) : (
          <>
            <Grid item xs={12} sm={6}><Card><CardContent><Typography>Total Users: {data.total_users}</Typography></CardContent></Card></Grid>
            <Grid item xs={12} sm={6}><Card><CardContent><Typography>Total Books: {data.total_books}</Typography></CardContent></Card></Grid>
            <Grid item xs={12} sm={6}><Card><CardContent><Typography>Issued Books: {data.issued_books}</Typography></CardContent></Card></Grid>
            <Grid item xs={12} sm={6}><Card><CardContent><Typography>Pending Issues: {data.pending_issue_requests}</Typography></CardContent></Card></Grid>
            <Grid item xs={12}><Card><CardContent><Typography>Pending Returns: {data.pending_return_approved}</Typography></CardContent></Card></Grid>
          </>
        )}
      </Grid>
    </Container>
  );
}

export default Dashboard;