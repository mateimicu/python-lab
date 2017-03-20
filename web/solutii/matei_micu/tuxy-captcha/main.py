"""
Tuxy captcha
"""
import cherrypy


def get_data(filename):
    with open(filename, 'r') as f:
        return f.read()


class TuxyCaptcha(object):
    exposed = True

    def GET(self):
        return get_data("index.html").format("")

    def POST(self, first, second, rez):
        try:
            # x + y = z
            # (z - y)/x
            x = float(first)
            y = float(second)
            z = float(rez)
            return get_data("index.html").format((z-y)/x)
        except ValueError:
            return get_data("index.html").format("Parametri prosti")


def main():
    conf = {
        "/": {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        }
    }
    cherrypy.quickstart(TuxyCaptcha(), "/", conf)


if __name__ == "__main__":
    main()
