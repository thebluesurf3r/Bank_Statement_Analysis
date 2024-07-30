# Documentation

## Overview

The **Bank Statement Analysis and Visualization Tool** helps you understand your financial transactions. Use it to track spending, manage your budget, and explore your financial trends.

**Key Features:**

- **📅 Date Range Selection**: Filter transactions by custom date ranges to focus on specific periods.
- **💸 Amount Filtering**: Identify transactions above or below certain amounts.
- **📊 Balance Tracking**: Keep track of your account balance over time.
- **📁 Categorization**: Automatically categorize transactions into types like groceries, utilities, and travel.
- **🔍 Entity Extraction**: Extract names or entities from transaction descriptions.
- **📈 Interactive Visualizations**: View and interact with charts and graphs to understand your financial data.

## Schema Definition

**Dimensions:**

- **`transaction_date`**: The date of the transaction.
- **`transaction_names`**: Names or descriptions of transactions.
- **`transaction_category`**: Categories of transactions.
- **`description`**: Additional notes or details about transactions.

**Metrics:**

- **`amount`**: The value of the transaction.
- **`balance`**: The account balance over time.
- **`credit_debit_value`**: Whether a transaction is a credit or debit.
- **`transaction_count`**: The number of transactions.

## Data Analysis

The tool uses **Pandas** and **Numpy** for analyzing your data:

- **Pandas**: Handles data cleaning, aggregation (like total spending per category), and time series analysis.
- **Numpy**: Performs numerical calculations and statistical analysis (such as mean and median).

## Data Visualization

Visualizations are created with **Plotly**, including:

- **Line Graph**: Shows spending trends over time.
- **Transaction Names**: Displays a visual overview of transaction names.
- **Transaction Category**: Visualizes spending by category.
- **Scatter 3D**: Maps `transaction_count`, `amount`, and `balance`. It helps visualize the relationship between the number of transactions, their amounts, and the balance over time, providing insights into transaction frequency, spending patterns, and how they affect the balance.
- **Parallel Categories**: To connect `transaction_category`, `transaction_names`, and `transaction_date`. It shows how different categories and names relate to transaction dates, helping you understand the distribution of transactions across categories and time periods.
- **Cross-Filtering**: All visualizations are cross-filtered, allowing you to interact with data across different charts for a cohesive analysis experience.
