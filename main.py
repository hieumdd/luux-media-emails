from google.cloud import bigquery

from models import reports

x = reports.reports(bigquery.Client(), '8735453121', "Weekly")
x
y = x()
y
with open('test.html', 'w', encoding="utf-8") as f:
    f.write(y[1])
