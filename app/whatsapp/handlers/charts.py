from flask import current_app
import plotly.express as px
from app.utils import generate_temp_chart


def handle_chart_request(message, employee):
    """Handle chart generation requests"""
    try:
        chart_type = message.split()[1] if len(message.split()) > 1 else 'bar'

        # Reuse your existing visualization logic
        df = current_app.config['CURRENT_DATA']  # Replace with your data source

        if chart_type == 'bar':
            fig = px.bar(df, x='Variety', y='Surf. [ha]')
        elif chart_type == 'pie':
            fig = px.pie(df, names='Variety', values='Surf. [ha]')
        else:
            fig = px.line(df, x='Date creation', y='Surf. [ha]')

        chart_url = generate_temp_chart(fig)
        return f"Here's your {chart_type} chart 📊", chart_url

    except IndexError:
        return "Please specify chart type: !chart <bar/pie/line>", None
    except Exception as e:
        current_app.logger.error(f"Chart error: {str(e)}")
        return "Error generating chart. Please try again.", None