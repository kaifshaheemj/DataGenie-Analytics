import plotly.express as px
import pandas as pd

df = pd.DataFrame({
    "category": ["Bikes", "Clothing", "Accessories"],
    "revenue": [450000, 120000, 65000]
})

fig = px.bar(df, x="category", y="revenue", title="Revenue Test Chart")
fig.show()
