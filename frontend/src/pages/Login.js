import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
  Container
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`auth-tabpanel-${index}`}
      aria-labelledby={`auth-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function Login() {
  const { login, register } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Login form state
  const [loginForm, setLoginForm] = useState({
    username: '',
    password: ''
  });

  // Register form state
  const [registerForm, setRegisterForm] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    setError('');
    setSuccess('');
  };

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    const result = await login(loginForm.username, loginForm.password);
    
    if (result.success) {
      setSuccess('Login successful!');
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    // Validate passwords match
    if (registerForm.password !== registerForm.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    const result = await register(registerForm.username, registerForm.email, registerForm.password);
    
    if (result.success) {
      setSuccess('Registration successful!');
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 8 }}>
      <Card>
        <CardContent>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            SleepNumber Automation
          </Typography>
          <Typography variant="body1" color="text.secondary" align="center" sx={{ mb: 3 }}>
            Control your mattress firmness with automated scheduling
          </Typography>

          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={handleTabChange} centered>
              <Tab label="Login" />
              <Tab label="Register" />
            </Tabs>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}

          {success && (
            <Alert severity="success" sx={{ mt: 2 }}>
              {success}
            </Alert>
          )}

          <TabPanel value={tabValue} index={0}>
            <Box component="form" onSubmit={handleLoginSubmit}>
              <TextField
                fullWidth
                label="Username or Email"
                value={loginForm.username}
                onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
                margin="normal"
                required
                disabled={loading}
              />
              <TextField
                fullWidth
                label="Password"
                type="password"
                value={loginForm.password}
                onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                margin="normal"
                required
                disabled={loading}
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Login'}
              </Button>
            </Box>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <Box component="form" onSubmit={handleRegisterSubmit}>
              <TextField
                fullWidth
                label="Username"
                value={registerForm.username}
                onChange={(e) => setRegisterForm({ ...registerForm, username: e.target.value })}
                margin="normal"
                required
                disabled={loading}
              />
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={registerForm.email}
                onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })}
                margin="normal"
                required
                disabled={loading}
              />
              <TextField
                fullWidth
                label="Password"
                type="password"
                value={registerForm.password}
                onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })}
                margin="normal"
                required
                disabled={loading}
              />
              <TextField
                fullWidth
                label="Confirm Password"
                type="password"
                value={registerForm.confirmPassword}
                onChange={(e) => setRegisterForm({ ...registerForm, confirmPassword: e.target.value })}
                margin="normal"
                required
                disabled={loading}
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Register'}
              </Button>
            </Box>
          </TabPanel>
        </CardContent>
      </Card>
    </Container>
  );
}

export default Login;
