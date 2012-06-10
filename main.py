
# Python 3.2.3
# CherryPy 3.2.2
# Dojo Toolkit Nightly build for 2012-05-20

import cherrypy
import os
import imaplib
import email
import email.mime.text
import email.header
import socket
import pprint
import html

import utf7imap

'''
email.parser.Parser
email.parser.BytesParser
何が違うのか？
適切に使い分けできているか？
'''

'''
セッション タイムアウトiで発生する KeyError と
その他の KeyError を区別するにはどうしたらよいか？
（あるいは区別する必要すらない状態にするとか・・・）
'''

'''
この位置に書いて・・・Thread-safe なのだろうか？不安だ。
'''
def myreplace(string):
    return string.replace(' ', '&nbsp;')

def hoge(x):
    buf = ''
    for ite in email.header.decode_header(x):
        data, charset = ite
        datatype = type(data).__name__
        # pprint.pprint(ite)
        # print(datatype)
        if datatype == 'bytes':
            if charset is None:
                buf += data.decode()
            else:
                buf += data.decode(charset)
        elif datatype == 'str':
            buf += data
        else:
            assert False
        buf += ' '
    return buf[:-1]

class Test1():

    @cherrypy.expose
    def index(self):
        return '<h1>hello</h1>'

    @cherrypy.expose
    def showmessage(self, uid):
        print('showmessage: ' + uid)
        buf = ''
        try:
            server = cherrypy.session['imap_server']
            user = cherrypy.session['imap_user']
            pwd = cherrypy.session['imap_pwd']
            folder = cherrypy.session['current_folder']
            print("folder: " + folder)
            imap = imaplib.IMAP4(server)
            imap.login(user, pwd)
            typ, [dat] = imap.select('"' + utf7imap.encoder(folder)[0].decode() + '"', True)
            if typ != 'OK':
                buf += html.escape(dat.decode())
            else:
                num_of_mails = int(dat.decode())
                if num_of_mails == 0:
                    pass
                else:
                    # typ, dat = imap.fetch(uid, '(BODY.PEEK[])')     # これでよいか？未読既読が変化すると嫌だ
                    typ, dat = imap.uid('FETCH', uid, '(BODY.PEEK[])')     # これでよいか？未読既読が変化すると嫌だ
                    assert typ == 'OK'
                    print('===================')
                    # pprint.pprint(dat)
                    # print(type(dat).__name__)
                    for x in dat:
                        if type(x).__name__ == 'tuple':
                            assert len(x) == 2
                            msg = email.parser.BytesParser().parsebytes(x[1], False)    # email.message.Message
                            '''
                            print(msg['subject'])
                            print(msg['date'])
                            print(msg['from'])
                            '''
                            buf += '<h1 data-dojo-type="dojox.mobile.Heading"'
                            buf += '    data-dojo-props="back:\'Messages\', moveTo:\'view3\', label:\'99 of 99\'">'
                            buf += '<ul data-dojo-type="dojox.mobile.TabBar" data-dojo-props=\'barType:"segmentedControl", selectOne:false\' style="float:right;">'
                            buf += '<li data-dojo-type="dojox.mobile.TabBarButton" data-dojo-props=\'icon:"mblDomButtonWhiteUpArrow"\'></li>'
                            buf += '<li data-dojo-type="dojox.mobile.TabBarButton" data-dojo-props=\'icon:"mblDomButtonWhiteDownArrow"\'></li>'
                            buf += '</ul>'
                            buf += '</h1>'
                            buf += '<ul data-dojo-type="dojox.mobile.EdgeToEdgeList" data-dojo-props=\'variableHeight:true\'>'
                            '''
                            buf += '<li data-dojo-type="dojox.mobile.ListItem" data-dojo-props=\'\'>From: </li>'
                            buf += '<li data-dojo-type="dojox.mobile.ListItem" data-dojo-props=\'\'>To: </li>'
                            '''
                            buf += '<li data-dojo-type="dojox.mobile.ListItem" data-dojo-props=\'\'>'
                            buf += '<div class="aaa2" >'
                            buf += myreplace('Subject: ' + html.escape(hoge(msg['subject']))) + '<br />'
                            buf += 'Date: ' + html.escape(msg['date']) + '<br />'
                            buf += myreplace('From: ' + html.escape(hoge(msg['from']))) + '<br />'
                            buf += 'To: ' + html.escape(msg['to']) + '<br />'
                            buf += '</div>'
                            buf += '</li>'
                            buf += '<li data-dojo-type="dojox.mobile.ListItem" data-dojo-props=\'\'>'
                            buf += '<div class="aaa2" style="font-family: monospace" >'
                            '''
                            print(msg.get_charset())
                            print(msg.get_content_type())
                            print(msg.get_content_charset())
                            '''
                            charset = msg.get_content_charset()
                            payload = msg.get_payload(decode=True)
                            payload = payload.decode(charset)
                            # print(type(payload))
                            # payload = html.escape(payload)
                            # payload = payload.replace('\r\n', '<br />\n')
                            # print(payload)
                            buf += '<pre>' + payload + '</pre>'
                            buf += '</div>'
                            buf += '</li>'
                            buf += '</ul>'
                            buf += ''
                        elif type(x).__name__ == 'bytes':
                            pass
                        else:
                            assert False
                    print('===================')
        except socket.gaierror as ex:
            return str(ex)
        except imaplib.IMAP4.error as ex:
            return str(ex)
        else:
            return buf

    @cherrypy.expose
    def listmessages(self, folder):
        print('listmessages: ' + folder)
        cherrypy.session['current_folder'] = folder     # @@@
        buf = ''
        buf += '<h1 data-dojo-type="dojox.mobile.Heading"'
        buf += '    data-dojo-props="back:\'Folders\', moveTo:\'viewFolders\', label:\'Messages\' " >'
        buf += '<span data-dojo-type="dojox.mobile.ToolBarButton" data-dojo-props=\'label:"Refresh"\' style="float:right;" ></span>'
        buf += '</h1>'
        try:
            server = cherrypy.session['imap_server']
            user = cherrypy.session['imap_user']
            pwd = cherrypy.session['imap_pwd']
            imap = imaplib.IMAP4(server)
            imap.login(user, pwd)
            # typ, [dat] = imap.select('"' + folder + '"', True)
            typ, [dat] = imap.select('"' + utf7imap.encoder(folder)[0].decode() + '"', True)
            if typ != 'OK':
                buf += html.escape(dat.decode())
            else:
                num_of_mails = int(dat.decode())
                if num_of_mails == 0:
                    pass
                else:
                    msg_ids = "1:" + str(num_of_mails)
                    typ, dat = imap.fetch(msg_ids, '(BODY.PEEK[HEADER] UID FLAGS)')
                    assert typ == 'OK'
                    # pprint.pprint(dat)
                    buf += '<ul data-dojo-type="dojox.mobile.RoundRectList" '
                    buf += '    data-dojo-props="variableHeight:true" >'
                    for x in dat:
                        if type(x).__name__ == 'tuple':
                            assert len(x) == 2
                            info = x[0].decode()    # 1 (UID 1 FLAGS (\Seen) BODY[HEADER] {3800}
                            uid = info.split()[2]
                            # print(info)
                            # print(uid)
                            lines = x[1].decode()
                            headers = email.parser.Parser().parsestr(lines, True)
                            subject = headers['subject']
                            subject_decoded = hoge(subject)
                            date = headers['date']
                            frm = headers['from']
                            frm_decoded = hoge(frm)
                            buf += '<li data-dojo-type="dojox.mobile.ListItem" '
                            buf += 'data-dojo-props="moveTo:\'#\', onClick:actShowMessage, '
                            # buf += 'label: \'' + subject_decoded + '\'">'
                            buf += 'UID: \'' + uid + '\' '
                            buf += '" >'
                            buf += '<div class="aaa1" >'
                            buf += myreplace(html.escape(subject_decoded))
                            buf += '</div>'
                            buf += '<div class="aaa2" >'
                            buf += myreplace(html.escape(frm_decoded)) + '<br />'
                            buf += myreplace(html.escape(date)) + '<br />'
                            buf += '</div>'
                            buf += '</li>'
                        elif type(x).__name__ == 'bytes':
                            pass
                        else:
                            assert False
                    buf += '</ul>'
        except socket.gaierror as ex:
            return str(ex)
        except imaplib.IMAP4.error as ex:
            return str(ex)
        else:
            return buf

    @cherrypy.expose
    def listfolders(self):
        buf = ''
        try:
            server = cherrypy.session['imap_server']
            user = cherrypy.session['imap_user']
            pwd = cherrypy.session['imap_pwd']
            imap = imaplib.IMAP4(server)
            imap.login(user, pwd)
            typ, dat = imap.list(directory='""', pattern='*')
            assert typ == 'OK'
            buf += '<h1 data-dojo-type="dojox.mobile.Heading"'
            buf += '    data-dojo-props="back:\'Log Out\', moveTo:\'view1\', label:\'Folders\' ">'
            buf += '<span data-dojo-type="dojox.mobile.ToolBarButton" data-dojo-props=\'label:"Refresh"\' style="float:right;" ></span>'
            buf += '</h1>'
            buf += '<ul data-dojo-type="dojox.mobile.RoundRectList">'
            for x in dat:
                tmp = x.decode()[:-1]
                index = tmp.rfind('"')
                output = tmp[index + 1:]
                # print(type(output)) # str
                output = output.encode()
                # print(type(output)) # bytes
                output = utf7imap.decoder(output)
                # print(type(output)) # tuple
                buf += '<li data-dojo-type="dojox.mobile.ListItem" '
                buf += 'data-dojo-props="moveTo:\'#\', onClick:actListMessages, '
                buf += 'label: \'' + output[0] + '\'"></li>'
            buf += '</ul>'
        except socket.gaierror as ex:
            return str(ex)
        except imaplib.IMAP4.error as ex:
            return str(ex)
        else:
            return buf

    @cherrypy.expose
    def logon(self, server, user, pwd):
        try:
            imap = imaplib.IMAP4(server)
            imap.login(user, pwd)
        except imaplib.IMAP4.error as ex:
            buf = ''
            for x in ex.args:
                buf += x.decode()
            return x
        except socket.error as ex:
            return str(ex)
        else:
            cherrypy.session['imap_server'] = server
            cherrypy.session['imap_user'] = user
            cherrypy.session['imap_pwd'] = pwd
            return 'OK'

current_dir = os.path.dirname(os.path.abspath(__file__))

conf1 = {
    'global': {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8080,
        'request.show_tracebacks': True,       ###
    },
    '/': {
        'tools.sessions.on': True,
    },
    '/jslib': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': '/usr/local/src/dojotoolkit',
    },
    '/s': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': os.path.join(current_dir, 'static')
    },
}

cherrypy.quickstart(Test1(), '/swmail', conf1)

