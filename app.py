#!/usr/bin/env python3
"""
Flask Web Dashboard untuk Monitoring Tunnel Mikrotik
Untuk deployment di Railway
"""

from flask import Flask, render_template, jsonify, request
import socket
import time
import subprocess
import json
import os
import re
from datetime import datetime, timedelta
from threading import Thread, Lock
import logging
import sqlite3
from contextlib import contextmanager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting untuk responsible monitoring
last_check_time = {}
rate_limit_lock = Lock()

class TunnelHistoryDB:
    """Database untuk menyimpan history tunnel status dan downtime"""

    def __init__(self, db_path="tunnel_history.db"):
        self.db_path = db_path
        self.init_database()

    @contextmanager
    def get_db_connection(self):
        """Context manager untuk database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def init_database(self):
        """Initialize database tables"""
        with self.get_db_connection() as conn:
            # Table untuk status history
            conn.execute('''
                CREATE TABLE IF NOT EXISTS tunnel_status_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tunnel_name TEXT NOT NULL,
                    host TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    response_time REAL,
                    error_message TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Table untuk downtime events
            conn.execute('''
                CREATE TABLE IF NOT EXISTS downtime_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tunnel_name TEXT NOT NULL,
                    host TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    down_start DATETIME NOT NULL,
                    down_end DATETIME,
                    duration_seconds INTEGER,
                    is_resolved BOOLEAN DEFAULT FALSE,
                    error_message TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Index untuk performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_tunnel_timestamp ON tunnel_status_history(tunnel_name, timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_downtime_tunnel ON downtime_events(tunnel_name, down_start)')

            conn.commit()

    def log_tunnel_status(self, tunnel_name, host, port, status, response_time=None, error_message=None):
        """Log status tunnel ke database"""
        with self.get_db_connection() as conn:
            conn.execute('''
                INSERT INTO tunnel_status_history
                (tunnel_name, host, port, status, response_time, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (tunnel_name, host, port, status, response_time, error_message))
            conn.commit()

    def start_downtime_event(self, tunnel_name, host, port, error_message=None):
        """Start tracking downtime event"""
        with self.get_db_connection() as conn:
            # Check if there's already an unresolved downtime
            existing = conn.execute('''
                SELECT id FROM downtime_events
                WHERE tunnel_name = ? AND is_resolved = FALSE
                ORDER BY down_start DESC LIMIT 1
            ''', (tunnel_name,)).fetchone()

            if not existing:
                conn.execute('''
                    INSERT INTO downtime_events
                    (tunnel_name, host, port, down_start, error_message)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?)
                ''', (tunnel_name, host, port, error_message))
                conn.commit()
                return True
            return False

    def end_downtime_event(self, tunnel_name):
        """End downtime event and calculate duration"""
        with self.get_db_connection() as conn:
            # Find unresolved downtime
            downtime = conn.execute('''
                SELECT id, down_start FROM downtime_events
                WHERE tunnel_name = ? AND is_resolved = FALSE
                ORDER BY down_start DESC LIMIT 1
            ''', (tunnel_name,)).fetchone()

            if downtime:
                # Calculate duration
                down_start = datetime.fromisoformat(downtime['down_start'])
                down_end = datetime.now()
                duration = int((down_end - down_start).total_seconds())

                conn.execute('''
                    UPDATE downtime_events
                    SET down_end = CURRENT_TIMESTAMP,
                        duration_seconds = ?,
                        is_resolved = TRUE
                    WHERE id = ?
                ''', (duration, downtime['id']))
                conn.commit()
                return duration
            return None

app = Flask(__name__)

# Global variables untuk menyimpan status
tunnel_status = {}
status_lock = Lock()
last_update = None

class TunnelMonitor:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.tunnels = []
        self.settings = {}
        self.load_config()
        self.history_db = TunnelHistoryDB()
        self.previous_status = {}  # Track previous status untuk detect changes
    
    def load_config(self):
        """Load konfigurasi tunnel"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.tunnels = config.get('tunnels', [])
                self.settings = config.get('settings', {})
                logger.info(f"Loaded {len(self.tunnels)} tunnels from config")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.tunnels = []
            self.settings = {}
    
    def is_rate_limited(self, host: str, port: int) -> bool:
        """Check if we should rate limit requests to avoid being seen as attack"""
        with rate_limit_lock:
            key = f"{host}:{port}"
            current_time = time.time()
            min_interval = self.settings.get('rate_limit_delay', 1)

            if key in last_check_time:
                time_since_last = current_time - last_check_time[key]
                if time_since_last < min_interval:
                    logger.info(f"Rate limiting {key} - too soon since last check")
                    return True

            last_check_time[key] = current_time
            return False

    def quick_tcp_check(self, host: str, port: int, timeout: int = 5) -> dict:
        """Quick TCP connection check with fast mode optimization"""
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Fast mode: shorter timeout for quicker response
            actual_timeout = min(timeout, self.settings.get('timeout', 5))
            sock.settimeout(actual_timeout)

            result = sock.connect_ex((host, port))
            end_time = time.time()

            if result == 0:
                response_time = round((end_time - start_time) * 1000, 2)
                sock.close()
                return {"status": "online", "time": response_time, "error": None}
            else:
                sock.close()
                return {"status": "offline", "time": None, "error": f"Connection failed"}

        except Exception as e:
            return {"status": "error", "time": None, "error": str(e)}
    
    def quick_ping(self, host: str) -> dict:
        """Quick ping test with fast mode optimization"""
        try:
            # Fast mode: reduced ping count for quicker response
            ping_count = self.settings.get('ping_count', 2)
            ping_timeout = min(self.settings.get('timeout', 5), 6)

            # Detect OS and use appropriate ping command
            if os.name == 'nt':  # Windows
                cmd = ["ping", "-n", str(ping_count), "-w", "3000", host]
            else:  # Linux/Unix
                cmd = ["ping", "-c", str(ping_count), "-W", "3", host]

            process = subprocess.run(cmd, capture_output=True, text=True, timeout=ping_timeout)

            if process.returncode == 0:
                output = process.stdout
                # Parse response time
                if os.name == 'nt':  # Windows
                    time_match = re.search(r'time[<=](\d+)ms', output)
                else:  # Linux
                    time_match = re.search(r'time=(\d+\.?\d*).*ms', output)

                if time_match:
                    ping_time = float(time_match.group(1))
                    return {"status": "success", "time": ping_time, "error": None}
                else:
                    return {"status": "success", "time": None, "error": None}
            else:
                return {"status": "failed", "time": None, "error": "Ping failed"}

        except Exception as e:
            return {"status": "error", "time": None, "error": str(e)}
    
    def check_tunnel(self, tunnel):
        """Check single tunnel with rate limiting and history logging"""
        tunnel_name = tunnel['name']

        # Check rate limiting untuk responsible monitoring
        if self.is_rate_limited(tunnel['host'], tunnel['port']):
            return {
                'name': tunnel['name'],
                'host': tunnel['host'],
                'port': tunnel['port'],
                'location': tunnel.get('location', ''),
                'description': tunnel.get('description', ''),
                'tcp': {'status': 'rate_limited', 'time': None, 'error': 'Rate limited'},
                'ping': {'status': 'rate_limited', 'time': None, 'error': 'Rate limited'},
                'overall': False,
                'timestamp': datetime.now().isoformat()
            }

        tcp_result = self.quick_tcp_check(tunnel['host'], tunnel['port'])
        ping_result = self.quick_ping(tunnel['host'])

        current_status = tcp_result['status'] == 'online'
        previous_status = self.previous_status.get(tunnel_name, None)

        # Log status ke database
        self.history_db.log_tunnel_status(
            tunnel_name=tunnel_name,
            host=tunnel['host'],
            port=tunnel['port'],
            status='online' if current_status else 'offline',
            response_time=tcp_result.get('time'),
            error_message=tcp_result.get('error') if not current_status else None
        )

        # Detect status changes untuk downtime tracking
        if previous_status is not None:
            if previous_status and not current_status:
                # Tunnel went down
                self.history_db.start_downtime_event(
                    tunnel_name=tunnel_name,
                    host=tunnel['host'],
                    port=tunnel['port'],
                    error_message=tcp_result.get('error')
                )
                logger.warning(f"🔴 TUNNEL DOWN: {tunnel_name} ({tunnel['host']}:{tunnel['port']})")

            elif not previous_status and current_status:
                # Tunnel came back up
                duration = self.history_db.end_downtime_event(tunnel_name)
                if duration:
                    logger.info(f"🟢 TUNNEL RECOVERED: {tunnel_name} - Downtime: {self.format_duration(duration)}")

        # Update previous status
        self.previous_status[tunnel_name] = current_status

        return {
            'name': tunnel['name'],
            'host': tunnel['host'],
            'port': tunnel['port'],
            'location': tunnel.get('location', ''),
            'description': tunnel.get('description', ''),
            'tcp': tcp_result,
            'ping': ping_result,
            'overall': current_status,
            'timestamp': datetime.now().isoformat()
        }

    def format_duration(self, seconds):
        """Format duration in human readable format"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}m {secs}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    def check_all_tunnels(self):
        """Check semua tunnel"""
        results = {}
        
        for tunnel in self.tunnels:
            try:
                result = self.check_tunnel(tunnel)
                results[tunnel['name']] = result
                logger.info(f"Checked {tunnel['name']}: {result['overall']}")
            except Exception as e:
                logger.error(f"Error checking {tunnel['name']}: {e}")
                results[tunnel['name']] = {
                    'name': tunnel['name'],
                    'host': tunnel['host'],
                    'port': tunnel['port'],
                    'location': tunnel.get('location', ''),
                    'description': tunnel.get('description', ''),
                    'tcp': {'status': 'error', 'time': None, 'error': str(e)},
                    'ping': {'status': 'error', 'time': None, 'error': str(e)},
                    'overall': False,
                    'timestamp': datetime.now().isoformat()
                }
        
        return results

# Initialize monitor
monitor = TunnelMonitor()

def background_monitoring():
    """Background monitoring thread with adaptive interval"""
    global tunnel_status, last_update

    while True:
        try:
            logger.info("Starting background check...")
            start_time = time.time()
            results = monitor.check_all_tunnels()

            with status_lock:
                tunnel_status = results
                last_update = datetime.now()

            check_duration = time.time() - start_time
            logger.info(f"Background check completed in {check_duration:.2f}s. {len(results)} tunnels checked.")

            # Adaptive interval based on performance and tunnel status
            base_interval = monitor.settings.get('monitor_interval', 10)

            # Check if any tunnel is down (faster monitoring when issues detected)
            down_tunnels = [name for name, result in results.items() if not result['overall']]

            if down_tunnels:
                # Faster monitoring when tunnels are down
                interval = max(base_interval // 2, 5)  # Minimum 5 seconds
                logger.info(f"Tunnels down detected: {down_tunnels}. Using fast interval: {interval}s")
            else:
                # Normal interval when all tunnels are up
                interval = base_interval

            # Adjust interval if check took too long
            if check_duration > interval * 0.8:
                interval = max(interval + 5, check_duration + 2)
                logger.warning(f"Check duration high ({check_duration:.2f}s), adjusting interval to {interval}s")

            time.sleep(interval)

        except Exception as e:
            logger.error(f"Error in background monitoring: {e}")
            time.sleep(15)  # Shorter retry interval for fast mode

# Routes
@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """API endpoint untuk status tunnel"""
    with status_lock:
        data = {
            'tunnels': tunnel_status,
            'last_update': last_update.isoformat() if last_update else None,
            'total_tunnels': len(tunnel_status),
            'online_tunnels': sum(1 for t in tunnel_status.values() if t['overall']),
            'settings': monitor.settings
        }
    
    return jsonify(data)

@app.route('/api/tunnel/<tunnel_name>')
def api_tunnel_detail(tunnel_name):
    """API endpoint untuk detail tunnel tertentu"""
    with status_lock:
        if tunnel_name in tunnel_status:
            return jsonify(tunnel_status[tunnel_name])
        else:
            return jsonify({'error': 'Tunnel not found'}), 404

@app.route('/api/refresh')
def api_refresh():
    """API endpoint untuk refresh manual"""
    try:
        results = monitor.check_all_tunnels()
        
        with status_lock:
            tunnel_status.update(results)
            last_update = datetime.now()
        
        return jsonify({'success': True, 'message': 'Refresh completed'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint untuk Railway"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'tunnels_configured': len(monitor.tunnels)
    })

@app.route('/api/history/<tunnel_name>')
def api_tunnel_history(tunnel_name):
    """API endpoint untuk history tunnel tertentu"""
    try:
        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 100, type=int)

        with monitor.history_db.get_db_connection() as conn:
            history = conn.execute('''
                SELECT status, response_time, error_message, timestamp
                FROM tunnel_status_history
                WHERE tunnel_name = ?
                AND timestamp >= datetime('now', '-{} hours')
                ORDER BY timestamp DESC
                LIMIT ?
            '''.format(hours), (tunnel_name, limit)).fetchall()

            return jsonify({
                'tunnel_name': tunnel_name,
                'history': [dict(row) for row in history],
                'total_records': len(history)
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/downtime/<tunnel_name>')
def api_tunnel_downtime(tunnel_name):
    """API endpoint untuk downtime events tunnel tertentu"""
    try:
        days = request.args.get('days', 7, type=int)

        with monitor.history_db.get_db_connection() as conn:
            downtime_events = conn.execute('''
                SELECT down_start, down_end, duration_seconds, is_resolved, error_message
                FROM downtime_events
                WHERE tunnel_name = ?
                AND down_start >= datetime('now', '-{} days')
                ORDER BY down_start DESC
            '''.format(days), (tunnel_name,)).fetchall()

            # Calculate statistics
            total_downtime = sum(row['duration_seconds'] or 0 for row in downtime_events)
            total_events = len(downtime_events)
            unresolved_events = sum(1 for row in downtime_events if not row['is_resolved'])

            return jsonify({
                'tunnel_name': tunnel_name,
                'downtime_events': [dict(row) for row in downtime_events],
                'statistics': {
                    'total_events': total_events,
                    'total_downtime_seconds': total_downtime,
                    'total_downtime_formatted': monitor.format_duration(total_downtime),
                    'unresolved_events': unresolved_events,
                    'average_downtime_seconds': total_downtime // total_events if total_events > 0 else 0
                }
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/downtime/all')
def api_all_downtime():
    """API endpoint untuk semua downtime events"""
    try:
        days = request.args.get('days', 7, type=int)

        with monitor.history_db.get_db_connection() as conn:
            downtime_events = conn.execute('''
                SELECT tunnel_name, down_start, down_end, duration_seconds, is_resolved, error_message
                FROM downtime_events
                WHERE down_start >= datetime('now', '-{} days')
                ORDER BY down_start DESC
            '''.format(days)).fetchall()

            # Group by tunnel
            tunnels_downtime = {}
            for row in downtime_events:
                tunnel = row['tunnel_name']
                if tunnel not in tunnels_downtime:
                    tunnels_downtime[tunnel] = {
                        'events': [],
                        'total_downtime': 0,
                        'total_events': 0
                    }

                tunnels_downtime[tunnel]['events'].append(dict(row))
                tunnels_downtime[tunnel]['total_downtime'] += row['duration_seconds'] or 0
                tunnels_downtime[tunnel]['total_events'] += 1

            return jsonify({
                'tunnels_downtime': tunnels_downtime,
                'summary': {
                    'total_tunnels_affected': len(tunnels_downtime),
                    'total_events': len(downtime_events),
                    'period_days': days
                }
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics')
def api_statistics():
    """API endpoint untuk statistik keseluruhan"""
    try:
        days = request.args.get('days', 7, type=int)

        with monitor.history_db.get_db_connection() as conn:
            # Uptime statistics
            uptime_stats = conn.execute('''
                SELECT
                    tunnel_name,
                    COUNT(*) as total_checks,
                    SUM(CASE WHEN status = 'online' THEN 1 ELSE 0 END) as online_checks,
                    AVG(CASE WHEN status = 'online' THEN response_time ELSE NULL END) as avg_response_time
                FROM tunnel_status_history
                WHERE timestamp >= datetime('now', '-{} days')
                GROUP BY tunnel_name
            '''.format(days)).fetchall()

            # Recent downtime
            recent_downtime = conn.execute('''
                SELECT tunnel_name, COUNT(*) as downtime_events, SUM(duration_seconds) as total_downtime
                FROM downtime_events
                WHERE down_start >= datetime('now', '-{} days')
                GROUP BY tunnel_name
            '''.format(days)).fetchall()

            # Combine statistics
            stats = {}
            for row in uptime_stats:
                tunnel = row['tunnel_name']
                uptime_percentage = (row['online_checks'] / row['total_checks'] * 100) if row['total_checks'] > 0 else 0

                stats[tunnel] = {
                    'uptime_percentage': round(uptime_percentage, 2),
                    'total_checks': row['total_checks'],
                    'online_checks': row['online_checks'],
                    'avg_response_time': round(row['avg_response_time'] or 0, 2),
                    'downtime_events': 0,
                    'total_downtime_seconds': 0
                }

            # Add downtime data
            for row in recent_downtime:
                tunnel = row['tunnel_name']
                if tunnel in stats:
                    stats[tunnel]['downtime_events'] = row['downtime_events']
                    stats[tunnel]['total_downtime_seconds'] = row['total_downtime'] or 0
                    stats[tunnel]['total_downtime_formatted'] = monitor.format_duration(row['total_downtime'] or 0)

            return jsonify({
                'period_days': days,
                'tunnel_statistics': stats,
                'generated_at': datetime.now().isoformat()
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Start background monitoring thread
    monitor_thread = Thread(target=background_monitoring, daemon=True)
    monitor_thread.start()
    
    # Get port from environment (Railway sets this)
    port = int(os.environ.get('PORT', 5000))
    
    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=False)
