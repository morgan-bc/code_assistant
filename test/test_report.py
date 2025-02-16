import pandas as pd
from code_assistant.reports import generate_pandas_report

df = pd.read_csv("output/reports_01.csv")
generate_pandas_report(df, "output/reports_01.html")