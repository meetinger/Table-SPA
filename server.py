import codecs
import json

import psycopg2
from http.server import HTTPServer, BaseHTTPRequestHandler

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

    def do_POST(self):
        print(self.path)
        if self.path == "/getData":
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            payload = json.loads(body.decode('utf-8'))
            print(payload)

            params = payload['params']

            cursor = conn.cursor()

            cursor.execute('SELECT * FROM table_datarow')

            fetch_all = cursor.fetchall()
            print(fetch_all)
            data_rows = [DataRow(i) for i in fetch_all]

            res = []

            if payload['method'] == 'search':
                condition = params['condition']
                column = params['column']
                search_value = params['searchValue']

                if condition != "has" and column != "name":
                    search_value = float(search_value)

                def filter_func(x):
                    x_dict = x.to_dict()
                    if condition == 'equal':
                        return x_dict[column] == search_value
                    elif condition == 'more':
                        return x_dict[column] > search_value
                    elif condition == 'less':
                        return x_dict[column] < search_value
                    elif condition == 'has':
                        return search_value in x_dict[column]

                res = list(filter(filter_func, data_rows))
            elif payload['method'] == 'getAll':
                res = data_rows

            print(res)

            data = {'data': res[params['leftBound']:params['rightBound']], 'lengthAll': len(res)}

            print(data)
            json_str = json.dumps(data, cls=DataRowJSONEncoder)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json_str.encode(encoding='utf-8'))


httpd = HTTPServer(('localhost', config['http_port']), SimpleHTTPRequestHandler)
print("Starting Server...")
httpd.serve_forever()
