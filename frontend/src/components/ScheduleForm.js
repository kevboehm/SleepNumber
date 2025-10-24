import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Button,
  Grid,
  Typography,
  Chip,
  IconButton
} from '@mui/material';
import { TimePicker } from '@mui/x-date-pickers/TimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import dayjs from 'dayjs';
import { Add, Remove } from '@mui/icons-material';
import { schedulesAPI } from '../services/api';

const DAYS_OF_WEEK = [
  { value: 0, label: 'Monday' },
  { value: 1, label: 'Tuesday' },
  { value: 2, label: 'Wednesday' },
  { value: 3, label: 'Thursday' },
  { value: 4, label: 'Friday' },
  { value: 5, label: 'Saturday' },
  { value: 6, label: 'Sunday' }
];

function ScheduleForm({ schedule, onClose, onSave }) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    time: dayjs().hour(22).minute(0), // Default to 10:00 PM
    left_firmness: null,
    right_firmness: null,
    apply_to_sides: 'both',
    enabled: true,
    days_of_week: [0, 1, 2, 3, 4, 5, 6] // All days by default
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (schedule) {
      setFormData({
        name: schedule.name || '',
        description: schedule.description || '',
        time: dayjs().hour(parseInt(schedule.time.split(':')[0])).minute(parseInt(schedule.time.split(':')[1])),
        left_firmness: schedule.left_firmness,
        right_firmness: schedule.right_firmness,
        apply_to_sides: schedule.apply_to_sides || 'both',
        enabled: schedule.enabled !== false,
        days_of_week: schedule.days_of_week || [0, 1, 2, 3, 4, 5, 6]
      });
    }
  }, [schedule]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const submitData = {
        ...formData,
        time: formData.time.format('HH:mm'),
        days_of_week: formData.days_of_week.length === 7 ? null : formData.days_of_week
      };

      if (schedule) {
        await schedulesAPI.updateSchedule(schedule.id, submitData);
      } else {
        await schedulesAPI.createSchedule(submitData);
      }

      onSave();
      onClose();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to save schedule');
    } finally {
      setLoading(false);
    }
  };

  const handleDayToggle = (day) => {
    setFormData(prev => ({
      ...prev,
      days_of_week: prev.days_of_week.includes(day)
        ? prev.days_of_week.filter(d => d !== day)
        : [...prev.days_of_week, day].sort()
    }));
  };

  const handleSelectAllDays = () => {
    setFormData(prev => ({
      ...prev,
      days_of_week: [0, 1, 2, 3, 4, 5, 6]
    }));
  };

  const handleClearAllDays = () => {
    setFormData(prev => ({
      ...prev,
      days_of_week: []
    }));
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Box component="form" onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Schedule Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              disabled={loading}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Description (Optional)"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              multiline
              rows={2}
              disabled={loading}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TimePicker
              label="Time"
              value={formData.time}
              onChange={(newTime) => setFormData({ ...formData, time: newTime })}
              disabled={loading}
              renderInput={(params) => <TextField {...params} fullWidth />}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Apply To</InputLabel>
              <Select
                value={formData.apply_to_sides}
                onChange={(e) => setFormData({ ...formData, apply_to_sides: e.target.value })}
                disabled={loading}
              >
                <MenuItem value="left">Left Side Only</MenuItem>
                <MenuItem value="right">Right Side Only</MenuItem>
                <MenuItem value="both">Both Sides</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          {(formData.apply_to_sides === 'left' || formData.apply_to_sides === 'both') && (
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Left Side Firmness"
                type="number"
                value={formData.left_firmness || ''}
                onChange={(e) => setFormData({ ...formData, left_firmness: e.target.value ? parseInt(e.target.value) : null })}
                inputProps={{ min: 0, max: 100 }}
                disabled={loading}
                helperText="0-100 (0 = softest, 100 = firmest)"
              />
            </Grid>
          )}

          {(formData.apply_to_sides === 'right' || formData.apply_to_sides === 'both') && (
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Right Side Firmness"
                type="number"
                value={formData.right_firmness || ''}
                onChange={(e) => setFormData({ ...formData, right_firmness: e.target.value ? parseInt(e.target.value) : null })}
                inputProps={{ min: 0, max: 100 }}
                disabled={loading}
                helperText="0-100 (0 = softest, 100 = firmest)"
              />
            </Grid>
          )}

          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Days of Week
            </Typography>
            <Box display="flex" flexWrap="wrap" gap={1} sx={{ mb: 2 }}>
              <Button
                size="small"
                variant="outlined"
                onClick={handleSelectAllDays}
                disabled={loading}
              >
                All Days
              </Button>
              <Button
                size="small"
                variant="outlined"
                onClick={handleClearAllDays}
                disabled={loading}
              >
                Clear All
              </Button>
            </Box>
            <Box display="flex" flexWrap="wrap" gap={1}>
              {DAYS_OF_WEEK.map((day) => (
                <Chip
                  key={day.value}
                  label={day.label}
                  clickable
                  color={formData.days_of_week.includes(day.value) ? 'primary' : 'default'}
                  onClick={() => handleDayToggle(day.value)}
                  disabled={loading}
                />
              ))}
            </Box>
          </Grid>

          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.enabled}
                  onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
                  disabled={loading}
                />
              }
              label="Enable Schedule"
            />
          </Grid>

          {error && (
            <Grid item xs={12}>
              <Typography color="error" variant="body2">
                {error}
              </Typography>
            </Grid>
          )}

          <Grid item xs={12}>
            <Box display="flex" gap={2} justifyContent="flex-end">
              <Button
                variant="outlined"
                onClick={onClose}
                disabled={loading}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="contained"
                disabled={loading}
              >
                {loading ? 'Saving...' : (schedule ? 'Update' : 'Create')}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Box>
    </LocalizationProvider>
  );
}

export default ScheduleForm;
