# src/memory_system.py
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List
import hashlib

class EnhancedMemorySystem:
    def __init__(self, db_path: str = "agent_memory.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for persistent memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Query history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_hash TEXT UNIQUE,
                query_text TEXT,
                timestamp TEXT,
                success_rate REAL DEFAULT 0,
                execution_count INTEGER DEFAULT 1,
                avg_processing_time REAL DEFAULT 0
            )
        ''')
        
        # Compliance violations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compliance_violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                violation_type TEXT,
                description TEXT,
                timestamp TEXT,
                resolved BOOLEAN DEFAULT FALSE,
                severity TEXT DEFAULT 'medium'
            )
        ''')
        
        # Agent performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT,
                task_type TEXT,
                success_count INTEGER DEFAULT 0,
                total_count INTEGER DEFAULT 0,
                avg_response_time REAL,
                last_updated TEXT
            )
        ''')
        
        # System insights table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insight_type TEXT,
                insight_data TEXT,
                confidence REAL,
                timestamp TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_query(self, query: str, success: bool = True, processing_time: float = 0):
        """Log query with learning capabilities"""
        query_hash = self._hash_query(query)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if query exists
        cursor.execute(
            'SELECT execution_count, success_rate, avg_processing_time FROM query_history WHERE query_hash = ?',
            (query_hash,)
        )
        result = cursor.fetchone()
        
        current_time = datetime.now().isoformat()
        
        if result:
            # Update existing query
            execution_count, old_success_rate, old_avg_time = result
            new_count = execution_count + 1
            new_success_rate = ((old_success_rate * execution_count) + int(success)) / new_count
            
            # Update average processing time
            if old_avg_time:
                new_avg_time = ((old_avg_time * execution_count) + processing_time) / new_count
            else:
                new_avg_time = processing_time
            
            cursor.execute('''
                UPDATE query_history 
                SET execution_count = ?, success_rate = ?, avg_processing_time = ?, timestamp = ?
                WHERE query_hash = ?
            ''', (new_count, new_success_rate, new_avg_time, current_time, query_hash))
        else:
            # Insert new query
            cursor.execute('''
                INSERT INTO query_history (query_hash, query_text, timestamp, success_rate, avg_processing_time)
                VALUES (?, ?, ?, ?, ?)
            ''', (query_hash, query, current_time, float(success), processing_time))
        
        conn.commit()
        conn.close()
    
    def log_compliance_violation(self, violation_type: str, description: str, severity: str = "medium"):
        """Log compliance violations for learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO compliance_violations (violation_type, description, timestamp, severity)
            VALUES (?, ?, ?, ?)
        ''', (violation_type, description, datetime.now().isoformat(), severity))
        
        conn.commit()
        conn.close()
    
    def get_query_success_rate(self, query: str) -> float:
        """Get historical success rate for similar queries"""
        query_hash = self._hash_query(query)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT success_rate FROM query_history WHERE query_hash = ?',
            (query_hash,)
        )
        result = cursor.fetchone()
        
        conn.close()
        
        return result[0] if result else 0.5  # Default confidence
    
    def get_common_violations(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get frequently occurring compliance violations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT violation_type, COUNT(*) as count, severity
            FROM compliance_violations 
            WHERE timestamp > ? AND resolved = FALSE
            GROUP BY violation_type, severity
            ORDER BY count DESC
            LIMIT 10
        ''', (cutoff_date,))
        
        violations = [
            {'type': row[0], 'count': row[1], 'severity': row[2]}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return violations
    
    def update_agent_performance(self, agent_name: str, task_type: str, 
                               success: bool, response_time: float):
        """Update agent performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if record exists
        cursor.execute('''
            SELECT success_count, total_count, avg_response_time FROM agent_performance 
            WHERE agent_name = ? AND task_type = ?
        ''', (agent_name, task_type))
        
        result = cursor.fetchone()
        current_time = datetime.now().isoformat()
        
        if result:
            success_count, total_count, old_avg_time = result
            new_success_count = success_count + int(success)
            new_total_count = total_count + 1
            
            # Calculate new average time
            if old_avg_time:
                new_avg_time = ((old_avg_time * total_count) + response_time) / new_total_count
            else:
                new_avg_time = response_time
            
            cursor.execute('''
                UPDATE agent_performance 
                SET success_count = ?, total_count = ?, avg_response_time = ?, last_updated = ?
                WHERE agent_name = ? AND task_type = ?
            ''', (new_success_count, new_total_count, new_avg_time, current_time, agent_name, task_type))
        else:
            cursor.execute('''
                INSERT INTO agent_performance 
                (agent_name, task_type, success_count, total_count, avg_response_time, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (agent_name, task_type, int(success), 1, response_time, current_time))
        
        conn.commit()
        conn.close()
    
    def store_system_insight(self, insight_type: str, insight_data: Dict[str, Any], confidence: float = 0.8):
        """Store system-generated insights"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO system_insights (insight_type, insight_data, confidence, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (insight_type, json.dumps(insight_data), confidence, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_recent_insights(self, insight_type: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent system insights"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if insight_type:
            cursor.execute('''
                SELECT insight_type, insight_data, confidence, timestamp
                FROM system_insights 
                WHERE insight_type = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (insight_type, limit))
        else:
            cursor.execute('''
                SELECT insight_type, insight_data, confidence, timestamp
                FROM system_insights 
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
        
        insights = []
        for row in cursor.fetchall():
            insights.append({
                'type': row[0],
                'data': json.loads(row[1]),
                'confidence': row[2],
                'timestamp': row[3]
            })
        
        conn.close()
        return insights
    
    def _hash_query(self, query: str) -> str:
        """Create hash of query for deduplication"""
        return hashlib.md5(query.encode()).hexdigest()
    
    def get_system_insights(self) -> Dict[str, Any]:
        """Get overall system insights from memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total queries
        cursor.execute('SELECT COUNT(*) FROM query_history')
        total_queries = cursor.fetchone()[0] or 0
        
        # Average success rate
        cursor.execute('SELECT AVG(success_rate) FROM query_history')
        avg_success_result = cursor.fetchone()
        avg_success = avg_success_result[0] if avg_success_result[0] is not None else 0
        
        # Recent violations
        common_violations = self.get_common_violations(days=7)
        
        # Agent performance
        cursor.execute('''
            SELECT agent_name, 
                   AVG(success_count * 1.0 / total_count) as success_rate,
                   AVG(avg_response_time) as avg_time
            FROM agent_performance 
            GROUP BY agent_name
        ''')
        agent_performance = {}
        for row in cursor.fetchall():
            agent_performance[row[0]] = {
                'success_rate': row[1] or 0,
                'avg_response_time': row[2] or 0
            }
        
        # System health calculation
        if avg_success > 0.8:
            system_health = 'excellent'
        elif avg_success > 0.6:
            system_health = 'good'
        elif avg_success > 0.4:
            system_health = 'fair'
        else:
            system_health = 'poor'
        
        conn.close()
        
        return {
            'total_queries_processed': total_queries,
            'average_success_rate': round(avg_success, 3),
            'common_compliance_issues': common_violations,
            'agent_performance': agent_performance,
            'system_health': system_health,
            'performance_trend': self._calculate_performance_trend()
        }
    
    def _calculate_performance_trend(self) -> str:
        """Calculate performance trend over time"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get success rates for last 7 days and previous 7 days
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        two_weeks_ago = (datetime.now() - timedelta(days=14)).isoformat()
        
        # Recent week
        cursor.execute('''
            SELECT AVG(success_rate) FROM query_history 
            WHERE timestamp > ?
        ''', (week_ago,))
        recent_success = cursor.fetchone()[0] or 0
        
        # Previous week
        cursor.execute('''
            SELECT AVG(success_rate) FROM query_history 
            WHERE timestamp > ? AND timestamp <= ?
        ''', (two_weeks_ago, week_ago))
        previous_success = cursor.fetchone()[0] or 0
        
        conn.close()
        
        if recent_success > previous_success + 0.05:
            return 'improving'
        elif recent_success < previous_success - 0.05:
            return 'declining'
        else:
            return 'stable'
    
    def get_agent_recommendations(self) -> List[str]:
        """Generate recommendations based on system performance"""
        recommendations = []
        insights = self.get_system_insights()
        
        # Check agent performance
        for agent, performance in insights['agent_performance'].items():
            if performance['success_rate'] < 0.6:
                recommendations.append(f"Review {agent} performance - low success rate detected")
            if performance['avg_response_time'] > 5.0:  # seconds
                recommendations.append(f"Optimize {agent} - high response time detected")
        
        # Check compliance issues
        if insights['common_compliance_issues']:
            top_issue = insights['common_compliance_issues'][0]
            recommendations.append(f"Address frequent {top_issue['type']} compliance violations")
        
        # System health recommendations
        if insights['system_health'] in ['fair', 'poor']:
            recommendations.append("System performance needs attention - review logs and metrics")
        
        return recommendations[:5]  # Return top 5 recommendations