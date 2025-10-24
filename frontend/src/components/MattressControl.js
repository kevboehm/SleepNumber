import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  Slider,
  Alert,
  CircularProgress,
  Divider
} from '@mui/material';
import { Bed, Adjust } from '@mui/icons-material';
import { mattressAPI } from '../services/api';

function MattressControl({ onAdjustment }) {
  const [leftFirmness, setLeftFirmness] = useState(50);
  const [rightFirmness, setRightFirmness] = useState(50);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleAdjustBoth = async () => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await mattressAPI.adjustFirmness({
        left_firmness: leftFirmness,
        right_firmness: rightFirmness
      });

      setSuccess('Firmness adjusted successfully!');
      if (onAdjustment) {
        onAdjustment();
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to adjust firmness');
    } finally {
      setLoading(false);
    }
  };

  const handleAdjustLeft = async () => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await mattressAPI.adjustFirmness({
        side: 'left',
        firmness: leftFirmness
      });

      setSuccess('Left side adjusted successfully!');
      if (onAdjustment) {
        onAdjustment();
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to adjust left side');
    } finally {
      setLoading(false);
    }
  };

  const handleAdjustRight = async () => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await mattressAPI.adjustFirmness({
        side: 'right',
        firmness: rightFirmness
      });

      setSuccess('Right side adjusted successfully!');
      if (onAdjustment) {
        onAdjustment();
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to adjust right side');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
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

      <Grid container spacing={3}>
        {/* Left Side Control */}
        <Grid item xs={12} md={6}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Left Side
              </Typography>
              <Box sx={{ px: 2 }}>
                <Typography gutterBottom>
                  Firmness: {leftFirmness}
                </Typography>
                <Slider
                  value={leftFirmness}
                  onChange={(e, value) => setLeftFirmness(value)}
                  min={0}
                  max={100}
                  step={1}
                  marks={[
                    { value: 0, label: 'Soft' },
                    { value: 50, label: 'Medium' },
                    { value: 100, label: 'Firm' }
                  ]}
                  disabled={loading}
                />
              </Box>
              <Box sx={{ mt: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<Adjust />}
                  onClick={handleAdjustLeft}
                  disabled={loading}
                  fullWidth
                >
                  {loading ? <CircularProgress size={20} /> : 'Adjust Left Side'}
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Right Side Control */}
        <Grid item xs={12} md={6}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Right Side
              </Typography>
              <Box sx={{ px: 2 }}>
                <Typography gutterBottom>
                  Firmness: {rightFirmness}
                </Typography>
                <Slider
                  value={rightFirmness}
                  onChange={(e, value) => setRightFirmness(value)}
                  min={0}
                  max={100}
                  step={1}
                  marks={[
                    { value: 0, label: 'Soft' },
                    { value: 50, label: 'Medium' },
                    { value: 100, label: 'Firm' }
                  ]}
                  disabled={loading}
                />
              </Box>
              <Box sx={{ mt: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<Adjust />}
                  onClick={handleAdjustRight}
                  disabled={loading}
                  fullWidth
                >
                  {loading ? <CircularProgress size={20} /> : 'Adjust Right Side'}
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Both Sides Control */}
        <Grid item xs={12}>
          <Divider sx={{ my: 2 }} />
          <Box textAlign="center">
            <Button
              variant="contained"
              size="large"
              startIcon={<Bed />}
              onClick={handleAdjustBoth}
              disabled={loading}
              sx={{ minWidth: 200 }}
            >
              {loading ? <CircularProgress size={24} /> : 'Adjust Both Sides'}
            </Button>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Left: {leftFirmness} | Right: {rightFirmness}
            </Typography>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
}

export default MattressControl;
