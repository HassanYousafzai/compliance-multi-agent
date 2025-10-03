# src/enhanced_compliance_agent.py
import re
import json
from datetime import datetime
from typing import Dict, Any, List

class EnhancedComplianceAgent:
    def __init__(self):
        self.compliance_rules = {
            'hipaa': self._check_hipaa_compliance,
            'gdpr': self._check_gdpr_compliance,
            'data_retention': self._check_data_retention
        }
        self.compliance_log = []
        
    def _check_hipaa_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for HIPAA compliance violations"""
        violations = []
        warnings = []
        
        # PHI (Protected Health Information) patterns
        phi_patterns = {
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'medical_terms': r'\b(cancer|diabetes|HIV|AIDS|treatment|diagnosis|hypertension)\b',
            'healthcare_facilities': r'\b(hospital|clinic|medical center|physician|doctor)\b'
        }
        
        data_str = json.dumps(data).lower()
        
        for field_name, field_value in data.items():
            # Check for potential PHI in field values
            if isinstance(field_value, str):
                # SSN detection
                if re.search(phi_patterns['ssn'], field_value):
                    violations.append(f"Potential SSN found in {field_name}")
                
                # Medical terms detection
                if re.search(phi_patterns['medical_terms'], field_value.lower()):
                    warnings.append(f"Medical terminology found in {field_name}")
                
                # Healthcare facility detection
                if re.search(phi_patterns['healthcare_facilities'], field_value.lower()):
                    warnings.append(f"Healthcare facility mention in {field_name}")
            
            # Check for patient identifiers
            if any(id_term in field_name.lower() for id_term in ['patient', 'medical', 'health']):
                if field_value and field_name not in ['temperature', 'heart_rate']:  # Allow vital signs
                    warnings.append(f"Potential patient identifier in field: {field_name}")
        
        return {
            'is_compliant': len(violations) == 0,
            'violations': violations,
            'warnings': warnings,
            'rule_applied': 'HIPAA'
        }
    
    def _check_gdpr_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for GDPR compliance violations"""
        violations = []
        warnings = []
        
        # Personal data patterns
        personal_data_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(\+?(\d{1,3})?[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        }
        
        data_str = json.dumps(data)
        
        for data_type, pattern in personal_data_patterns.items():
            if re.search(pattern, data_str):
                violations.append(f"Potential {data_type.upper()} found in data")
        
        # Data minimization check
        data_size = len(data_str)
        if data_size > 2000:
            violations.append("Data size exceeds minimization principles")
        elif data_size > 1000:
            warnings.append("Large data payload - consider minimization")
        
        # Check for explicit consent fields
        if any('consent' in key.lower() for key in data.keys()):
            consent_fields = [key for key in data.keys() if 'consent' in key.lower()]
            for consent_field in consent_fields:
                if not data.get(consent_field):
                    violations.append(f"Missing consent in field: {consent_field}")
        
        return {
            'is_compliant': len(violations) == 0,
            'violations': violations,
            'warnings': warnings,
            'rule_applied': 'GDPR'
        }
    
    def _check_data_retention(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check data retention compliance"""
        violations = []
        warnings = []
        
        # Check if data contains timestamps older than retention period
        retention_period_days = 30  # Example: 30-day retention
        
        for key, value in data.items():
            if any(time_term in key.lower() for time_term in ['date', 'timestamp', 'time', 'created', 'last']):
                if isinstance(value, str):
                    try:
                        # Try to parse various date formats
                        date_str = value.replace('Z', '+00:00').split('.')[0]  # Handle milliseconds
                        data_date = datetime.fromisoformat(date_str)
                        days_diff = (datetime.now() - data_date).days
                        
                        if days_diff > retention_period_days:
                            violations.append(
                                f"Data in {key} exceeds retention period ({days_diff} days old)"
                            )
                        elif days_diff > retention_period_days * 0.7:  # Warning at 70% of retention
                            warnings.append(
                                f"Data in {key} approaching retention limit ({days_diff} days old)"
                            )
                    except (ValueError, TypeError):
                        # If date parsing fails, continue
                        continue
        
        return {
            'is_compliant': len(violations) == 0,
            'violations': violations,
            'warnings': warnings,
            'rule_applied': 'DATA_RETENTION'
        }
    
    def validate_compliance(self, data: Dict[str, Any], regulations: List[str] = None) -> Dict[str, Any]:
        """Enhanced compliance validation with multiple regulations"""
        if regulations is None:
            regulations = ['hipaa', 'gdpr']
        
        results = {}
        overall_compliant = True
        all_violations = []
        all_warnings = []
        
        for regulation in regulations:
            if regulation in self.compliance_rules:
                result = self.compliance_rules[regulation](data)
                results[regulation] = result
                
                if not result['is_compliant']:
                    overall_compliant = False
                
                all_violations.extend(result['violations'])
                all_warnings.extend(result['warnings'])
        
        # Log compliance check
        compliance_record = {
            'timestamp': datetime.now().isoformat(),
            'data_sample': {k: str(v)[:100] for k, v in list(data.items())[:3]},  # Sample for logging
            'results': results,
            'overall_compliant': overall_compliant,
            'total_violations': len(all_violations),
            'total_warnings': len(all_warnings)
        }
        self.compliance_log.append(compliance_record)
        
        return {
            'overall_compliant': overall_compliant,
            'regulation_results': results,
            'compliance_id': f"COMP_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'summary': {
                'total_violations': len(all_violations),
                'total_warnings': len(all_warnings),
                'violations': all_violations[:5],  # Limit for response
                'warnings': all_warnings[:5]
            }
        }
    
    def get_compliance_stats(self) -> Dict[str, Any]:
        """Get compliance checking statistics"""
        if not self.compliance_log:
            return {"total_checks": 0, "compliance_rate": 1.0}
        
        total_checks = len(self.compliance_log)
        compliant_checks = sum(1 for record in self.compliance_log if record['overall_compliant'])
        
        return {
            "total_checks": total_checks,
            "compliance_rate": compliant_checks / total_checks,
            "recent_checks": self.compliance_log[-5:],
            "most_common_violation": self._get_most_common_violation()
        }
    
    def _get_most_common_violation(self) -> str:
        """Get most common violation type"""
        if not self.compliance_log:
            return "none"
        
        violations = []
        for record in self.compliance_log:
            for regulation, result in record['results'].items():
                violations.extend(result['violations'])
        
        if not violations:
            return "none"
        
        # Count violation types
        violation_types = {}
        for violation in violations:
            v_type = violation.split(' ')[0]  # Simple type extraction
            violation_types[v_type] = violation_types.get(v_type, 0) + 1
        
        return max(violation_types.items(), key=lambda x: x[1])[0]