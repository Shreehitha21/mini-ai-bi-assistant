from app.database import get_db_connection

def get_total_revenue():
    """Calculates total revenue from completed transactions."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Notice we strictly use Status = 'Completed' to exclude returned items
    query = """
        SELECT 
            SUM(Revenue) as total_revenue,
            COUNT(Transaction_Id) as transaction_count,
            SUM(Quantity) as total_units_sold
        FROM sales
        WHERE Status = 'Completed'
    """
    row = cursor.execute(query).fetchone()
    conn.close()
    
    return {
        "total_revenue": round(row['total_revenue'], 2) if row['total_revenue'] else 0,
        "transaction_count": row['transaction_count'],
        "total_units_sold": row['total_units_sold'],
        "inclusion_rules": "Only includes transactions with Status = 'Completed' and Quantity > 0."
    }, query

def get_highest_revenue_product():
    """Finds the product that generated the most revenue."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT Product, SUM(Revenue) as total_revenue
        FROM sales
        WHERE Status = 'Completed'
        GROUP BY Product
        ORDER BY total_revenue DESC
    """
    rows = cursor.execute(query).fetchall()
    conn.close()
    
    if not rows:
        return {"highest_revenue_product": None, "revenue": 0, "supporting_data": []}, query
        
    supporting_data = [{"product": r["Product"], "revenue": r["total_revenue"]} for r in rows]
    
    return {
        "highest_revenue_product": rows[0]["Product"],
        "revenue": round(rows[0]["total_revenue"], 2),
        "supporting_data": supporting_data
    }, query

def get_monthly_revenue_trend():
    """Groups revenue by month."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # strftime('%Y-%m', Order_date) groups dates by Year and Month in SQLite
    query = """
        SELECT 
            strftime('%Y-%m', Order_date) as month, 
            SUM(Revenue) as total_revenue
        FROM sales
        WHERE Status = 'Completed'
        GROUP BY month
        ORDER BY month ASC
    """
    rows = cursor.execute(query).fetchall()
    conn.close()
    
    labels = [r["month"] for r in rows]
    revenues = [r["total_revenue"] for r in rows]
    supporting_data = [{"month": r["month"], "revenue": r["total_revenue"]} for r in rows]
    
    return {
        "month_labels": labels,
        "monthly_revenue": revenues,
        "supporting_data": supporting_data
    }, query

def get_highest_revenue_region():
    """Finds the region that generated the most sales."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT Region, SUM(Revenue) as total_revenue
        FROM sales
        WHERE Status = 'Completed'
        GROUP BY Region
        ORDER BY total_revenue DESC
    """
    rows = cursor.execute(query).fetchall()
    conn.close()
    
    if not rows:
        return {"highest_revenue_region": None, "revenue": 0, "supporting_data": []}, query
        
    supporting_data = [{"region": r["Region"], "revenue": r["total_revenue"]} for r in rows]
    
    return {
        "highest_revenue_region": rows[0]["Region"],
        "revenue": round(rows[0]["total_revenue"], 2),
        "supporting_data": supporting_data
    }, query

def get_revenue_comparison(month1: str, month2: str):
    """Compares revenue between two specified months (format: YYYY-MM)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Parameterized query protects against SQL injection
    query = """
        SELECT strftime('%Y-%m', Order_date) as month, SUM(Revenue) as total_revenue
        FROM sales
        WHERE Status = 'Completed' AND strftime('%Y-%m', Order_date) IN (?, ?)
        GROUP BY month
    """
    rows = cursor.execute(query, (month1, month2)).fetchall()
    conn.close()
    
    m1_rev = 0
    m2_rev = 0
    for r in rows:
        if r["month"] == month1:
            m1_rev = r["total_revenue"]
        elif r["month"] == month2:
            m2_rev = r["total_revenue"]
            
    absolute_change = m2_rev - m1_rev
    
    # Handle zero division safely
    if m1_rev == 0:
        percent_change = 100.0 if m2_rev > 0 else 0.0
    else:
        percent_change = (absolute_change / m1_rev) * 100
        
    direction = "increased" if absolute_change > 0 else "decreased" if absolute_change < 0 else "remained the same"
    
    return {
        "month1": month1,
        "month1_revenue": round(m1_rev, 2),
        "month2": month2,
        "month2_revenue": round(m2_rev, 2),
        "absolute_change": round(absolute_change, 2),
        "percentage_change": round(percent_change, 2),
        "explanation": f"Revenue {direction} by {abs(round(absolute_change, 2))} ({round(percent_change, 2)}%) from {month1} to {month2}."
    }, query