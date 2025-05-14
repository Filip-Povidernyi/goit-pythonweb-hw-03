from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import mimetypes
import pathlib
from datetime import datetime
import json
from jinja2 import Environment, FileSystemLoader


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url_pr = urllib.parse.urlparse(self.path)
        if url_pr.path == '/':
            self.send_html_file('./home_work/src/index.html')
        elif url_pr.path == '/message':
            self.send_html_file('./home_work/src/message.html')
        elif url_pr.path == '/read':
            json_path = pathlib.Path('./home_work/src/storage/data.json')
            data = self.get_data(json_path)
            if data:

                self.render_data([value for value in data.values()])
                # self.send_html_file('./home_work/src/new_read.html')
            else:
                self.send_html_file('./home_work/src/error.html', 404)
        else:
            static_path = pathlib.Path(
                './home_work/src').joinpath(url_pr.path.lstrip('/'))
            if static_path.exists() and static_path.is_file():
                self.send_static(static_path)
            else:
                self.send_html_file('./home_work/src/error.html', 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        print(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        print(data_parse)
        dt = datetime.now()
        data_dict = {key: value for key, value in [
            el.split('=') for el in data_parse.split('&')]}
        print(data_dict)
        json_path = pathlib.Path('./home_work/src/storage/data.json')
        data = self.get_data(json_path)
        data[dt.strftime('%Y-%m-%d %H:%M:%S')] = data_dict
        print(data)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())

    def send_static(self, static_path):
        self.send_response(200)
        mime_type, _ = mimetypes.guess_type(static_path)
        if mime_type:
            self.send_header('Content-type', mime_type)
        else:
            self.send_header('Content-type', 'text/plain')
        self.end_headers()
        with open(f'{static_path}', 'rb') as f:
            self.wfile.write(f.read())

    def get_data(self, path):
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                try:
                    json_data = json.load(f)
                    return json_data
                except json.JSONDecodeError:
                    return {}
        else:
            return {}

    def render_data(self, data: list, status=200):
        env = Environment(loader=FileSystemLoader('./home_work/src'))
        template = env.get_template("read.html")
        output = template.render(data=data, )
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(output.encode('utf-8'))


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        print('Server started at http://localhost:3000')
        http.serve_forever()
    except KeyboardInterrupt:
        print('Server stopped by user')
        http.server_close()


if __name__ == '__main__':
    run()
