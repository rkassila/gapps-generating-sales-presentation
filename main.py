import os
import json
import logging
import base64
from io import BytesIO
import pandas as pd
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_sales_slides(request):
    try:
        # Parse request
        request_json = request.get_json()
        headers = request_json["headers"]
        rows = request_json["rows"]
        report_month = request_json["reportMonth"]

        # Convert to Pandas DataFrame
        df = pd.DataFrame(rows, columns=headers)
        logger.info(f"DataFrame shape: {df.shape}")

        # Generate graphs
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df, x="Date", y="Sales", hue="Region")
        plt.title(f"Sales by Region - {report_month}")
        sales_graph_buffer = BytesIO()
        plt.savefig(sales_graph_buffer, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        sales_graph_buffer.seek(0)
        sales_graph_base64 = base64.b64encode(sales_graph_buffer.getvalue()).decode("utf-8")

        plt.figure(figsize=(10, 6))
        sns.barplot(data=df, x="Product", y="Profit")
        plt.title(f"Profit by Product - {report_month}")
        profit_graph_buffer = BytesIO()
        plt.savefig(profit_graph_buffer, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        profit_graph_buffer.seek(0)
        profit_graph_base64 = base64.b64encode(profit_graph_buffer.getvalue()).decode("utf-8")

        # Generate ChatGPT analysis
        prompt = f"""
        Analyze this sales data for {report_month}:
        - Top 3 products by sales and profit.
        - Regions with highest/lowest growth.
        - Any anomalies or trends.
        - 3 actionable recommendations.
        Data sample: {df.head().to_dict()}
        """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        chatgpt_analysis = response["choices"][0]["message"]["content"]

        return {
            "status": "success",
            "salesGraph": sales_graph_base64,
            "profitGraph": profit_graph_base64,
            "analysis": chatgpt_analysis,
            "reportMonth": report_month
        }

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return {"error": str(e), "status": "error"}
