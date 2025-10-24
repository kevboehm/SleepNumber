import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Grid,
  Alert,
  CircularProgress,
  Pagination,
  IconButton,
  Tooltip
} from '@mui/material';
import { Refresh, FilterList, Clear } from '@mui/icons-material';
import { logsAPI } from '../services/api';

function Logs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [stats, setStats] = useState(null);
  
  // Filters
  const [filters, setFilters] = useState({
    side: '',
    status: '',
    days: 30
  });
  
  // Pagination
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 50,
    total: 0,
    pages: 0
  });

  useEffect(() => {
    loadLogs();
    loadStats();
  }, [filters, pagination.page]);

  const loadLogs = async () => {
    try {
      setLoading(true);
      const params = {
        page: pagination.page,
        per_page: pagination.per_page,
        ...filters
      };
      
      const response = await logsAPI.getLogs(params);
      setLogs(response.data.logs);
      setPagination(response.data.pagination);
    } catch (err) {
      setError('Failed to load logs');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await logsAPI.getLogStats(filters.days);
      setStats(response.data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
    setPagination(prev => ({ ...prev, page: 1 })); // Reset to first page
  };

  const clearFilters = () => {
    setFilters({
      side: '',
      status: '',
      days: 30
    });
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handlePageChange = (event, page) => {
    setPagination(prev => ({ ...prev, page }));
  };

  const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusChip = (status) => {
    const statusConfig = {
      success: { color: 'success', label: 'Success' },
      failed: { color: 'error', label: 'Failed' },
      pending: { color: 'warning', label: 'Pending' }
    };
    
    const config = statusConfig[status] || { color: 'default', label: status };
    return <Chip label={config.label} color={config.color} size="small" />;
  };

  const getSideChip = (side) => {
    return (
      <Chip 
        label={side.charAt(0).toUpperCase() + side.slice(1)} 
        color={side === 'left' ? 'primary' : 'secondary'} 
        size="small" 
      />
    );
  };

  if (loading && logs.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box className="page-container">
      <Typography variant="h4" gutterBottom>
        Adjustment Logs
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Statistics */}
        {stats && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Statistics (Last {stats.period_days} days)
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={3}>
                    <Typography variant="h4" color="primary">
                      {stats.total_adjustments}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Adjustments
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={3}>
                    <Typography variant="h4" color="success.main">
                      {stats.success_rate}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Success Rate
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={3}>
                    <Typography variant="h4" color="primary">
                      {stats.adjustments_by_side.left}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Left Side Adjustments
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={3}>
                    <Typography variant="h4" color="secondary.main">
                      {stats.adjustments_by_side.right}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Right Side Adjustments
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Filters */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} sx={{ mb: 2 }}>
                <FilterList />
                <Typography variant="h6">
                  Filters
                </Typography>
                <Box sx={{ flexGrow: 1 }} />
                <Button
                  variant="outlined"
                  startIcon={<Refresh />}
                  onClick={loadLogs}
                  disabled={loading}
                >
                  Refresh
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Clear />}
                  onClick={clearFilters}
                >
                  Clear
                </Button>
              </Box>
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={4}>
                  <FormControl fullWidth>
                    <InputLabel>Side</InputLabel>
                    <Select
                      value={filters.side}
                      onChange={(e) => handleFilterChange('side', e.target.value)}
                    >
                      <MenuItem value="">All Sides</MenuItem>
                      <MenuItem value="left">Left Side</MenuItem>
                      <MenuItem value="right">Right Side</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <FormControl fullWidth>
                    <InputLabel>Status</InputLabel>
                    <Select
                      value={filters.status}
                      onChange={(e) => handleFilterChange('status', e.target.value)}
                    >
                      <MenuItem value="">All Statuses</MenuItem>
                      <MenuItem value="success">Success</MenuItem>
                      <MenuItem value="failed">Failed</MenuItem>
                      <MenuItem value="pending">Pending</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    label="Days"
                    type="number"
                    value={filters.days}
                    onChange={(e) => handleFilterChange('days', parseInt(e.target.value) || 30)}
                    inputProps={{ min: 1, max: 365 }}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Logs Table */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Adjustment History
              </Typography>
              
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Timestamp</TableCell>
                      <TableCell>Side</TableCell>
                      <TableCell>Firmness</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Error Message</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {logs.map((log) => (
                      <TableRow key={log.id}>
                        <TableCell>
                          {formatDateTime(log.executed_at)}
                        </TableCell>
                        <TableCell>
                          {getSideChip(log.side)}
                        </TableCell>
                        <TableCell>
                          {log.firmness}
                        </TableCell>
                        <TableCell>
                          {getStatusChip(log.status)}
                        </TableCell>
                        <TableCell>
                          {log.error_message ? (
                            <Tooltip title={log.error_message}>
                              <Typography 
                                variant="body2" 
                                color="error"
                                sx={{ 
                                  maxWidth: 200, 
                                  overflow: 'hidden', 
                                  textOverflow: 'ellipsis',
                                  whiteSpace: 'nowrap'
                                }}
                              >
                                {log.error_message}
                              </Typography>
                            </Tooltip>
                          ) : (
                            '-'
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              {logs.length === 0 && !loading && (
                <Box textAlign="center" sx={{ py: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    No logs found for the selected filters.
                  </Typography>
                </Box>
              )}

              {pagination.pages > 1 && (
                <Box display="flex" justifyContent="center" sx={{ mt: 2 }}>
                  <Pagination
                    count={pagination.pages}
                    page={pagination.page}
                    onChange={handlePageChange}
                    color="primary"
                  />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Logs;
