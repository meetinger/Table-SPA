import codecs
import json

import psycopg2

from http.server import HTTPServer, BaseHTTPRequestHandler
from psycopg2 import sql
from DataRow import DataRow
from DataRowJSONEncoder import DataRowJSONEncoder
from config import config
from io import BytesIO

conn = psycopg2.connect(
    database=config['db_name'], user=config['db_user'], password=config['db_password'], host=config['db_host'],
    port=config['db_port']
)


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = open('static/html/index.html', 'rb')
            self.wfile.write(html.read())
        elif self.path.endswith('.css'):
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            style = open('static/css/' + self.path, 'rb')
            self.wfile.write(style.read())
        elif self.path.endswith('.ttf'):
            self.send_response(200)
            self.send_header('Content-type', 'text/x-font-ttf')
            self.end_headers()
            font = open('static/fonts/' + self.path, 'rb')
            self.wfile.write(font.read())
        else:
            self.send_response(404)

    def do_POST(self):
        # print(self.path)
        if self.path == "/getData":
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            payload = json.loads(body.decode('utf-8'))
            # print(payload)

            params = payload['params']

            cursor = conn.cursor()

            res = []

            if payload['method'] == 'search':
                condition = params['condition']
                column = params['column']
                search_value = params['searchValue']

                # if condition != "has" and column != "name":
                #     search_value = int(search_value)

                # Previously, there was a filter function with get all the rows of the table, but this is ineffective

                cast_dict = {
                    'name': str,
                    'amount': int,
                    'distance': int
                }

                query_dict = {
                    'equal': 'SELECT * FROM table_datarow WHERE {} = %(search_value)s',
                    'more': 'SELECT * FROM table_datarow WHERE {} > %(search_value)s',
                    'less': 'SELECT * FROM table_datarow WHERE {} < %(search_value)s',
                    'has': 'SELECT * FROM table_datarow WHERE {} ~ %(search_value)s'
                }

                query = sql.SQL(query_dict[condition])

                search_value_casted = cast_dict[column](search_value)

                if isinstance(search_value_casted, int) and condition == 'has':
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    cursor.close()
                    return

                cursor.execute(query.format(sql.Identifier(column)), {'search_value': search_value_casted})

            elif payload['method'] == 'getAll':
                cursor.execute('SELECT * FROM table_datarow')

            fetch_all = cursor.fetchall()
            data_rows = [DataRow(i) for i in fetch_all]
            res = data_rows

            # print(res)

            data = {'data': res[params['leftBound']:params['rightBound']], 'lengthAll': len(res)}

            # print(data)
            json_str = json.dumps(data, cls=DataRowJSONEncoder)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json_str.encode(encoding='utf-8'))
            cursor.close()
        else:
            self.send_response(404)


httpd = HTTPServer(('localhost', config['http_port']), SimpleHTTPRequestHandler)
print("Starting Server...")
httpd.serve_forever()
