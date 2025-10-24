const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const bcrypt = require('bcryptjs');

const DB_PATH = path.join(__dirname, '..', 'data', 'sleepnumber.db');

let db;

function getDatabase() {
  if (!db) {
    db = new sqlite3.Database(DB_PATH);
  }
  return db;
}

async function initializeDatabase() {
  return new Promise((resolve, reject) => {
    const database = getDatabase();
    
    // Enable foreign keys
    database.run('PRAGMA foreign_keys = ON');
    
    // Create users table
    database.run(`
      CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);
    
    // Create schedules table
    database.run(`
      CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        time TEXT NOT NULL,
        firmness_level INTEGER NOT NULL CHECK (firmness_level >= 0 AND firmness_level <= 100),
        side TEXT NOT NULL CHECK (side IN ('left', 'right', 'both')),
        enabled BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
      )
    `);
    
    // Create adjustment_logs table
    database.run(`
      CREATE TABLE IF NOT EXISTS adjustment_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        schedule_id INTEGER,
        firmness_level INTEGER NOT NULL,
        side TEXT NOT NULL,
        status TEXT NOT NULL CHECK (status IN ('success', 'failed', 'pending')),
        error_message TEXT,
        executed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (schedule_id) REFERENCES schedules (id) ON DELETE SET NULL
      )
    `);
    
    // Create mattress_settings table
    database.run(`
      CREATE TABLE IF NOT EXISTS mattress_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        sleepnumber_email TEXT,
        sleepnumber_password TEXT,
        ifttt_webhook_key TEXT,
        bed_id TEXT,
        api_endpoint TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
      )
    `);
    
    // Create indexes for better performance
    database.run('CREATE INDEX IF NOT EXISTS idx_schedules_user_id ON schedules(user_id)');
    database.run('CREATE INDEX IF NOT EXISTS idx_schedules_time ON schedules(time)');
    database.run('CREATE INDEX IF NOT EXISTS idx_logs_user_id ON adjustment_logs(user_id)');
    database.run('CREATE INDEX IF NOT EXISTS idx_logs_executed_at ON adjustment_logs(executed_at)');
    
    // Create default admin user if it doesn't exist
    database.get('SELECT id FROM users WHERE username = ?', ['admin'], (err, row) => {
      if (err) {
        reject(err);
        return;
      }
      
      if (!row) {
        const defaultPassword = process.env.ADMIN_PASSWORD || 'admin123';
        const hashedPassword = bcrypt.hashSync(defaultPassword, 10);
        
        database.run(
          'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
          ['admin', 'admin@sleepnumber.local', hashedPassword],
          function(err) {
            if (err) {
              reject(err);
            } else {
              console.log('Default admin user created');
              resolve();
            }
          }
        );
      } else {
        resolve();
      }
    });
  });
}

function closeDatabase() {
  if (db) {
    db.close((err) => {
      if (err) {
        console.error('Error closing database:', err);
      } else {
        console.log('Database connection closed');
      }
    });
  }
}

module.exports = {
  getDatabase,
  initializeDatabase,
  closeDatabase
};
