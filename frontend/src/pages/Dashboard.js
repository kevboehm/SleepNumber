import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Schedule,
  Bed,
  History,
  Settings,
  PlayArrow,
  Pause
} from '@mui/icons-material';
import { schedulesAPI, mattressAPI } from '../services/api';
import ScheduleForm from '../components/ScheduleForm';
import MattressControl from '../components/MattressControl';

function Dashboard() {
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showScheduleForm, setShowScheduleForm] = useState(false);
  const [editingSchedule, setEditingSchedule] = useState(null);
  const [mattressStatus, setMattressStatus] = useState(null);

  useEffect(() => {
    loadSchedules();
    loadMattressStatus();
  }, []);

  const loadSchedules = async () => {
    try {
      const response = await schedulesAPI.getSchedules();
      setSchedules(response.data.schedules);
    } catch (err) {
      setError('Failed to load schedules');
    } finally {
      setLoading(false);
    }
  };

  const loadMattressStatus = async () => {
    try {
      const response = await mattressAPI.getStatus();
      setMattressStatus(response.data);
    } catch (err) {
      console.error('Failed to load mattress status:', err);
    }
  };

  const handleCreateSchedule = () => {
    setEditingSchedule(null);
    setShowScheduleForm(true);
  };

  const handleEditSchedule = (schedule) => {
    setEditingSchedule(schedule);
    setShowScheduleForm(true);
  };

  const handleDeleteSchedule = async (scheduleId) => {
    if (window.confirm('Are you sure you want to delete this schedule?')) {
      try {
        await schedulesAPI.deleteSchedule(scheduleId);
        loadSchedules();
      } catch (err) {
        setError('Failed to delete schedule');
      }
    }
  };

  const handleToggleSchedule = async (scheduleId) => {
    try {
      await schedulesAPI.toggleSchedule(scheduleId);
      loadSchedules();
    } catch (err) {
      setError('Failed to toggle schedule');
    }
  };

  const handleScheduleFormClose = () => {
    setShowScheduleForm(false);
    setEditingSchedule(null);
    loadSchedules();
  };

  const formatTime = (time) => {
    const [hours, minutes] = time.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
  };

  const getDaysText = (daysOfWeek) => {
    if (!daysOfWeek || daysOfWeek.length === 7) {
      return 'Every day';
    }
    
    const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    if (daysOfWeek.length === 0) {
      return 'Never';
    }
    
    return daysOfWeek.map(day => dayNames[day]).join(', ');
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box className="page-container">
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Box display="flex" flexDirection="column" gap={2}>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  onClick={handleCreateSchedule}
                  fullWidth
                >
                  New Schedule
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Bed />}
                  onClick={loadMattressStatus}
                  fullWidth
                >
                  Check Mattress Status
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Mattress Status */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Mattress Status
              </Typography>
              {mattressStatus ? (
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Last updated: {new Date(mattressStatus.timestamp).toLocaleString()}
                  </Typography>
                  <Typography variant="body1" sx={{ mt: 1 }}>
                    Connection: <Chip label="Connected" color="success" size="small" />
                  </Typography>
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Click "Check Mattress Status" to see current information
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Manual Control */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Manual Control
              </Typography>
              <MattressControl onAdjustment={loadMattressStatus} />
            </CardContent>
          </Card>
        </Grid>

        {/* Schedules */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                <Typography variant="h6">
                  Schedules ({schedules.length})
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  onClick={handleCreateSchedule}
                >
                  Add Schedule
                </Button>
              </Box>

              {schedules.length === 0 ? (
                <Typography variant="body2" color="text.secondary" align="center" sx={{ py: 4 }}>
                  No schedules created yet. Click "Add Schedule" to create your first automated schedule.
                </Typography>
              ) : (
                <List>
                  {schedules.map((schedule) => (
                    <ListItem key={schedule.id} divider>
                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" gap={1}>
                            <Typography variant="subtitle1">
                              {schedule.name}
                            </Typography>
                            <Chip
                              label={schedule.enabled ? 'Enabled' : 'Disabled'}
                              color={schedule.enabled ? 'success' : 'default'}
                              size="small"
                            />
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Time: {formatTime(schedule.time)} | Days: {getDaysText(schedule.days_of_week)}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {schedule.apply_to_sides === 'both' ? (
                                `Left: ${schedule.left_firmness || 'N/A'}, Right: ${schedule.right_firmness || 'N/A'}`
                              ) : (
                                `${schedule.apply_to_sides}: ${schedule[`${schedule.apply_to_sides}_firmness`] || 'N/A'}`
                              )}
                            </Typography>
                            {schedule.description && (
                              <Typography variant="body2" color="text.secondary">
                                {schedule.description}
                              </Typography>
                            )}
                          </Box>
                        }
                      />
                      <ListItemSecondaryAction>
                        <Box display="flex" gap={1}>
                          <IconButton
                            size="small"
                            onClick={() => handleToggleSchedule(schedule.id)}
                            title={schedule.enabled ? 'Disable' : 'Enable'}
                          >
                            {schedule.enabled ? <Pause /> : <PlayArrow />}
                          </IconButton>
                          <IconButton
                            size="small"
                            onClick={() => handleEditSchedule(schedule)}
                            title="Edit"
                          >
                            <Edit />
                          </IconButton>
                          <IconButton
                            size="small"
                            onClick={() => handleDeleteSchedule(schedule.id)}
                            title="Delete"
                            color="error"
                          >
                            <Delete />
                          </IconButton>
                        </Box>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Schedule Form Dialog */}
      <Dialog
        open={showScheduleForm}
        onClose={handleScheduleFormClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editingSchedule ? 'Edit Schedule' : 'Create New Schedule'}
        </DialogTitle>
        <DialogContent>
          <ScheduleForm
            schedule={editingSchedule}
            onClose={handleScheduleFormClose}
            onSave={loadSchedules}
          />
        </DialogContent>
      </Dialog>
    </Box>
  );
}

export default Dashboard;
