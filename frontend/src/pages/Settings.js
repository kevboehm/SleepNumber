import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Grid,
  Divider,
  Chip
} from '@mui/material';
import { Save, TestTube, CheckCircle, Error } from '@mui/icons-material';
import { authAPI } from '../services/api';

function Settings() {
  const [credentials, setCredentials] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [connectionStatus, setConnectionStatus] = useState(null);

  useEffect(() => {
    checkCredentials();
  }, []);

  const checkCredentials = async () => {
    try {
      const response = await authAPI.getCredentials();
      setConnectionStatus(response.data.has_credentials ? 'configured' : 'not_configured');
    } catch (err) {
      console.error('Failed to check credentials:', err);
    }
  };

  const handleSaveCredentials = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await authAPI.setupCredentials(credentials.email, credentials.password);
      setSuccess('SleepNumber credentials saved successfully!');
      setConnectionStatus('configured');
      setCredentials({ email: '', password: '' }); // Clear form
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to save credentials');
    } finally {
      setLoading(false);
    }
  };

  const handleTestConnection = async () => {
    setTesting(true);
    setError('');
    setSuccess('');

    try {
      const response = await authAPI.testConnection();
      setSuccess('Connection test successful!');
      setConnectionStatus('connected');
    } catch (err) {
      setError(err.response?.data?.error || 'Connection test failed');
      setConnectionStatus('error');
    } finally {
      setTesting(false);
    }
  };

  const getStatusChip = () => {
    switch (connectionStatus) {
      case 'connected':
        return <Chip icon={<CheckCircle />} label="Connected" color="success" />;
      case 'configured':
        return <Chip icon={<CheckCircle />} label="Configured" color="primary" />;
      case 'error':
        return <Chip icon={<Error />} label="Error" color="error" />;
      default:
        return <Chip label="Not Configured" color="default" />;
    }
  };

  return (
    <Box className="page-container">
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>

      <Grid container spacing={3}>
        {/* SleepNumber Credentials */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                SleepNumber Credentials
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Enter your SleepNumber account credentials to enable automated mattress control.
                These credentials are encrypted and stored securely.
              </Typography>

              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}

              {success && (
                <Alert severity="success" sx={{ mb: 2 }}>
                  {success}
                </Alert>
              )}

              <Box component="form" onSubmit={handleSaveCredentials}>
                <TextField
                  fullWidth
                  label="SleepNumber Email"
                  type="email"
                  value={credentials.email}
                  onChange={(e) => setCredentials({ ...credentials, email: e.target.value })}
                  margin="normal"
                  required
                  disabled={loading}
                  helperText="The email address associated with your SleepNumber account"
                />
                <TextField
                  fullWidth
                  label="SleepNumber Password"
                  type="password"
                  value={credentials.password}
                  onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                  margin="normal"
                  required
                  disabled={loading}
                  helperText="Your SleepNumber account password"
                />
                <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                  <Button
                    type="submit"
                    variant="contained"
                    startIcon={<Save />}
                    disabled={loading}
                  >
                    {loading ? <CircularProgress size={20} /> : 'Save Credentials'}
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<TestTube />}
                    onClick={handleTestConnection}
                    disabled={testing || connectionStatus === 'not_configured'}
                  >
                    {testing ? <CircularProgress size={20} /> : 'Test Connection'}
                  </Button>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Connection Status */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Connection Status
              </Typography>
              <Box sx={{ mb: 2 }}>
                {getStatusChip()}
              </Box>
              <Typography variant="body2" color="text.secondary">
                {connectionStatus === 'connected' && 'Your mattress is connected and ready for automation.'}
                {connectionStatus === 'configured' && 'Credentials are saved. Test the connection to verify.'}
                {connectionStatus === 'error' && 'There was an error connecting to your mattress. Check your credentials.'}
                {connectionStatus === 'not_configured' && 'No credentials configured yet.'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* App Information */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                About SleepNumber Automation
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                This application allows you to automate your SleepNumber mattress firmness adjustments
                based on schedules you create. You can set different firmness levels for different
                times of day and days of the week.
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                <strong>Features:</strong>
              </Typography>
              <Typography variant="body2" color="text.secondary" component="div">
                <ul>
                  <li>Automated firmness scheduling</li>
                  <li>Independent left/right side control</li>
                  <li>Manual mattress control</li>
                  <li>Adjustment history and logs</li>
                  <li>Secure credential storage</li>
                </ul>
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Settings;
