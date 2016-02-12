#!/usr/bin/env python
# *-* coding: UTF-8 *-*

"""
Tuxy își dorește un sistem care să automatizeze instalării unui proiect
pe infrastructura din `TuxyLand`.

Acest proiect de automatizare va primi un fișier de configurare ce va
conține toate instrucțiunile necesare pentru pregătirea mediului ideal
în care va rula `TuxyApp`.

Un exemplu de fișier de configurare ar putea fi:



{
    "before_install": [
        {
            "download": {
                "source": "https://localhost/file",
                "destination": "/home/alex/script.sh",
            }
        },
    ],
    "install": [
        {
            "run_script": {
                # How many times to retry running the command.
                "attempts": 3,
                # Single bool, int, or list of allowed exit codes.
                "check_exit_code": True,
                # The command passed to the command runner.
                "command": "bash /home/alex/script.sh",
                # Set the current working directory
                "cwd": "/home/alex/",
                # Environment variables and their values that
                # will be set for the process.
                "env_variables": {"tuxy": "Tuxy Pinguinescu"},
                # Interval between execute attempts, in seconds.
                "retry_interval": 3,
                # Whether or not there should be a shell used to
                # execute this command.
                "shell": True,
            },
            # ...
        }
    ],
    "after_install": [
        {
            "reboot": {
                "method": "soft",
            }
        }
    ],

    "install_failed": [
        {
            "delete": {
                "method": "force",
                "path": "/home/alex"
            },
        },
        {
            "shutdown": {
                "method": "hard",
            },
        },
    ],
    "config": {
        "hostname": "TuxyNode-1",
        "users": {
            "acoman": {
                "full_name": "Alexandru Coman",
                "primary-group": "admin",
                "groups": ["users"],
                "expiredate": "2016-09-01",
                "password": ""
            },
            # ...
        },
        "write_files": {
            0: {
                "path": "/home/alex/test",
                "permissions": "0555",
                "encoding": "gzip",
                "content": "",
            },
            # ...
        },
    }
}

Trebuie să dezvoltați o aplicație care să primească un fișier de
configurare și să rezolve toate sarcinile precizate în acesta.

La sfârșit va trebui să ofere un fișier build.log care să descrie
toate lucrurile care s-au întâmplat.
"""
from __future__ import print_function
import json
# import os
import argparse
import urllib2


def write_log(message_type, message):
    """ scriem mesajul in fisierul cu log-uri.
    prefixul este dat de tipul de mesaj dorit """

    if message_type == 'e':
        message = "EROARE :" + message
    elif message_type == 'o':
        message = "OK :" + message
    elif message_type == 'w':
        message = "WARNING :" + message
    elif message_type == 'f':
        message = "FINISH :" + message
    elif message_type == 'h':
        message = "HINT :" + message
    elif message_type == 'd':
        message = "DUMP INFO:" + str(message)

    message = message + ' \n'
    with open('build.log', "a") as file_data:
        file_data.write(message)


def parse_file(path):
    """ parsam fisierul de configurare. """

    try:
        with open(path) as data_file:
            data = json.load(data_file)
            write_log('o', "Am citit informatiile de configurare din " + path)
    except ValueError:
        write_log('e', "Informatiile din fisier nu sunt valide (" + path + ")")
        data = {'NU_EXISTA': True}

    except IOError:
        write_log('e', "Nu am gasit fisierul (" + path + ")")
        data = {'NU_EXISTA': True}
    return data


def parser_cli_arguments():
    """ parseaza argumentele primite la rularea programului """
    args = argparse.ArgumentParser()
    args.add_argument("-c", "--config_file",
                      help="Path to config file")
    args = args.parse_args()
    return args


def function_download(name, valori):
    """ downloadam de la o sursa la o destinatie """
    it_workerd = True
    source = valori.get('source', None)
    destination = valori.get('destination', None)
    if not source and not destination:
        it_workerd = False
        write_log('e', "Nu putem efectua " + name)
        write_log('d', valori)

    try:
        response = urllib2.urlopen(source)
        data = response.read()
        response.close()
        try:
            file_data = open(destination, 'w')
            file_data.write(data)
        except IOError as error:
            write_log('e', 'Nu am putut scrie la locatia ' + destination)
            write_log('d', error)
            it_workerd = False
    except IOError as error:
        write_log('e', 'Nu am putut descarca de la ' + source)
        write_log('d', error)
        it_workerd = False

    write_log('o', "Am descarcat de la <" + source + "> si am ")
    write_log('o', "salvat in <" + destination + ">")
    return it_workerd



def apel_functie(functie_name, valori):
    """ apelam parsam valorile pentru functie si apelam functia """
    it_workerd = True

    if functie_name == 'download':
        it_workerd = function_download(functie_name, valori)
    elif functie_name == 'run_script':
        it_workerd = function_run_script(functie_name, valori)

    return it_workerd


def do_set_of_instructions(faza, instructiuni):
    """ primeste o faza si face setul de instructiuni din acea faza"""
    write_log("h", "Rulam faza " + faza)
    it_workerd = True

    # deoarece after_install, install, si after_install sunt liste cu un
    # element
    if isinstance(instructiuni, list) and len(instructiuni) > 0:
        instructiuni = instructiuni[0]

    for key in instructiuni:
        value = instructiuni[key]
        it_workerd = apel_functie(key, value)

        if not it_workerd:
            write_log("e", "Nu am putut efectua instructiunea " + key)
            write_log("d", value)
            break

    return it_workerd


def main():
    """ main function """
    args = parser_cli_arguments()
    data = parse_file(args.config_file)

    f = open('build.log', 'w')
    f.write('')
    f.close()

    it_workerd = True
    if not data:
        write_log('w', "Am terminat programul!")
        it_workerd = False

    if 'config' in data.keys() and it_workerd:
        it_workerd = do_set_of_instructions('config', data['config'])

    if 'before_install' in data.keys() and it_workerd:
        it_workerd = do_set_of_instructions('before_install',
                                            data['before_install'])

    if 'install' in data.keys() and it_workerd:
        it_workerd = do_set_of_instructions('install',
                                            data['install'])

    if 'after_install' in data.keys() and it_workerd:
        it_workerd = do_set_of_instructions('after_install',
                                            data['after_install'])

    if 'install_failed' in data.keys() and not it_workerd:
        do_set_of_instructions("install_failed", data['install_failed'])


if __name__ == "__main__":
    main()
