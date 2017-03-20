"""
Tuxy bot
"""
import cherrypy


class TuxyBot(object):

    @cherrypy.expose
    def index(self):
        return "OK"

    @cherrypy.expose
    def retine(self, key, value):
        cherrypy.session[key] = value
        return repr(cherrypy.session.items())

    @cherrypy.expose
    def palindrom(self, value):
        data = ""
        for key, value in cherrypy.session.items():
            data += "{} -- {}".format(key, value)
            value.replace(key, value)
        return str(value == value[::-1])

    @cherrypy.expose
    def calculeaza(self, val1, operator, val2):
        for key, value in cherrypy.session.items():
            val1 = val1.replace(key, value)
            operator = operator.replace(key, value)
            val2 = val2.replace(key, value)

        try:
            if operator == "+":
                return str(int(val1) + int(val2))
            elif operator == "-":
                return str(int(val1) - int(val2))
            elif operator == "*":
                return str(int(val1) * int(val2))
            elif operator == "/":
                return str(int(val1) / int(val2))
        except ValueError:
            return "Respecta constrangerile pentru: {} {} {}".format(
                val1, operator, val2)
        except ZeroDivisionError:
            return "Div by zero"

    @cherrypy.expose
    def curata(self):
        cherrypy.session.clear()


def main():
    conf = {
        "/": {
            'tools.sessions.on': True,
        }
    }
    cherrypy.quickstart(TuxyBot(), "/", conf)


if __name__ == "__main__":
    main()
