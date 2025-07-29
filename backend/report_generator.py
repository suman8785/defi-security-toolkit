import json
from datetime import datetime
from typing import Dict, List, Any
import markdown
from pathlib import Path

class ReportGenerator:
    def __init__(self):
        self.templates = {
            'executive_summary': self._executive_summary_template,
            'vulnerability_details': self._vulnerability_details_template,
            'code_analysis': self._code_analysis_template,
            'recommendations': self._recommendations_template,
            'risk_matrix': self._risk_matrix_template
        }

    
    def generate_report(
        self,
        analysis_results: Dict[str, Any],
        report_name: str,
        format_type: str,
        sections: List[str],
        severity_filter: List[str]
    ) -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        
        # Filter vulnerabilities by severity
        filtered_vulnerabilities = self._filter_vulnerabilities(analysis_results, severity_filter)
        
        # Generate report content
        if format_type == "Markdown":
            content = self._generate_markdown_report(
                filtered_vulnerabilities,
                sections,
                report_name
            )
            mime_type = "text/markdown"
        elif format_type == "JSON":
            content = json.dumps(
                self._generate_json_report(filtered_vulnerabilities, sections, report_name),
                indent=2
            )
            mime_type = "application/json"
        else:
            content = "Format not supported"
            mime_type = "text/plain"
        
        return {
            'content': content,
            'mime_type': mime_type,
            'filename': f"{report_name}.{format_type.lower()}"
        }
    
    def _filter_vulnerabilities(self, analysis_results: Dict, severity_filter: List[str]) -> List[Dict]:
        """Filter vulnerabilities by severity"""
        all_vulnerabilities = []
        
        # Extract from Slither results
        if 'slither' in analysis_results:
            slither_vulns = analysis_results['slither'].get('vulnerabilities', [])
            for vuln in slither_vulns:
                if vuln.get('severity', '').capitalize() in severity_filter:
                    vuln['source'] = 'Slither'
                    all_vulnerabilities.append(vuln)
        
        # Extract from Mythril results
        if 'mythril' in analysis_results:
            mythril_issues = analysis_results['mythril'].get('issues', [])
            for issue in mythril_issues:
                if issue.get('severity', '').capitalize() in severity_filter:
                    issue['source'] = 'Mythril'
                    all_vulnerabilities.append(issue)
        
        return all_vulnerabilities
    
    def _generate_markdown_report(self, vulnerabilities: List[Dict], sections: List[str], report_name: str) -> str:
        """Generate Markdown format report"""
        report_parts = []
        
        # Header
        report_parts.append(f"# Security Audit Report: {report_name}")
        report_parts.append(f"\n*Generated:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_parts.append("\n---\n")
        
        # Generate each section
        for section in sections:
            section_key = section.lower().replace(' ', '_')
            if section_key in self.templates:
                content = self.templates[section_key](vulnerabilities)
                report_parts.append(content)
                report_parts.append("\n---\n")
        
        return "\n".join(report_parts)
    
    def _generate_json_report(self, vulnerabilities: List[Dict], sections: List[str], report_name: str) -> Dict:
        """Generate JSON format report"""
        report = {
            'report_name': report_name,
            'generated': datetime.now().isoformat(),
            'sections': {}
        }
        
        for section in sections:
            section_key = section.lower().replace(' ', '_')
            if section_key == 'executive_summary':
                report['sections']['executive_summary'] = {
                    'total_issues': len(vulnerabilities),
                    'critical_high': sum(1 for v in vulnerabilities if v.get('severity', '').lower() in ['critical', 'high']),
                    'medium': sum(1 for v in vulnerabilities if v.get('severity', '').lower() == 'medium'),
                    'low': sum(1 for v in vulnerabilities if v.get('severity', '').lower() == 'low')
                }
            elif section_key == 'vulnerability_details':
                report['sections']['vulnerabilities'] = vulnerabilities
            elif section_key == 'recommendations':
                report['sections']['recommendations'] = self._get_recommendations_data(vulnerabilities)
        
        return report
    
    def _executive_summary_template(self, vulnerabilities: List[Dict]) -> str:
        """Generate executive summary section"""
        total = len(vulnerabilities)
        critical_high = sum(1 for v in vulnerabilities if v.get('severity', '').lower() in ['critical', 'high'])
        medium = sum(1 for v in vulnerabilities if v.get('severity', '').lower() == 'medium')
        low = sum(1 for v in vulnerabilities if v.get('severity', '').lower() in ['low', 'informational'])
        
        summary = f"""## Executive Summary

                      This security audit identified *{total} potential issues* in the analyzed smart contract(s).

                      ### Issue Breakdown:
                      - 🔴 *Critical/High Severity:* {critical_high} issues
                      - 🟡 *Medium Severity:* {medium} issues  
                      - 🟢 *Low/Informational:* {low} issues

                      ### Risk Assessment:
                   """
        
        if critical_high > 0:
            summary += "⚠ *IMMEDIATE ACTION REQUIRED*: Critical vulnerabilities detected that could lead to loss of funds or contract compromise.\n\n"
        elif medium > 0:
            summary += "⚡ *ACTION RECOMMENDED*: Medium severity issues detected that should be addressed before mainnet deployment.\n\n"
        else:
            summary += "✅ *LOW RISK*: Only minor issues detected. Contract appears to follow security best practices.\n\n"
        
        # Add tool coverage
        tools_used = set(v.get('source', 'Unknown') for v in vulnerabilities)
        summary += f"*Analysis Tools Used:* {', '.join(tools_used)}"
        
        return summary
    
    def _vulnerability_details_template(self, vulnerabilities: List[Dict]) -> str:
        """Generate detailed vulnerability section"""
        details = "## Vulnerability Details\n\n"
        
        # Group by severity
        severity_groups = {
            'Critical': [],
            'High': [],
            'Medium': [],
            'Low': [],
            'Informational': []
        }
        
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'unknown').capitalize()
            if severity in severity_groups:
                severity_groups[severity].append(vuln)
        
        # Generate details for each severity level
        for severity, vulns in severity_groups.items():
            if vulns:
                details += f"### {severity} Severity Issues\n\n"
                
                for i, vuln in enumerate(vulns, 1):
                    details += f"#### {i}. {vuln.get('title', 'Untitled Issue')}\n\n"
                    details += f"*Tool:* {vuln.get('source', 'Unknown')}\n\n"
                    details += f"*Description:* {vuln.get('description', 'No description available')}\n\n"
                    
                    if vuln.get('location'):
                        details += f"*Location:* {vuln['location']}\n\n"
                    
                    if vuln.get('code_snippet') or vuln.get('code'):
                        code = vuln.get('code_snippet') or vuln.get('code')
                        details += f"*Code:*\nsolidity\n{code}\n\n\n"
                    
                    if vuln.get('recommendation'):
                        details += f"*Recommendation:* {vuln['recommendation']}\n\n"
                    
                    details += "---\n\n"
        
        return details
    
    def _code_analysis_template(self, vulnerabilities: List[Dict]) -> str:
        """Generate code analysis section"""
        analysis = "## Code Analysis\n\n"
        
        # Categorize issues by type
        issue_categories = {}
        for vuln in vulnerabilities:
            category = self._categorize_issue(vuln.get('title', ''))
            if category not in issue_categories:
                issue_categories[category] = []
            issue_categories[category].append(vuln)
        
        analysis += "### Issue Categories\n\n"
        for category, issues in issue_categories.items():
            analysis += f"- *{category}:* {len(issues)} issue(s)\n"
        
        analysis += "\n### Common Patterns Detected\n\n"
        
        # Check for common antipatterns
        patterns = {
            'Reentrancy': any('reentran' in str(v).lower() for v in vulnerabilities),
            'Unchecked Calls': any('unchecked' in str(v).lower() for v in vulnerabilities),
            'Access Control': any('access' in str(v).lower() or 'owner' in str(v).lower() for v in vulnerabilities),
            'Integer Issues': any('overflow' in str(v).lower() or 'underflow' in str(v).lower() for v in vulnerabilities)
        }
        
        for pattern, detected in patterns.items():
            if detected:
                analysis += f"- ⚠ {pattern} vulnerabilities detected\n"
        
        return analysis
    
    def _recommendations_template(self, vulnerabilities: List[Dict]) -> str:
        """Generate recommendations section"""
        recommendations = "## Recommendations\n\n"
        
        # Priority recommendations based on severity
        high_priority = [v for v in vulnerabilities if v.get('severity', '').lower() in ['critical', 'high']]
        medium_priority = [v for v in vulnerabilities if v.get('severity', '').lower() == 'medium']
        
        if high_priority:
            recommendations += "### 🔴 High Priority (Fix Immediately)\n\n"
            for vuln in high_priority[:5]:  # Top 5 critical issues
                recommendations += f"1. *{vuln.get('title', 'Issue')}*\n"
                recommendations += f"   - {vuln.get('recommendation', 'Review and fix this issue')}\n\n"
        
        if medium_priority:
            recommendations += "### 🟡 Medium Priority (Fix Before Deployment)\n\n"
            for vuln in medium_priority[:5]:  # Top 5 medium issues
                recommendations += f"1. *{vuln.get('title', 'Issue')}*\n"
                recommendations += f"   - {vuln.get('recommendation', 'Consider addressing this issue')}\n\n"
        
        # General recommendations
        recommendations += """### 📋 General Security Best Practices

1. *Implement Comprehensive Testing*
   - Write unit tests for all functions
   - Add integration tests for complex interactions
   - Consider formal verification for critical functions

2. *Use Security Tools in CI/CD*
   - Integrate Slither in your build pipeline
   - Run Mythril before each deployment
   - Consider using Echidna for property testing

3. *Follow Security Patterns*
   - Use OpenZeppelin contracts where applicable
   - Implement reentrancy guards
   - Follow checks-effects-interactions pattern

4. *Audit Process*
   - Conduct internal code reviews
   - Get external audit before mainnet deployment
   - Set up bug bounty program
"""
        
        return recommendations
    
    def _risk_matrix_template(self, vulnerabilities: List[Dict]) -> str:
        """Generate risk matrix section"""
        matrix = "## Risk Matrix\n\n"
        
        # Create risk matrix table
        matrix += "| Severity | Count | Risk Level | Action Required |\n"
        matrix += "|----------|-------|------------|----------------|\n"
        
        severities = {
            'Critical': {'count': 0, 'risk': 'Critical', 'action': 'Fix immediately'},
            'High': {'count': 0, 'risk': 'High', 'action': 'Fix before deployment'},
            'Medium': {'count': 0, 'risk': 'Medium', 'action': 'Fix recommended'},
            'Low': {'count': 0, 'risk': 'Low', 'action': 'Fix if possible'},
            'Informational': {'count': 0, 'risk': 'Info', 'action': 'Review'}
        }
        
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'unknown').capitalize()
            if severity in severities:
                severities[severity]['count'] += 1
        
        for severity, data in severities.items():
            if data['count'] > 0:
                matrix += f"| {severity} | {data['count']} | {data['risk']} | {data['action']} |\n"
        
        # Add risk score calculation
        risk_score = (
            severities['Critical']['count'] * 10 +
            severities['High']['count'] * 5 +
            severities['Medium']['count'] * 3 +
            severities['Low']['count'] * 1
        )
        
        matrix += f"\n### Overall Risk Score: {risk_score}/100\n"
        
        if risk_score > 30:
            matrix += "\n⚠ *High Risk*: Significant security improvements needed\n"
        elif risk_score > 10:
            matrix += "\n⚡ *Medium Risk*: Some security improvements recommended\n"
        else:
            matrix += "\n✅ *Low Risk*: Contract follows security best practices\n"
        
        return matrix
    
    def _categorize_issue(self, title: str) -> str:
        """Categorize issue based on title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['reentrancy', 'reentrant']):
            return 'Reentrancy'
        elif any(word in title_lower for word in ['overflow', 'underflow', 'arithmetic']):
            return 'Arithmetic'
        elif any(word in title_lower for word in ['access', 'owner', 'auth']):
            return 'Access Control'
        elif any(word in title_lower for word in ['unchecked', 'return', 'call']):
            return 'External Calls'
        elif any(word in title_lower for word in ['random', 'timestamp', 'block']):
            return 'Randomness'
        else:
            return 'Other'
    
    def _get_recommendations_data(self, vulnerabilities: List[Dict]) -> List[Dict]:
        """Get recommendations in structured format"""
        recommendations = []
        
        # Group similar vulnerabilities
        seen_titles = set()
        for vuln in vulnerabilities:
            title = vuln.get('title', '')
            if title not in seen_titles:
                seen_titles.add(title)
                recommendations.append({
                    'issue': title,
                    'severity': vuln.get('severity', 'unknown'),
                    'recommendation': vuln.get('recommendation', 'Review and fix this issue'),
                    'priority': 'High' if vuln.get('severity', '').lower() in ['critical', 'high'] else 'Medium'
                })
        
        return sorted(recommendations, key=lambda x: x['priority'])

# Module-level function
generator = ReportGenerator()

def generate_report(
    analysis_results: Dict[str, Any],
    report_name: str,
    format_type: str,
    sections: List[str],
    severity_filter: List[str]
) -> Dict[str, Any]:
    return generator.generate_report(
        analysis_results,
        report_name,
        format_type,
        sections,
        severity_filter
    )
