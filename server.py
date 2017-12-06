#!/usr/bin/pyhton2
import BaseHTTPServer as BHS
import SocketServer as SS
from Crypto.Cipher import AES
from urlparse import parse_qs
import json, base64

iv = "SameIVisn'tgood."

class CryptoHandler(BHS.BaseHTTPRequestHandler):

    def address_string(self):
        host, port = self.client_address[:2]
        #return socket.getfqdn(host)
        return host

    def _set_headers(self,code=200,mime='text/html'):
        self.send_response(code)
        self.send_header('Content-type',mime)
        self.end_headers()

    def do_GET(self):
        try:
            if self.path == '/':
                self._set_headers(200)
                f = open("index.html","r")
                self.wfile.write(f.read())
            else:
                f = open('.'+self.path,'r')
                if self.path.split('.')[-1] == 'css':
                    self._set_headers(200,'text/css')
                elif self.path.split('.')[-1] == 'js':
                    self._set_headers(200,'text/javascript ')
                else:
                    self._set_headers(200)
                self.wfile.write(f.read())
        except IOError as io:
            self._set_headers(404)
            self.wfile.write('')

    def do_POST(self):
        jOut = "{}"
        try:
            if self.path == '/encrypt':
                data_string = self.rfile.read(int(self.headers['Content-Length']))
                jData = parse_qs(data_string)
                key = jData["key"][0]
                plain = jData["data"][0]
                crypter = AES.new(key, AES.MODE_CBC, iv)
                cipher = crypter.encrypt(pad(plain))
                jOut = json.dumps({'data':base64.b64encode(cipher)})
                self._set_headers(200,'application/json')

            elif self.path == '/decrypt':
                data_string = self.rfile.read(int(self.headers['Content-Length']))
                jData = parse_qs(data_string)
                key = jData['key'][0]
                cipher = base64.b64decode(jData['data'][0])
                crypter = AES.new(key, AES.MODE_CBC, iv)
                intermediate = crypter.decrypt(cipher)
                plain = unpad(intermediate)
                jOut = json.dumps({'data':plain}) # This line seems to be throwing an error on some strings
                                                  # I was able to fix the issue by forcing it to use the b64 encoding,
                                                  # but that obviously breaks the website output
                self._set_headers(200,'application/json')
            else:
                self._set_headers(404)
        except ValueError as ve:
            self._set_headers(500,'application/json')
            #print ve.message
            jOut = json.dumps({'error':ve.message})

        self.wfile.write(json.loads(jOut))
            
def pad(s):
    padByte = 16-len(s) % 16
    return s + chr(padByte)*padByte

def unpad(s):
    padByte = ord(s[-1])
    #print str(padByte)
    if padByte == 0 or padByte > 16:
        raise ValueError("Incorrect Padding Byte, greater than 16")
    for i in range(padByte):
        if ord(s[-(i+1)]) != padByte:
            raise ValueError("Incorrect Padding Byte, found data in the padding")
    return s[:-padByte]



port = 8080
Handler = CryptoHandler
httpd = SS.TCPServer(("",port),Handler)
print "Server running on port ",port
httpd.serve_forever()