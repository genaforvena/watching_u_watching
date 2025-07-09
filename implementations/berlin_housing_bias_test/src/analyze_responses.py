"""
Analysis and Reporting Tools for Berlin Housing Bias Testing

This module provides tools to analyze collected responses and generate
reports on potential bias patterns.
"""

import sqlite3
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path


class BiasAnalyzer:
    """
    Analyzes collected response data for bias patterns.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize the bias analyzer.
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = db_path
        
    def get_response_statistics(self) -> Dict:
        """Get basic response statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Overall statistics
                cursor.execute('SELECT COUNT(*) FROM properties')
                total_properties = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM applications')
                total_applications = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM submissions WHERE success = 1')
                successful_submissions = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM responses')
                total_responses = cursor.fetchone()[0]
                
                # Response rates by persona
                cursor.execute('''
                    SELECT persona, COUNT(*) 
                    FROM responses 
                    GROUP BY persona
                ''')
                response_by_persona = dict(cursor.fetchall())
                
                # Properties with responses
                cursor.execute('''
                    SELECT COUNT(DISTINCT property_id) 
                    FROM responses
                ''')
                properties_with_responses = cursor.fetchone()[0]
                
                return {
                    'total_properties': total_properties,
                    'total_applications': total_applications,
                    'successful_submissions': successful_submissions,
                    'total_responses': total_responses,
                    'properties_with_responses': properties_with_responses,
                    'response_by_persona': response_by_persona,
                    'overall_response_rate': total_responses / successful_submissions if successful_submissions > 0 else 0
                }
                
        except Exception as e:
            logging.error(f"Error getting response statistics: {e}")
            return {}
    
    def analyze_response_patterns(self) -> Dict:
        """Analyze response patterns for bias indicators."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get property-level response data
                cursor.execute('''
                    SELECT 
                        p.id,
                        p.title,
                        p.location,
                        p.price,
                        COUNT(CASE WHEN r.persona = 'mohammed_abasi' THEN 1 END) as mohammed_responses,
                        COUNT(CASE WHEN r.persona = 'franz_muller' THEN 1 END) as franz_responses,
                        MIN(CASE WHEN r.persona = 'mohammed_abasi' THEN r.response_received_at END) as mohammed_first_response,
                        MIN(CASE WHEN r.persona = 'franz_muller' THEN r.response_received_at END) as franz_first_response
                    FROM properties p
                    LEFT JOIN applications a ON p.id = a.property_id
                    LEFT JOIN submissions s ON a.id = s.application_id AND s.success = 1
                    LEFT JOIN responses r ON s.id = r.submission_id
                    GROUP BY p.id
                    HAVING COUNT(s.id) >= 2  -- Only properties with applications from both personas
                ''')
                
                property_data = cursor.fetchall()
                
                if not property_data:
                    return {'error': 'No data available for analysis'}
                
                analysis = {
                    'properties_analyzed': len(property_data),
                    'mohammed_response_rate': 0,
                    'franz_response_rate': 0,
                    'bias_indicators': [],
                    'response_time_analysis': {},
                    'property_details': []
                }
                
                mohammed_total_responses = 0
                franz_total_responses = 0
                response_time_differences = []
                
                for prop in property_data:
                    prop_id, title, location, price, mohammed_resp, franz_resp, mohammed_time, franz_time = prop
                    
                    mohammed_total_responses += mohammed_resp
                    franz_total_responses += franz_resp
                    
                    # Response time analysis
                    time_diff = None
                    if mohammed_time and franz_time:
                        mohammed_dt = datetime.fromisoformat(mohammed_time.replace('Z', '+00:00'))
                        franz_dt = datetime.fromisoformat(franz_time.replace('Z', '+00:00'))
                        time_diff = (mohammed_dt - franz_dt).total_seconds() / 3600  # Hours
                        response_time_differences.append(time_diff)
                    
                    analysis['property_details'].append({
                        'property_id': prop_id,
                        'title': title,
                        'location': location,
                        'price': price,
                        'mohammed_responses': mohammed_resp,
                        'franz_responses': franz_resp,
                        'response_time_difference_hours': time_diff
                    })
                
                # Calculate overall response rates
                total_properties = len(property_data)
                analysis['mohammed_response_rate'] = mohammed_total_responses / total_properties
                analysis['franz_response_rate'] = franz_total_responses / total_properties
                
                # Response time analysis
                if response_time_differences:
                    avg_time_diff = sum(response_time_differences) / len(response_time_differences)
                    analysis['response_time_analysis'] = {
                        'average_time_difference_hours': avg_time_diff,
                        'properties_with_time_data': len(response_time_differences)
                    }
                
                # Bias indicators
                if franz_total_responses > 0:
                    response_ratio = mohammed_total_responses / franz_total_responses
                    
                    if response_ratio < 0.7:
                        analysis['bias_indicators'].append({
                            'type': 'LOW_MOHAMMED_RESPONSE_RATE',
                            'severity': 'HIGH',
                            'description': f'Mohammed receives {response_ratio:.2f}x as many responses as Franz',
                            'ratio': response_ratio
                        })
                    elif response_ratio < 0.9:
                        analysis['bias_indicators'].append({
                            'type': 'MODERATE_MOHAMMED_RESPONSE_RATE',
                            'severity': 'MEDIUM', 
                            'description': f'Mohammed receives {response_ratio:.2f}x as many responses as Franz',
                            'ratio': response_ratio
                        })
                
                # Check for properties where only Franz gets responses
                franz_only_count = len([p for p in property_data if p[4] == 0 and p[5] > 0])
                if franz_only_count > 0:
                    analysis['bias_indicators'].append({
                        'type': 'FRANZ_ONLY_RESPONSES',
                        'severity': 'HIGH',
                        'description': f'{franz_only_count} properties responded only to Franz',
                        'count': franz_only_count
                    })
                
                return analysis
                
        except Exception as e:
            logging.error(f"Error in bias analysis: {e}")
            return {'error': str(e)}
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """Generate a comprehensive bias analysis report."""
        stats = self.get_response_statistics()
        analysis = self.analyze_response_patterns()
        
        report_lines = [
            "BERLIN HOUSING MARKET BIAS ANALYSIS REPORT",
            "=" * 50,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "OVERVIEW",
            "-" * 20,
            f"Total properties monitored: {stats.get('total_properties', 0)}",
            f"Total applications sent: {stats.get('total_applications', 0)}",
            f"Successful submissions: {stats.get('successful_submissions', 0)}",
            f"Total responses received: {stats.get('total_responses', 0)}",
            f"Properties with responses: {stats.get('properties_with_responses', 0)}",
            f"Overall response rate: {stats.get('overall_response_rate', 0):.2%}",
            "",
            "RESPONSE RATES BY PERSONA",
            "-" * 30,
        ]
        
        response_by_persona = stats.get('response_by_persona', {})
        for persona, count in response_by_persona.items():
            report_lines.append(f"{persona}: {count} responses")
        
        if 'error' not in analysis:
            report_lines.extend([
                "",
                "BIAS ANALYSIS",
                "-" * 20,
                f"Properties analyzed: {analysis.get('properties_analyzed', 0)}",
                f"Mohammed response rate: {analysis.get('mohammed_response_rate', 0):.2f} responses/property",
                f"Franz response rate: {analysis.get('franz_response_rate', 0):.2f} responses/property",
                ""
            ])
            
            bias_indicators = analysis.get('bias_indicators', [])
            if bias_indicators:
                report_lines.append("BIAS INDICATORS DETECTED:")
                for indicator in bias_indicators:
                    report_lines.append(f"  [{indicator['severity']}] {indicator['description']}")
            else:
                report_lines.append("No significant bias indicators detected.")
            
            # Response time analysis
            time_analysis = analysis.get('response_time_analysis', {})
            if time_analysis:
                report_lines.extend([
                    "",
                    "RESPONSE TIME ANALYSIS",
                    "-" * 25,
                    f"Average time difference: {time_analysis.get('average_time_difference_hours', 0):.1f} hours",
                    f"(Positive = Mohammed responded to first, Negative = Franz responded to first)"
                ])
        else:
            report_lines.append(f"Analysis error: {analysis['error']}")
        
        report_text = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            logging.info(f"Report saved to {output_file}")
        
        return report_text


def main():
    """Command-line interface for analysis tools."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Berlin Housing Bias Analysis Tools")
    parser.add_argument('--db', default='data/housing_bias_test.db', help='Database file path')
    parser.add_argument('--output', help='Output file for report')
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    
    args = parser.parse_args()
    
    if not Path(args.db).exists():
        print(f"Database file not found: {args.db}")
        return
    
    analyzer = BiasAnalyzer(args.db)
    
    if args.format == 'json':
        stats = analyzer.get_response_statistics()
        analysis = analyzer.analyze_response_patterns()
        result = {
            'statistics': stats,
            'analysis': analysis,
            'generated_at': datetime.now().isoformat()
        }
        
        output_text = json.dumps(result, indent=2, ensure_ascii=False)
    else:
        output_text = analyzer.generate_report()
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_text)
        print(f"Report saved to {args.output}")
    else:
        print(output_text)


if __name__ == "__main__":
    main()