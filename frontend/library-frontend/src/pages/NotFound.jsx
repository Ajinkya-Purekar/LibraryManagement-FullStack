import { Container, Typography, Button } from '@mui/material';
import { Link } from 'react-router-dom';

function NotFound() {
  return (
    <Container style={{ textAlign: 'center', marginTop: '50px' }}>
      <Typography variant="h1" color="error">404</Typography>
      <Typography variant="h5" gutterBottom>Page Not Found</Typography>
      <Typography variant="body1" gutterBottom>The page you're looking for doesn't exist.</Typography>
      <Button variant="contained" component={Link} to="/dashboard">Go to Dashboard</Button>
    </Container>
  );
}

export default NotFound;