"""
Vendored and modified from Azure CLI

https://github.com/Azure/azure-cli/blob/master/src/azure-cli-core/azure/cli/core/_profile.py
https://github.com/Azure/azure-cli/blob/master/src/azure-cli-core/azure/cli/core/util.py
"""


import logging
import os
import platform

from stacklet_cli.context import StackletContext

logger = logging.getLogger()


def _get_platform_info():
    uname = platform.uname()
    # python 2, `platform.uname()` returns:
    # tuple(system, node, release, version, machine, processor)
    platform_name = getattr(uname, "system", None) or uname[0]
    release = getattr(uname, "release", None) or uname[2]
    return platform_name.lower(), release.lower()


def is_wsl():
    platform_name, release = _get_platform_info()
    # "Official" way of detecting WSL:
    # https://github.com/Microsoft/WSL/issues/423#issuecomment-221627364
    # Run `uname -a` to get 'release' without python
    #   - WSL 1: '4.4.0-19041-Microsoft'
    #   - WSL 2: '4.19.128-microsoft-standard'
    return platform_name == "linux" and "microsoft" in release


def is_windows():
    platform_name, _ = _get_platform_info()
    return platform_name == "windows"


def open_page_in_browser(url):
    import subprocess
    import webbrowser

    platform_name, _ = _get_platform_info()

    if is_wsl():  # windows 10 linux subsystem
        try:
            # https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_powershell_exe
            # Ampersand (&) should be quoted
            return subprocess.Popen(
                ["powershell.exe", "-Command", 'Start-Process "{}"'.format(url)]
            )
        except OSError:  # WSL might be too old  # FileNotFoundError introduced in Python 3
            pass
    elif platform_name == "darwin":
        # handle 2 things:
        # a. On OSX sierra,
        #   'python -m webbrowser -t <url>' emits out "execution error: <url> doesn't
        #    understand the "open location" message"
        # b. Python 2.x can't sniff out the default browser
        return subprocess.Popen(["open", url])
    try:
        return webbrowser.open(url, new=2)  # 2 means: open in a new tab, if possible
    except TypeError:  # See https://bugs.python.org/msg322439
        return webbrowser.open(url, new=2)


def _get_authorization_code_worker(authority_url, client_id, idp_id):
    # pylint: disable=too-many-statements
    import http.server
    import socket

    class ClientRedirectServer(
        http.server.HTTPServer
    ):  # pylint: disable=too-few-public-methods
        query_params = {}
        completed = False

    class ClientRedirectHandler(http.server.BaseHTTPRequestHandler):
        # pylint: disable=line-too-long

        def do_GET(self):
            try:
                from urllib.parse import parse_qs
            except ImportError:
                from urlparse import parse_qs  # pylint: disable=import-error

            if self.path.endswith("/favicon.ico"):  # deal with legacy IE
                self.send_response(204)
                return

            query = self.path.split("?", 1)[-1]
            query = parse_qs(query, keep_blank_values=True)
            self.server.query_params = query
            self.server.url = self.path

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            landing_file = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "auth_landing_pages",
                "ok.html",
            )
            with open(landing_file, "rb") as html_file:
                self.wfile.write(html_file.read())

        def do_POST(self):
            token = self.rfile.read(int(self.headers["Content-length"]))
            res = token.decode("utf-8")
            with open(
                os.path.expanduser(StackletContext.DEFAULT_CREDENTIALS), "w+"
            ) as f:  # noqa
                f.write(res)
            ClientRedirectServer.completed = True

        def log_message(
            self, format, *args
        ):  # pylint: disable=redefined-builtin,unused-argument,no-self-use
            pass  # this prevent http server from dumping messages to stdout

    reply_url = None

    # On Windows, HTTPServer by default doesn't throw error if the port is in-use
    # https://github.com/Azure/azure-cli/issues/10578
    if is_windows():
        logger.debug("Windows is detected. Set HTTPServer.allow_reuse_address to False")
        ClientRedirectServer.allow_reuse_address = False
    elif is_wsl():
        logger.debug("WSL is detected. Set HTTPServer.allow_reuse_address to False")
        ClientRedirectServer.allow_reuse_address = False

    port = 3000
    try:
        web_server = ClientRedirectServer(("localhost", port), ClientRedirectHandler)
        reply_url = "http://localhost:{}".format(port)
    except socket.error as ex:
        logger.warning(
            "Port '%s' is taken with error '%s'. Trying with the next one", port, ex
        )
    except UnicodeDecodeError:
        logger.warning(
            "Please make sure there is no international (Unicode) character in the computer "
            r"name or C:\Windows\System32\drivers\etc\hosts file's 127.0.0.1 entries. "
            "For more details, please see https://github.com/Azure/azure-cli/issues/12957"
        )

    if reply_url is None:
        logger.warning("Error: can't reserve a port for authentication reply url")
        return

    # launch browser:
    url = "{0}/oauth2/authorize?response_type=token&client_id={1}&redirect_uri={2}&scope=email+openid&idp_identifier={3}"  # noqa
    url = url.format(authority_url, client_id, reply_url, idp_id)

    logger.info("Open browser with url: %s", url)
    succ = open_page_in_browser(url)
    if succ is False:
        web_server.server_close()
        return

    # Emit a warning to inform that a browser is opened.
    # Only show the path part of the URL and hide the query string.
    logger.warning(
        "The default web browser has been opened at %s. Please continue the login in the web "
        "browser. Please login through the web browser. Your token will be automatically saved."
        % url.split("?")[0],
    )

    # wait for callback from browser.
    while True:
        web_server.handle_request()
        if web_server.completed:
            logger.warning("Login successful.")
            logger.warning(
                "Credentials written to %s" % StackletContext.DEFAULT_CREDENTIALS
            )
            break
