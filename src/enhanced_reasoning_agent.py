# src/enhanced_reasoning_agent.py
import json
from datetime import datetime
from typing import Dict, Any, List

class EnhancedReasoningAgent:
    def __init__(self):
        self.reasoning_steps = []
        self.hypotheses = []
    
    def analyze_with_chain_of_thought(self, data: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Perform multi-step reasoning with chain-of-thought"""
        self.reasoning_steps = []
        self.hypotheses = []
        
        # Step 1: Data Understanding
        self._add_reasoning_step("DATA_UNDERSTANDING", "Analyzing data structure and content")
        data_insights = self._understand_data_structure(data)
        
        # Step 2: Hypothesis Generation
        self._add_reasoning_step("HYPOTHESIS_GENERATION", "Generating potential insights based on data patterns")
        hypotheses = self._generate_hypotheses(data, query)
        
        # Step 3: Pattern Recognition
        self._add_reasoning_step("PATTERN_RECOGNITION", "Identifying patterns and correlations in the data")
        patterns = self._identify_patterns(data)
        
        # Step 4: Context Analysis
        self._add_reasoning_step("CONTEXT_ANALYSIS", "Analyzing data in the context of the query")
        context_analysis = self._analyze_context(data, query)
        
        # Step 5: Insight Synthesis
        self._add_reasoning_step("INSIGHT_SYNTHESIS", "Synthesizing final insights from all analysis steps")
        final_insights = self._synthesize_insights(data_insights, hypotheses, patterns, context_analysis, query)
        
        return {
            'structured_insights': final_insights,
            'reasoning_chain': self.reasoning_steps,
            'generated_hypotheses': hypotheses,
            'identified_patterns': patterns,
            'context_analysis': context_analysis,
            'timestamp': datetime.now().isoformat()
        }
    
    def _add_reasoning_step(self, step_type: str, description: str):
        """Add a step to the reasoning chain"""
        step = {
            'step': len(self.reasoning_steps) + 1,
            'type': step_type,
            'description': description,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        self.reasoning_steps.append(step)
    
    def _understand_data_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data structure and content"""
        insights = {
            'data_type': type(data).__name__,
            'field_count': len(data),
            'fields': list(data.keys()),
            'field_types': {},
            'data_quality': {}
        }
        
        numeric_count = 0
        string_count = 0
        null_count = 0
        
        for key, value in data.items():
            field_type = type(value).__name__
            insights['field_types'][key] = field_type
            
            # Count types for quality assessment
            if isinstance(value, (int, float)):
                numeric_count += 1
            elif isinstance(value, str):
                string_count += 1
            elif value is None:
                null_count += 1
        
        # Data quality assessment
        insights['data_quality'] = {
            'numeric_fields': numeric_count,
            'text_fields': string_count,
            'null_fields': null_count,
            'completeness_score': 1 - (null_count / len(data)) if data else 1.0
        }
        
        return insights
    
    def _generate_hypotheses(self, data: Dict[str, Any], query: str) -> List[str]:
        """Generate potential hypotheses based on data and query"""
        hypotheses = []
        query_lower = query.lower()
        data_str = str(data).lower()
        
        # Weather-specific hypotheses
        if any(term in query_lower for term in ['weather', 'temperature', 'forecast']):
            temp = data.get('temperature')
            if isinstance(temp, (int, float)):
                if temp > 30:
                    hypotheses.append("High temperature conditions detected - potential heat wave impact")
                elif temp < 0:
                    hypotheses.append("Freezing temperatures - risk of ice and winter conditions")
                elif 20 <= temp <= 26:
                    hypotheses.append("Comfortable temperature range - ideal for outdoor activities")
            
            humidity = data.get('humidity')
            if isinstance(humidity, (int, float)):
                if humidity > 80:
                    hypotheses.append("High humidity may affect comfort and equipment")
                elif humidity < 30:
                    hypotheses.append("Low humidity conditions - potential dehydration risk")
            
            # Weather condition hypotheses
            condition = data.get('weather_condition')
            if condition:
                if 'rain' in condition.lower():
                    hypotheses.append("Precipitation expected - consider indoor alternatives")
                elif 'snow' in condition.lower():
                    hypotheses.append("Snow conditions - transportation and safety considerations")
        
        # Medical/health hypotheses
        if any(term in query_lower for term in ['patient', 'medical', 'health']):
            if 'blood_pressure' in data:
                hypotheses.append("Blood pressure data available for health monitoring")
            if 'heart_rate' in data:
                hypotheses.append("Heart rate monitoring provides vital health insights")
        
        # Business/data analysis hypotheses
        if any(term in query_lower for term in ['sales', 'business', 'customer']):
            if 'sales_volume' in data:
                hypotheses.append("Sales volume trends can inform business strategy")
            if 'customer_count' in data:
                hypotheses.append("Customer behavior patterns may reveal opportunities")
        
        # General data quality hypotheses
        if any(value is None for value in data.values()):
            hypotheses.append("Data completeness issues detected - may affect analysis accuracy")
        
        if len(data) < 3:
            hypotheses.append("Limited data fields available - consider additional data sources")
        
        return hypotheses
    
    def _identify_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify patterns in the data"""
        patterns = {
            'numeric_ranges': {},
            'categorical_values': {},
            'correlations': [],
            'anomalies': [],
            'trends': []
        }
        
        numeric_fields = {}
        
        # Analyze numeric fields
        for key, value in data.items():
            if isinstance(value, (int, float)):
                numeric_fields[key] = value
                patterns['numeric_ranges'][key] = {
                    'value': value,
                    'type': 'numeric'
                }
            
            elif isinstance(value, str):
                if key not in patterns['categorical_values']:
                    patterns['categorical_values'][key] = []
                if value not in patterns['categorical_values'][key]:
                    patterns['categorical_values'][key].append(value)
        
        # Simple correlation detection between numeric fields
        if len(numeric_fields) >= 2:
            field_names = list(numeric_fields.keys())[:3]  # Limit to first 3 for simplicity
            if len(field_names) >= 2:
                patterns['correlations'].append(
                    f"Potential relationship between {field_names[0]} and {field_names[1]}"
                )
        
        # Anomaly detection (simplified)
        for field, value in numeric_fields.items():
            if field == 'temperature' and isinstance(value, (int, float)):
                if value > 50 or value < -50:  # Extreme temperatures
                    patterns['anomalies'].append(f"Extreme temperature value: {value}")
            
            elif field == 'humidity' and isinstance(value, (int, float)):
                if value > 100 or value < 0:  # Impossible humidity
                    patterns['anomalies'].append(f"Invalid humidity value: {value}")
        
        # Trend detection (simplified)
        if 'timestamp' in data:
            patterns['trends'].append("Temporal data available for trend analysis")
        
        return patterns
    
    def _analyze_context(self, data: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Analyze data in the context of the query"""
        context = {
            'query_intent': self._infer_query_intent(query),
            'data_relevance': self._assess_data_relevance(data, query),
            'actionable_insights': [],
            'limitations': []
        }
        
        # Determine actionable insights based on data and query
        if 'weather' in query.lower() and 'temperature' in data:
            temp = data['temperature']
            if isinstance(temp, (int, float)):
                if temp < 10:
                    context['actionable_insights'].append("Recommend warm clothing")
                elif temp > 25:
                    context['actionable_insights'].append("Recommend light clothing and hydration")
        
        # Identify limitations
        if len(data) < 5:
            context['limitations'].append("Limited data fields may restrict comprehensive analysis")
        
        if any(value is None for value in data.values()):
            context['limitations'].append("Missing values in dataset")
        
        return context
    
    def _infer_query_intent(self, query: str) -> str:
        """Infer the intent behind the query"""
        query_lower = query.lower()
        
        if any(term in query_lower for term in ['weather', 'temperature', 'forecast']):
            return "weather_inquiry"
        elif any(term in query_lower for term in ['patient', 'medical', 'health']):
            return "health_analysis"
        elif any(term in query_lower for term in ['sales', 'business', 'customer']):
            return "business_intelligence"
        elif any(term in query_lower for term in ['analyze', 'insight', 'pattern']):
            return "data_analysis"
        else:
            return "general_inquiry"
    
    def _assess_data_relevance(self, data: Dict[str, Any], query: str) -> float:
        """Assess how relevant the data is to the query"""
        relevance_score = 0.5  # Base score
        
        query_terms = query.lower().split()
        data_terms = ' '.join(str(data).lower().split())
        
        # Simple term matching for relevance
        matching_terms = sum(1 for term in query_terms if term in data_terms)
        relevance_score += min(matching_terms * 0.1, 0.3)  # Max 0.3 boost from term matching
        
        # Boost for specific domain matches
        if 'weather' in query.lower() and any(field in data for field in ['temperature', 'humidity']):
            relevance_score += 0.2
        
        return min(relevance_score, 1.0)
    
    def _synthesize_insights(self, data_insights: Dict, hypotheses: List[str], 
                           patterns: Dict, context: Dict, query: str) -> Dict[str, Any]:
        """Synthesize final insights from all reasoning steps"""
        insights = {
            'query_response': self._generate_query_response(data_insights, hypotheses, patterns, context, query),
            'data_quality_assessment': self._assess_data_quality(data_insights),
            'recommendations': self._generate_recommendations(hypotheses, patterns, context),
            'confidence_score': self._calculate_confidence(data_insights, hypotheses, context),
            'key_findings': self._extract_key_findings(hypotheses, patterns)
        }
        
        return insights
    
    def _generate_query_response(self, data_insights: Dict, hypotheses: List[str],
                              patterns: Dict, context: Dict, query: str) -> str:
        """Generate natural language response to the original query"""
        base_response = f"Based on analysis of {data_insights['field_count']} data fields, "
        
        if hypotheses:
            primary_insight = hypotheses[0]
            base_response += f"the primary insight is: {primary_insight}. "
        else:
            base_response += "the data appears consistent with expected patterns. "
        
        # Add context-specific information
        if context['actionable_insights']:
            base_response += f"Recommendation: {context['actionable_insights'][0]}. "
        
        # Add data quality note
        quality_score = data_insights['data_quality']['completeness_score']
        if quality_score < 0.8:
            base_response += "Note: Data quality considerations identified. "
        
        return base_response.strip()
    
    def _assess_data_quality(self, data_insights: Dict) -> Dict[str, Any]:
        """Assess the quality of the input data"""
        quality = data_insights['data_quality']
        completeness = quality['completeness_score']
        
        if completeness > 0.9:
            quality_level = "excellent"
        elif completeness > 0.7:
            quality_level = "good"
        elif completeness > 0.5:
            quality_level = "fair"
        else:
            quality_level = "poor"
        
        return {
            'completeness': quality_level,
            'field_variety': 'good' if data_insights['field_count'] > 3 else 'limited',
            'assessment': f"Data quality is {quality_level} with {completeness:.1%} completeness",
            'numeric_fields': quality['numeric_fields'],
            'text_fields': quality['text_fields']
        }
    
    def _generate_recommendations(self, hypotheses: List[str], patterns: Dict, context: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Add context recommendations
        recommendations.extend(context['actionable_insights'])
        
        # Add hypothesis-based recommendations
        if hypotheses:
            recommendations.append("Consider validating the generated hypotheses with additional data")
        
        # Add pattern-based recommendations
        if patterns.get('correlations'):
            recommendations.append("Further analysis recommended for identified correlations")
        
        if patterns.get('anomalies'):
            recommendations.append("Review data anomalies for potential data quality issues")
        
        # General recommendations
        recommendations.append("Regular data quality validation recommended")
        
        # Ensure we don't have too many recommendations
        return recommendations[:5]
    
    def _extract_key_findings(self, hypotheses: List[str], patterns: Dict) -> List[str]:
        """Extract the most important findings"""
        findings = []
        
        # Add top hypotheses as findings
        if hypotheses:
            findings.extend(hypotheses[:2])
        
        # Add significant patterns
        if patterns.get('anomalies'):
            findings.append("Data anomalies detected requiring review")
        
        if patterns.get('correlations'):
            findings.append("Potential correlations identified in the data")
        
        return findings[:3]  # Limit to top 3 findings
    
    def _calculate_confidence(self, data_insights: Dict, hypotheses: List[str], context: Dict) -> float:
        """Calculate confidence score for the analysis"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on data richness
        if data_insights['field_count'] > 3:
            confidence += 0.2
        
        # Increase confidence if hypotheses were generated
        if hypotheses:
            confidence += 0.2
        
        # Adjust based on data relevance
        confidence += (context['data_relevance'] - 0.5) * 0.3
        
        # Adjust based on data quality
        quality_score = data_insights['data_quality']['completeness_score']
        confidence += (quality_score - 0.5) * 0.3
        
        return min(max(confidence, 0.1), 1.0)  # Ensure between 0.1 and 1.0