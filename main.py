from google.cloud import bigquery

from models import reports

x = reports.reports(bigquery.Client(), '8735453121')
x
y = x()
y
with open('test.html', 'w') as f:
    f.write(y[1])
