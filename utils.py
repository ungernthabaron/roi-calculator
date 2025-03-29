import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def calculate_project_impact(inputs):
    """
    Calculate project impact based on various inputs
    This is a simplified version - you can expand the calculation logic
    """
    total_impact = 0
    
    # Example calculation (modify based on your specific requirements)
    if 'expected_revenue' in inputs:
        total_impact += inputs['expected_revenue'] * 0.3
    
    if 'cost_savings' in inputs:
        total_impact += inputs['cost_savings'] * 0.4
    
    if 'efficiency_improvement' in inputs:
        total_impact += inputs['efficiency_improvement'] * 0.3
    
    return total_impact

def create_impact_visualization(project_data):
    """
    Create visualizations for project impact analysis
    """
    # Create a sample visualization
    fig = go.Figure()
    
    # Add impact components
    fig.add_trace(go.Bar(
        name='Revenue Impact',
        x=['Revenue'],
        y=[project_data.get('expected_revenue', 0) * 0.3]
    ))
    
    fig.add_trace(go.Bar(
        name='Cost Savings',
        x=['Cost Savings'],
        y=[project_data.get('cost_savings', 0) * 0.4]
    ))
    
    fig.add_trace(go.Bar(
        name='Efficiency Impact',
        x=['Efficiency'],
        y=[project_data.get('efficiency_improvement', 0) * 0.3]
    ))
    
    fig.update_layout(
        title='Project Impact Breakdown',
        barmode='stack',
        yaxis_title='Impact Value'
    )
    
    return fig

def create_project_timeline(projects):
    """
    Create a timeline visualization of projects
    """
    df = pd.DataFrame(projects, columns=[
        'id', 'title', 'description', 'project_type', 'status',
        'customer_id', 'pm_estimate', 'it_director_estimate', 'created_at', 'customer_name'
    ])
    
    df['created_at'] = pd.to_datetime(df['created_at'])
    
    fig = px.scatter(df,
                    x='created_at',
                    y='project_type',
                    color='status',
                    hover_data=['title', 'customer_name'],
                    title='Project Timeline')
    
    return fig

def format_currency(value):
    """
    Format number as currency
    """
    return f"${value:,.2f}"

def get_status_color(status):
    """
    Get color for different statuses
    """
    status_colors = {
        'submitted': '#FFA500',  # Orange
        'estimated_by_pm': '#4169E1',  # Royal Blue
        'estimated_by_it': '#32CD32'  # Lime Green
    }
    return status_colors.get(status, '#808080')  # Default to gray 