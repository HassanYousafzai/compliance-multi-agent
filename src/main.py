# src/main.py
import json
from datetime import datetime
from typing import Dict, Any, List
import traceback

from retrieval_agent import RetrievalAgent
from enhanced_reasoning_agent import EnhancedReasoningAgent
from enhanced_compliance_agent import EnhancedComplianceAgent
from memory_system import EnhancedMemorySystem

class EnhancedComplianceAwareAgentSystem:
    def __init__(self, db_path: str = "agent_memory.db"):
        self.retrieval_agent = RetrievalAgent()
        self.reasoning_agent = EnhancedReasoningAgent()
        self.compliance_agent = EnhancedComplianceAgent()
        self.memory_system = EnhancedMemorySystem(db_path)
        
        # System configuration
        self.config = {
            'default_regulations': ['hipaa', 'gdpr'],
            'enable_learning': True,
            'log_level': 'INFO'
        }
        
        print("🚀 Enhanced Compliance-Aware Multi-Agent System Initialized")
    
    def process_query(self, query: str, regulations: List[str] = None) -> Dict[str, Any]:
        """
        Process a query through the complete multi-agent pipeline
        
        Args:
            query: User query string
            regulations: List of compliance regulations to check
            
        Returns:
            Dictionary containing complete processing results
        """
        start_time = datetime.now()
        
        if regulations is None:
            regulations = self.config['default_regulations']
        
        try:
            # Check historical performance for this type of query
            historical_success = self.memory_system.get_query_success_rate(query)
            
            # Step 1: Retrieve data
            retrieval_start = datetime.now()
            data = self.retrieval_agent.fetch_data(query)
            retrieval_time = (datetime.now() - retrieval_start).total_seconds()
            
            self.memory_system.update_agent_performance(
                "retrieval_agent", "data_fetch", bool(data), retrieval_time
            )
            
            if not data:
                return self._create_error_response("No data retrieved from source", start_time)
            
            # Step 2: Reasoning with chain-of-thought
            reasoning_start = datetime.now()
            insights = self.reasoning_agent.analyze_with_chain_of_thought(data, query)
            reasoning_time = (datetime.now() - reasoning_start).total_seconds()
            
            self.memory_system.update_agent_performance(
                "reasoning_agent", "data_analysis", True, reasoning_time
            )
            
            # Step 3: Compliance check
            compliance_start = datetime.now()
            compliance_result = self.compliance_agent.validate_compliance(data, regulations)
            compliance_time = (datetime.now() - compliance_start).total_seconds()
            
            self.memory_system.update_agent_performance(
                "compliance_agent", "compliance_check", 
                compliance_result['overall_compliant'], compliance_time
            )
            
            # Log compliance violations if any
            for regulation, result in compliance_result['regulation_results'].items():
                for violation in result.get('violations', []):
                    # Determine severity based on violation type
                    severity = "high" if "SSN" in violation or "email" in violation.lower() else "medium"
                    self.memory_system.log_compliance_violation(regulation, violation, severity)
            
            # Step 4: Generate system insights for learning
            if self.config['enable_learning']:
                self._generate_learning_insights(data, insights, compliance_result, query)
            
            # Step 5: Log successful query
            total_time = (datetime.now() - start_time).total_seconds()
            self.memory_system.log_query(query, success=True, processing_time=total_time)
            
            return {
                'success': True,
                'query': query,
                'retrieved_data': data,
                'insights': insights,
                'compliance_check': compliance_result,
                'performance_metrics': {
                    'total_processing_time': total_time,
                    'historical_success_rate': historical_success,
                    'component_times': {
                        'retrieval': retrieval_time,
                        'reasoning': reasoning_time,
                        'compliance': compliance_time
                    },
                    'efficiency_score': self._calculate_efficiency_score(total_time, len(str(data)))
                },
                'system_recommendations': self._generate_system_recommendations(insights, compliance_result),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            # Log failed query
            total_time = (datetime.now() - start_time).total_seconds()
            self.memory_system.log_query(query, success=False, processing_time=total_time)
            
            error_details = {
                'error': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat()
            }
            
            return self._create_error_response(f"Processing failed: {str(e)}", start_time, error_details)
    
    def _generate_learning_insights(self, data: Dict[str, Any], insights: Dict[str, Any], 
                                  compliance_result: Dict[str, Any], query: str):
        """Generate and store learning insights from the processing"""
        
        # Insight 1: Query type patterns
        query_insight = {
            'query_length': len(query),
            'data_fields_retrieved': len(data),
            'compliance_status': compliance_result['overall_compliant'],
            'reasoning_confidence': insights['structured_insights']['confidence_score']
        }
        self.memory_system.store_system_insight('query_pattern', query_insight, 0.7)
        
        # Insight 2: Compliance patterns
        if not compliance_result['overall_compliant']:
            compliance_insight = {
                'violation_count': compliance_result['summary']['total_violations'],
                'regulation_violations': list(compliance_result['regulation_results'].keys()),
                'data_type': type(data).__name__
            }
            self.memory_system.store_system_insight('compliance_pattern', compliance_insight, 0.8)
        
        # Insight 3: Performance patterns
        performance_insight = {
            'data_complexity': len(str(data)),
            'hypotheses_generated': len(insights['generated_hypotheses']),
            'reasoning_steps': len(insights['reasoning_chain'])
        }
        self.memory_system.store_system_insight('performance_pattern', performance_insight, 0.6)
    
    def _generate_system_recommendations(self, insights: Dict[str, Any], 
                                       compliance_result: Dict[str, Any]) -> List[str]:
        """Generate system-level recommendations"""
        recommendations = []
        
        # Data quality recommendations
        data_quality = insights['structured_insights']['data_quality_assessment']
        if data_quality['completeness'] in ['fair', 'poor']:
            recommendations.append("Consider improving data quality for more accurate insights")
        
        # Compliance recommendations
        if not compliance_result['overall_compliant']:
            recommendations.append("Address compliance violations before production deployment")
        
        # Reasoning recommendations
        confidence = insights['structured_insights']['confidence_score']
        if confidence < 0.6:
            recommendations.append("Low confidence in analysis - consider additional data sources")
        
        # Add memory system recommendations
        memory_recommendations = self.memory_system.get_agent_recommendations()
        recommendations.extend(memory_recommendations)
        
        return list(set(recommendations))[:5]  # Remove duplicates and limit
    
    def _calculate_efficiency_score(self, processing_time: float, data_size: int) -> float:
        """Calculate processing efficiency score"""
        # Normalize based on data size and time
        base_efficiency = 1.0 / (processing_time + 1)  # Avoid division by zero
        size_factor = 1.0 / (data_size / 1000 + 1)  # Normalize data size
        
        efficiency = (base_efficiency + size_factor) / 2
        return min(efficiency, 1.0)
    
    def _create_error_response(self, error_message: str, start_time: datetime, 
                             error_details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create standardized error response"""
        total_time = (datetime.now() - start_time).total_seconds()
        
        response = {
            'success': False,
            'error': error_message,
            'performance_metrics': {
                'total_processing_time': total_time,
                'error_occurred': True
            },
            'timestamp': datetime.now().isoformat()
        }
        
        if error_details:
            response['error_details'] = error_details
        
        return response
    
    def get_system_analytics(self) -> Dict[str, Any]:
        """Get comprehensive system analytics"""
        memory_insights = self.memory_system.get_system_insights()
        compliance_stats = self.compliance_agent.get_compliance_stats()
        retrieval_stats = self.retrieval_agent.get_request_stats()
        
        return {
            'memory_system': memory_insights,
            'compliance_agent': compliance_stats,
            'retrieval_agent': retrieval_stats,
            'system_health': self._calculate_system_health(memory_insights, compliance_stats),
            'recommendations': self.memory_system.get_agent_recommendations()
        }
    
    def _calculate_system_health(self, memory_insights: Dict[str, Any], 
                               compliance_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall system health"""
        success_rate = memory_insights.get('average_success_rate', 0)
        compliance_rate = compliance_stats.get('compliance_rate', 1.0)
        
        # Calculate health score (0-100)
        health_score = (success_rate * 0.6 + compliance_rate * 0.4) * 100
        
        if health_score >= 80:
            status = "healthy"
        elif health_score >= 60:
            status = "degraded"
        else:
            status = "unhealthy"
        
        return {
            'score': round(health_score, 1),
            'status': status,
            'success_rate': round(success_rate * 100, 1),
            'compliance_rate': round(compliance_rate * 100, 1)
        }
    
    def batch_process_queries(self, queries: List[str]) -> Dict[str, Any]:
        """Process multiple queries in batch"""
        results = []
        successful = 0
        total_time = 0
        
        for query in queries:
            result = self.process_query(query)
            results.append(result)
            
            if result['success']:
                successful += 1
                total_time += result['performance_metrics']['total_processing_time']
        
        success_rate = successful / len(queries) if queries else 0
        avg_time = total_time / successful if successful else 0
        
        return {
            'total_queries': len(queries),
            'successful_queries': successful,
            'success_rate': success_rate,
            'average_processing_time': avg_time,
            'results': results
        }
    
    def reset_system(self):
        """Reset system state (for testing)"""
        # Note: This would typically require database reset in production
        print("System reset requested - memory remains persisted")
    
    def __del__(self):
        """Cleanup when system is destroyed"""
        print("Multi-Agent System shutdown complete")