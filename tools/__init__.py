"""
Módulo de ferramentas (tools) para agentes
"""
# Example tools
from tools.example_tool import example_tool

# iGaming tools
from tools.igaming_search import search_betting_offers, get_major_betting_houses
from tools.tc_analyzer import analyze_terms_and_conditions, format_comparative_table

# Cost management tools
from tools.cost_manager import add_cost, list_costs, get_categories_summary, delete_cost
from tools.cost_reports import generate_monthly_report, get_expense_trends, export_to_dashboard_json

__all__ = [
    # Example
    'example_tool',
    # iGaming
    'search_betting_offers',
    'get_major_betting_houses',
    'analyze_terms_and_conditions',
    'format_comparative_table',
    # Cost Management
    'add_cost',
    'list_costs',
    'get_categories_summary',
    'delete_cost',
    'generate_monthly_report',
    'get_expense_trends',
    'export_to_dashboard_json',
]
