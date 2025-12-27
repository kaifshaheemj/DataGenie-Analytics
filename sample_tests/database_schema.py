"""
AdventureWorks Database Schema Metadata
========================================

This file contains the complete database schema information that the Dashboard Agent
uses to intelligently generate analytical questions.

The Dashboard Agent reads this schema and cognitively understands what questions
can be answered with the available data.
"""

DATABASE_SCHEMA = {
    "database_name": "DataGenie-Analytics",
    "description": "AdventureWorks retail and manufacturing business data (2020-2022)",
    
    "tables": {
        "fact_sales": {
            "type": "fact",
            "description": "Core sales transactions",
            "row_count": "~105,000",
            "columns": {
                "sales_id": {
                    "type": "SERIAL",
                    "description": "Auto-incrementing primary key"
                },
                "order_date": {
                    "type": "DATE",
                    "description": "Date when order was placed",
                    "analysis_potential": "time_series, trends, seasonality"
                },
                "stock_date": {
                    "type": "DATE",
                    "description": "Date when product was stocked"
                },
                "order_number": {
                    "type": "VARCHAR(20)",
                    "description": "Unique order identifier (e.g., SO45080)"
                },
                "product_key": {
                    "type": "INTEGER",
                    "description": "Foreign key to dim_products",
                    "references": "dim_products.product_key"
                },
                "customer_key": {
                    "type": "INTEGER",
                    "description": "Foreign key to dim_customers",
                    "references": "dim_customers.customer_key"
                },
                "territory_key": {
                    "type": "INTEGER",
                    "description": "Foreign key to dim_territories",
                    "references": "dim_territories.sales_territory_key"
                },
                "order_line_item": {
                    "type": "INTEGER",
                    "description": "Line item number within order"
                },
                "order_quantity": {
                    "type": "INTEGER",
                    "description": "Quantity of items ordered",
                    "analysis_potential": "volume_analysis"
                }
            },
            "business_purpose": "Track all sales transactions for revenue and performance analysis",
            "key_metrics": [
                "revenue (calculated as order_quantity * product_price)",
                "profit (calculated as order_quantity * (product_price - product_cost))",
                "units_sold",
                "average_order_value"
            ]
        },
        
        "fact_returns": {
            "type": "fact",
            "description": "Product returns tracking",
            "row_count": "~1,500",
            "columns": {
                "return_id": {
                    "type": "SERIAL",
                    "description": "Auto-incrementing primary key"
                },
                "return_date": {
                    "type": "DATE",
                    "description": "Date of product return",
                    "analysis_potential": "return_rate_trends"
                },
                "territory_key": {
                    "type": "INTEGER",
                    "description": "Foreign key to dim_territories",
                    "references": "dim_territories.sales_territory_key"
                },
                "product_key": {
                    "type": "INTEGER",
                    "description": "Foreign key to dim_products",
                    "references": "dim_products.product_key"
                },
                "return_quantity": {
                    "type": "INTEGER",
                    "description": "Number of items returned"
                }
            },
            "business_purpose": "Track product returns for quality analysis and customer satisfaction",
            "key_metrics": [
                "return_rate (returns / sales * 100)",
                "return_value",
                "net_sales (sales - returns)"
            ]
        },
        
        "dim_products": {
            "type": "dimension",
            "description": "Product catalog with pricing and cost information",
            "row_count": "~600",
            "columns": {
                "product_key": {
                    "type": "INTEGER",
                    "description": "Primary key"
                },
                "product_subcategory_key": {
                    "type": "INTEGER",
                    "description": "Foreign key to dim_product_subcategories",
                    "references": "dim_product_subcategories.product_subcategory_key"
                },
                "product_sku": {
                    "type": "VARCHAR(50)",
                    "description": "Stock Keeping Unit identifier"
                },
                "product_name": {
                    "type": "VARCHAR(100)",
                    "description": "Full product name"
                },
                "model_name": {
                    "type": "VARCHAR(50)",
                    "description": "Product model identifier"
                },
                "product_description": {
                    "type": "TEXT",
                    "description": "Detailed product description"
                },
                "product_color": {
                    "type": "VARCHAR(20)",
                    "description": "Product color"
                },
                "product_size": {
                    "type": "VARCHAR(10)",
                    "description": "Product size (e.g., M, L, XL)"
                },
                "product_style": {
                    "type": "VARCHAR(10)",
                    "description": "Product style code"
                },
                "product_cost": {
                    "type": "DECIMAL(10,4)",
                    "description": "Cost to company",
                    "analysis_potential": "profitability"
                },
                "product_price": {
                    "type": "DECIMAL(10,4)",
                    "description": "Selling price",
                    "analysis_potential": "revenue, profitability"
                }
            },
            "business_purpose": "Master product data for sales and profitability analysis"
        },
        
        "dim_product_subcategories": {
            "type": "dimension",
            "description": "Product subcategory classification",
            "row_count": "~37",
            "columns": {
                "product_subcategory_key": {
                    "type": "INTEGER",
                    "description": "Primary key"
                },
                "subcategory_name": {
                    "type": "VARCHAR(100)",
                    "description": "Subcategory name (e.g., Mountain Bikes, Road Bikes)"
                },
                "product_category_key": {
                    "type": "INTEGER",
                    "description": "Foreign key to dim_product_categories",
                    "references": "dim_product_categories.product_category_key"
                }
            },
            "business_purpose": "Second-level product classification for detailed analysis"
        },
        
        "dim_product_categories": {
            "type": "dimension",
            "description": "Top-level product categories",
            "row_count": "4",
            "columns": {
                "product_category_key": {
                    "type": "INTEGER",
                    "description": "Primary key"
                },
                "category_name": {
                    "type": "VARCHAR(50)",
                    "description": "Category name (Bikes, Components, Clothing, Accessories)"
                }
            },
            "business_purpose": "Top-level product grouping for strategic analysis",
            "categories": ["Bikes", "Components", "Clothing", "Accessories"]
        },
        
        "dim_customers": {
            "type": "dimension",
            "description": "Customer demographics and attributes",
            "row_count": "~18,484",
            "columns": {
                "customer_key": {
                    "type": "INTEGER",
                    "description": "Primary key"
                },
                "prefix": {
                    "type": "VARCHAR(10)",
                    "description": "Title (Mr., Ms., etc.)"
                },
                "first_name": {
                    "type": "VARCHAR(50)",
                    "description": "Customer first name"
                },
                "last_name": {
                    "type": "VARCHAR(50)",
                    "description": "Customer last name"
                },
                "birth_date": {
                    "type": "DATE",
                    "description": "Date of birth",
                    "analysis_potential": "age_segmentation"
                },
                "marital_status": {
                    "type": "VARCHAR(10)",
                    "description": "Marital status (M=Married, S=Single)",
                    "analysis_potential": "demographic_segmentation"
                },
                "gender": {
                    "type": "VARCHAR(10)",
                    "description": "Gender (M/F)",
                    "analysis_potential": "demographic_segmentation"
                },
                "email_address": {
                    "type": "VARCHAR(100)",
                    "description": "Customer email"
                },
                "annual_income": {
                    "type": "INTEGER",
                    "description": "Annual income in dollars",
                    "analysis_potential": "income_segmentation, customer_value"
                },
                "total_children": {
                    "type": "INTEGER",
                    "description": "Number of children",
                    "analysis_potential": "demographic_segmentation"
                },
                "education_level": {
                    "type": "VARCHAR(50)",
                    "description": "Education qualification",
                    "analysis_potential": "demographic_segmentation"
                },
                "occupation": {
                    "type": "VARCHAR(50)",
                    "description": "Job category",
                    "analysis_potential": "demographic_segmentation"
                },
                "home_owner": {
                    "type": "VARCHAR(10)",
                    "description": "Home ownership (Y/N)",
                    "analysis_potential": "demographic_segmentation"
                }
            },
            "business_purpose": "Customer master data for segmentation and lifetime value analysis"
        },
        
        "dim_territories": {
            "type": "dimension",
            "description": "Geographic sales territories",
            "row_count": "~10",
            "columns": {
                "sales_territory_key": {
                    "type": "INTEGER",
                    "description": "Primary key"
                },
                "region": {
                    "type": "VARCHAR(50)",
                    "description": "Region name (e.g., Northwest, Northeast)",
                    "analysis_potential": "regional_analysis"
                },
                "country": {
                    "type": "VARCHAR(50)",
                    "description": "Country name",
                    "analysis_potential": "country_analysis"
                },
                "continent": {
                    "type": "VARCHAR(50)",
                    "description": "Continent name",
                    "analysis_potential": "continental_analysis"
                }
            },
            "business_purpose": "Geographic hierarchy for regional performance analysis",
            "geographic_levels": ["continent", "country", "region"]
        },
        
        "dim_calendar": {
            "type": "dimension",
            "description": "Date dimension for time-based analysis",
            "row_count": "~912",
            "columns": {
                "date": {
                    "type": "DATE",
                    "description": "Date value"
                },
                "year": {
                    "type": "INTEGER",
                    "description": "Year (2020-2022)",
                    "analysis_potential": "yearly_trends"
                },
                "quarter": {
                    "type": "INTEGER",
                    "description": "Quarter (1-4)",
                    "analysis_potential": "quarterly_analysis"
                },
                "month": {
                    "type": "INTEGER",
                    "description": "Month (1-12)",
                    "analysis_potential": "monthly_trends, seasonality"
                },
                "month_name": {
                    "type": "VARCHAR(20)",
                    "description": "Month name (January, February, etc.)"
                },
                "day_of_week": {
                    "type": "INTEGER",
                    "description": "Day of week (0-6)",
                    "analysis_potential": "day_of_week_patterns"
                },
                "day_name": {
                    "type": "VARCHAR(20)",
                    "description": "Day name (Monday, Tuesday, etc.)"
                },
                "week_of_year": {
                    "type": "INTEGER",
                    "description": "Week number (1-52)",
                    "analysis_potential": "weekly_trends"
                }
            },
            "business_purpose": "Time dimension for temporal analysis and trend detection",
            "time_periods": ["2020", "2021", "2022"]
        }
    },
    
    "relationships": {
        "fact_sales_to_products": {
            "from": "fact_sales.product_key",
            "to": "dim_products.product_key",
            "type": "many_to_one",
            "enables": "Product performance analysis, category analysis, profitability"
        },
        "fact_sales_to_customers": {
            "from": "fact_sales.customer_key",
            "to": "dim_customers.customer_key",
            "type": "many_to_one",
            "enables": "Customer lifetime value, segmentation, demographic analysis"
        },
        "fact_sales_to_territories": {
            "from": "fact_sales.territory_key",
            "to": "dim_territories.sales_territory_key",
            "type": "many_to_one",
            "enables": "Regional performance, geographic expansion analysis"
        },
        "fact_sales_to_calendar": {
            "from": "fact_sales.order_date",
            "to": "dim_calendar.date",
            "type": "many_to_one",
            "enables": "Time-series analysis, trends, seasonality"
        },
        "products_to_subcategories": {
            "from": "dim_products.product_subcategory_key",
            "to": "dim_product_subcategories.product_subcategory_key",
            "type": "many_to_one",
            "enables": "Subcategory performance analysis"
        },
        "subcategories_to_categories": {
            "from": "dim_product_subcategories.product_category_key",
            "to": "dim_product_categories.product_category_key",
            "type": "many_to_one",
            "enables": "Category-level strategic analysis"
        },
        "returns_to_products": {
            "from": "fact_returns.product_key",
            "to": "dim_products.product_key",
            "type": "many_to_one",
            "enables": "Product quality analysis, return rate calculation"
        },
        "returns_to_territories": {
            "from": "fact_returns.territory_key",
            "to": "dim_territories.sales_territory_key",
            "type": "many_to_one",
            "enables": "Regional return rate analysis"
        }
    },
    
    "calculated_metrics": {
        "revenue": {
            "formula": "SUM(fact_sales.order_quantity * dim_products.product_price)",
            "description": "Total sales revenue",
            "tables_required": ["fact_sales", "dim_products"]
        },
        "cost": {
            "formula": "SUM(fact_sales.order_quantity * dim_products.product_cost)",
            "description": "Total cost of goods sold",
            "tables_required": ["fact_sales", "dim_products"]
        },
        "profit": {
            "formula": "SUM(fact_sales.order_quantity * (dim_products.product_price - dim_products.product_cost))",
            "description": "Total profit (revenue - cost)",
            "tables_required": ["fact_sales", "dim_products"]
        },
        "profit_margin": {
            "formula": "(profit / revenue) * 100",
            "description": "Profit margin percentage",
            "tables_required": ["fact_sales", "dim_products"]
        },
        "return_rate": {
            "formula": "(SUM(fact_returns.return_quantity) / SUM(fact_sales.order_quantity)) * 100",
            "description": "Percentage of products returned",
            "tables_required": ["fact_sales", "fact_returns"]
        },
        "customer_lifetime_value": {
            "formula": "SUM(revenue) per customer",
            "description": "Total revenue generated by each customer",
            "tables_required": ["fact_sales", "dim_customers", "dim_products"]
        },
        "average_order_value": {
            "formula": "SUM(revenue) / COUNT(DISTINCT order_number)",
            "description": "Average value per order",
            "tables_required": ["fact_sales", "dim_products"]
        }
    },
    
    "business_dimensions": {
        "temporal": {
            "description": "Time-based analysis",
            "dimensions": ["year", "quarter", "month", "week", "day_of_week"],
            "analysis_types": ["trends", "seasonality", "year_over_year", "month_over_month"]
        },
        "product": {
            "description": "Product hierarchy analysis",
            "levels": ["category", "subcategory", "product"],
            "analysis_types": ["performance", "mix", "profitability", "returns"]
        },
        "geography": {
            "description": "Geographic analysis",
            "levels": ["continent", "country", "region"],
            "analysis_types": ["regional_performance", "expansion_opportunities", "market_penetration"]
        },
        "customer": {
            "description": "Customer segmentation",
            "segments": ["income_level", "age_group", "occupation", "education", "demographics"],
            "analysis_types": ["lifetime_value", "acquisition", "retention", "behavior"]
        }
    },
    
    "common_business_questions": {
        "revenue_analysis": [
            "Total revenue over time",
            "Revenue by product category",
            "Revenue by region",
            "Revenue growth rates"
        ],
        "product_performance": [
            "Top performing products",
            "Product profitability",
            "Product mix analysis",
            "New vs existing products"
        ],
        "customer_insights": [
            "Customer segmentation",
            "Customer lifetime value",
            "Customer acquisition trends",
            "High-value customer identification"
        ],
        "operational_metrics": [
            "Return rates by product/category",
            "Inventory turnover",
            "Order fulfillment patterns",
            "Seasonal demand patterns"
        ],
        "strategic_analysis": [
            "Market expansion opportunities",
            "Pricing strategy effectiveness",
            "Product portfolio optimization",
            "Competitive positioning"
        ]
    }
}

def get_schema_summary():
    """Get a concise summary of the database schema."""
    return {
        "total_tables": len(DATABASE_SCHEMA["tables"]),
        "fact_tables": len([t for t in DATABASE_SCHEMA["tables"].values() if t["type"] == "fact"]),
        "dimension_tables": len([t for t in DATABASE_SCHEMA["tables"].values() if t["type"] == "dimension"]),
        "total_relationships": len(DATABASE_SCHEMA["relationships"]),
        "calculated_metrics": len(DATABASE_SCHEMA["calculated_metrics"]),
        "business_dimensions": len(DATABASE_SCHEMA["business_dimensions"])
    }

def get_table_info(table_name):
    """Get detailed information about a specific table."""
    return DATABASE_SCHEMA["tables"].get(table_name, None)

def get_all_table_names():
    """Get list of all table names."""
    return list(DATABASE_SCHEMA["tables"].keys())

def get_fact_tables():
    """Get list of fact table names."""
    return [name for name, info in DATABASE_SCHEMA["tables"].items() if info["type"] == "fact"]

def get_dimension_tables():
    """Get list of dimension table names."""
    return [name for name, info in DATABASE_SCHEMA["tables"].items() if info["type"] == "dimension"]
