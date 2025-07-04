import pandas as pd
from scipy import stats

def analyze_responses(csv_path):
    """Bertrand & Mullainathan-style comparison"""
    df = pd.read_csv(csv_path)
    
    # Simple response rate comparison
    anglo_rate = df[df['type'] == 'anglo']['replied'].mean()
    minority_rate = df[df['type'] == 'minority']['replied'].mean()
    
    # Chi-square test
    contingency_table = pd.crosstab(df['type'], df['replied'])
    chi2, p, _, _ = stats.chi2_contingency(contingency_table)
    
    return {
        "anglo_response_rate": anglo_rate,
        "minority_response_rate": minority_rate,
        "p_value": p
    }
