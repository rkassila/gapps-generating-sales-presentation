import os
import base64
from io import BytesIO
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from openai import OpenAI

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_SECRET"))
model = "gpt-3.5-turbo"

# Generate ChatGPT analysis
def chatgpt_analysis(df, model, report_month):
    prompt = f"""
        Analyze this sales data for {report_month}:
        - Top 3 products by sales and profit.
        - Regions with highest/lowest growth.
        - Any anomalies or trends.
        - 3 actionable recommendations.
        Data sample: {df.head().to_dict()}
        """
    response = openai_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

# Generate sales graph
def generate_sales_graph(df, report_month):
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x="Date", y="Sales", hue="Region")
    plt.title(f"Sales by Region - {report_month}")
    sales_graph_buffer = BytesIO()
    plt.savefig(sales_graph_buffer, format='png', bbox_inches='tight', dpi=100)
    plt.close()
    sales_graph_buffer.seek(0)
    return base64.b64encode(sales_graph_buffer.getvalue()).decode("utf-8")

# Generate profit graph
def generate_profit_graph(df, report_month):
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x="Product", y="Profit")
    plt.title(f"Profit by Product - {report_month}")
    profit_graph_buffer = BytesIO()
    plt.savefig(profit_graph_buffer, format='png', bbox_inches='tight', dpi=100)
    plt.close()
    profit_graph_buffer.seek(0)
    return base64.b64encode(profit_graph_buffer.getvalue()).decode("utf-8")

# Generate slides function
def generate_sales_slides(request):
    try:
        # Parse request
        request_json = request.get_json()
        headers = request_json["headers"]
        rows = request_json["rows"]
        report_month = request_json["reportMonth"]

        # Convert to Pandas DataFrame
        df = pd.DataFrame(rows, columns=headers)

        sales_graph_base64 = generate_sales_graph(df, report_month)
        profit_graph_base64 = generate_profit_graph(df, report_month)
        chatgpt_analysis = chatgpt_analysis(df, model, report_month)

        return {
            "status": "success",
            "salesGraph": sales_graph_base64,
            "profitGraph": profit_graph_base64,
            "analysis": chatgpt_analysis,
            "reportMonth": report_month
        }

    except Exception as e:
        return {"error": str(e), "status": "error"}
