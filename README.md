# SleepNumber Automation Webapp

A modern web application for automating your SleepNumber KingP6 mattress firmness adjustments with scheduling and logging capabilities.

## Features

- **Automated Scheduling**: Set daily recurring schedules for mattress firmness adjustments
- **Dual-Side Control**: Independent control of left and right mattress sides
- **Manual Control**: Real-time manual adjustment of mattress firmness
- **Comprehensive Logging**: Track all adjustment attempts with success/failure status
- **Secure Authentication**: User accounts with encrypted SleepNumber credential storage
- **Modern UI**: Beautiful, responsive interface built with React and Material-UI

## Architecture

- **Backend**: Python Flask API with sleepyq library integration
- **Frontend**: React with Material-UI components
- **Database**: SQLite (development) / PostgreSQL (production)
- **Scheduler**: APScheduler for cron-based automation
- **Deployment**: Render.com (backend) + Vercel/Netlify (frontend)

## Prerequisites

- Python 3.11+
- Node.js 18+
- SleepNumber account with SleepIQ enabled
- Git

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/kevboehm/SleepNumber.git
cd SleepNumber
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Set environment variables
export FLASK_ENV=development
export SECRET_KEY=your-secret-key-here
export JWT_SECRET_KEY=your-jwt-secret-here
export ENCRYPTION_KEY=your-encryption-key-here

# Run the backend
python app.py
```

The backend will be available at `http://localhost:5000`

### 3. Frontend Setup

```bash
# In a new terminal
cd frontend
npm install

# Set environment variable
export REACT_APP_API_URL=http://localhost:5000/api

# Run the frontend
npm start
```

The frontend will be available at `http://localhost:3000`

## Deployment

### Option 1: Render.com (Recommended)

1. **Fork this repository** to your GitHub account
2. **Connect to Render.com**:
   - Go to [render.com](https://render.com)
   - Sign up/login with GitHub
   - Click "New +" → "Blueprint"
   - Connect your forked repository
   - Render will automatically detect the `render.yaml` configuration

3. **Configure Environment Variables**:
   - In Render dashboard, go to your backend service
   - Add these environment variables:
     - `FLASK_ENV=production`
     - `SECRET_KEY` (generate a secure random string)
     - `JWT_SECRET_KEY` (generate a secure random string)
     - `ENCRYPTION_KEY` (generate a secure random string)
     - `ADMIN_PASSWORD` (set a secure password)

4. **Deploy Frontend**:
   - The frontend will automatically deploy as a static site
   - Update the `REACT_APP_API_URL` environment variable to point to your backend URL

### Option 2: Manual Deployment

#### Backend (Render.com)

1. Create a new Web Service on Render.com
2. Connect your GitHub repository
3. Set build command: `pip install -r backend/requirements.txt`
4. Set start command: `cd backend && python app.py`
5. Add PostgreSQL database
6. Configure environment variables as above

#### Frontend (Vercel)

1. Go to [vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Set build command: `cd frontend && npm install && npm run build`
4. Set output directory: `frontend/build`
5. Add environment variable: `REACT_APP_API_URL=https://your-backend-url.com/api`

## Usage

### 1. Initial Setup

1. **Register/Login**: Create an account or login to the webapp
2. **Configure SleepNumber Credentials**: 
   - Go to Settings page
   - Enter your SleepNumber email and password
   - Test the connection to verify credentials work
3. **Create Your First Schedule**:
   - Go to Dashboard
   - Click "Add Schedule"
   - Set time, firmness levels, and days of week
   - Enable the schedule

### 2. Managing Schedules

- **Create Schedule**: Set time, firmness levels for left/right sides, and days
- **Edit Schedule**: Modify existing schedules
- **Enable/Disable**: Toggle schedules on/off without deleting
- **Delete Schedule**: Remove schedules permanently

### 3. Manual Control

- Use the Manual Control panel on the Dashboard
- Adjust firmness for individual sides or both sides
- Real-time adjustment with immediate feedback

### 4. Monitoring

- **Logs Page**: View all adjustment attempts with timestamps and status
- **Statistics**: See success rates and adjustment counts
- **Filtering**: Filter logs by side, status, and time period

## API Documentation

### Authentication Endpoints

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/profile` - Get user profile
- `POST /api/auth/setup-credentials` - Store SleepNumber credentials
- `POST /api/auth/test-connection` - Test SleepNumber connection

### Schedule Endpoints

- `GET /api/schedules/` - Get all schedules
- `POST /api/schedules/` - Create new schedule
- `GET /api/schedules/{id}` - Get specific schedule
- `PUT /api/schedules/{id}` - Update schedule
- `DELETE /api/schedules/{id}` - Delete schedule
- `POST /api/schedules/{id}/toggle` - Enable/disable schedule

### Mattress Endpoints

- `GET /api/mattress/status` - Get mattress status
- `POST /api/mattress/adjust` - Adjust firmness
- `POST /api/mattress/test` - Test connection

### Log Endpoints

- `GET /api/logs/` - Get adjustment logs
- `GET /api/logs/stats` - Get log statistics
- `GET /api/logs/{id}` - Get specific log entry

## Security

- **Encrypted Storage**: SleepNumber credentials are encrypted using Fernet encryption
- **JWT Authentication**: Secure token-based authentication
- **HTTPS**: All production deployments use HTTPS
- **Environment Variables**: Sensitive data stored in environment variables

## Troubleshooting

### Common Issues

1. **Connection Failed**: 
   - Verify SleepNumber credentials are correct
   - Ensure your mattress is connected to WiFi
   - Check that SleepIQ is enabled on your mattress

2. **Schedule Not Running**:
   - Verify schedule is enabled
   - Check that current time matches schedule time
   - Ensure days of week are configured correctly

3. **Frontend Not Loading**:
   - Check that `REACT_APP_API_URL` environment variable is set correctly
   - Verify backend is running and accessible

### Debug Mode

Enable debug logging by setting `FLASK_ENV=development` in your environment variables.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Commit your changes: `git commit -m 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section above
- Review the API documentation

## Acknowledgments

- [sleepyq](https://github.com/technicalpickles/sleepyq) - Python library for SleepIQ API
- SleepNumber for their innovative mattress technology
- Material-UI for the beautiful React components
