"""
Vendored and refactored from Azure CLI

# MIT License
#
# Copyright (c) 2016 Microsoft Corporation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

https://github.com/Azure/azure-cli/blob/master/src/azure-cli-core/azure/cli/core/_profile.py
https://github.com/Azure/azure-cli/blob/master/src/azure-cli-core/azure/cli/core/util.py
"""

import http.server
import json
import logging
import os
import platform
import socket
import subprocess
import urllib
import webbrowser

import click

from stacklet.client.platform.context import StackletContext, StackletCredentialWriter


class ClientRedirectServer(http.server.HTTPServer):
    query_params = {}

    def __init__(self, auth_url, server_address, RequestHandlerClass, bind_and_activate=True):
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        self.log = logging.getLogger("ClientRedirectServer")
        self.completed = False

        self.auth_url = auth_url

        RequestHandlerClass.auth_url = self.auth_url

        # On Windows, HTTPServer by default doesn't throw error if the port is in-use
        # https://github.com/Azure/azure-cli/issues/10578
        if BrowserAuthenticator.is_windows():
            self.log.debug("Windows is detected. Set HTTPServer.allow_reuse_address to False")
            self.allow_reuse_address = False
        elif BrowserAuthenticator.is_wsl():
            self.log.debug("WSL is detected. Set HTTPServer.allow_reuse_address to False")
            self.allow_reuse_address = False


class ClientRedirectHandler(http.server.BaseHTTPRequestHandler):
    def get_request_body(self):
        token = self.rfile.read(int(self.headers["Content-length"]))
        res = token.decode("utf-8")
        return res

    def do_GET(self):
        self.route_stacklet_auth_shortlink()
        self.route_favicon()
        self.route_index()

    def do_POST(self):
        res = self.get_request_body()
        res = json.loads(res)
        StackletCredentialWriter(res["access_token"])()
        StackletCredentialWriter(res["id_token"], StackletContext.DEFAULT_ID)()
        self.send_response(200)
        self.server.completed = True

    def route_stacklet_auth_shortlink(self):
        """
        Provides a short link for users to copy and paste into the browser more easily

            http://localhost:43210/stacklet_auth

        """
        if self.path == "/stacklet_auth":
            # moved temporarily as to prevent the browser from caching the result page
            self.send_response(302)
            self.send_header("Location", self.auth_url)
            self.end_headers()
            return

    def route_favicon(self):
        # deal with legacy IE
        if self.path.endswith("/favicon.ico"):
            self.send_response(204)
            return

    def route_index(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        landing_file = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "auth_landing_pages",
            "ok.html",
        )
        try:
            with open(landing_file, "rb") as html_file:
                self.wfile.write(html_file.read())
        except BrokenPipeError:
            pass

    def log_message(self, format, *args):
        """
        Prevent http server from dumping messages to stdout
        """


class BrowserAuthenticator:
    """
    Handle browser authentication for CLI
    """

    # due to limitations with cognito and defining redirect targets in the cognito
    # client, we have to hard code a port for our own usage.
    CLI_REDIRECT_PORT = 43210

    REDIRECT_URI = f"http://localhost:{CLI_REDIRECT_PORT}"
    SHORT_LINK = f"http://localhost:{CLI_REDIRECT_PORT}/stacklet_auth"

    def __init__(self, authority_url, client_id, idp_id=""):
        self.authority_url = authority_url
        self.client_id = client_id
        self.idp_id = idp_id
        self.auth_url = self.build_url()
        self.log = logging.getLogger("StackletBrowserAuthenticator")

    def build_url(self):
        """
        Build the full auth url with the required query parameters
        """

        auth_url = f"{self.authority_url}/oauth2/authorize"
        parts = list(urllib.parse.urlparse(auth_url))
        # query params are found at index 4 of the parsed url
        parts[4] = urllib.parse.urlencode(
            {
                "response_type": "token",
                "redirect_uri": self.REDIRECT_URI,
                "client_id": self.client_id,
                "scope": "email+openid",
                "idp_identifier": self.idp_id,
            }
        )
        return urllib.parse.unquote(urllib.parse.urlunparse(parts))

    @staticmethod
    def _get_platform_info():
        uname = platform.uname()
        # python 2, `platform.uname()` returns:
        # tuple(system, node, release, version, machine, processor)
        platform_name = getattr(uname, "system", None) or uname[0]
        release = getattr(uname, "release", None) or uname[2]
        return platform_name.lower(), release.lower()

    @staticmethod
    def is_wsl():
        platform_name, release = BrowserAuthenticator._get_platform_info()
        # "Official" way of detecting WSL:
        # https://github.com/Microsoft/WSL/issues/423#issuecomment-221627364
        # Run `uname -a` to get 'release' without python
        #   - WSL 1: '4.4.0-19041-Microsoft'
        #   - WSL 2: '4.19.128-microsoft-standard'
        return platform_name == "linux" and "microsoft" in release

    @staticmethod
    def is_windows():
        platform_name, _ = BrowserAuthenticator._get_platform_info()
        return platform_name == "windows"

    @staticmethod
    def is_macos():
        platform_name, _ = BrowserAuthenticator._get_platform_info()
        return platform_name == "darwin"

    @staticmethod
    def open_page_in_browser(url):
        # windows 10 linux subsystem
        if BrowserAuthenticator.is_wsl():
            # https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_powershell_exe
            # Ampersand (&) should be quoted
            try:
                return subprocess.Popen(
                    ["powershell.exe", "-Command", 'Start-Process "{}"'.format(url)]
                )
            # WSL might be too old
            # FileNotFoundError introduced in Python 3
            except OSError:
                pass
        elif BrowserAuthenticator.is_macos():
            # handle 2 things:
            # a. On OSX sierra,
            #   'python -m webbrowser -t <url>' emits out "execution error: <url> doesn't
            #    understand the "open location" message"
            # b. Python 2.x can't sniff out the default browser
            return subprocess.Popen(["open", url])

        try:
            # 2 means: open in a new tab, if possible
            return webbrowser.open(url, new=2)
        except TypeError:
            # See https://bugs.python.org/msg322439
            return webbrowser.open(url, new=2)

    def __call__(self):
        try:
            self.log.debug(f"Full Auth URL: {self.auth_url}")
            web_server = ClientRedirectServer(
                auth_url=self.auth_url,
                server_address=("localhost", self.CLI_REDIRECT_PORT),
                RequestHandlerClass=ClientRedirectHandler,
            )
        except socket.error:
            raise Exception(
                f"Port '{self.CLI_REDIRECT_PORT}' is taken with error '%s'. "
                "Ensure that port {self.CLI_REDIRECT_PORT} is open"
            )
        except UnicodeDecodeError:
            self.log.warning(
                "Please make sure there is no international (Unicode) character in the computer "
                r"name or C:\Windows\System32\drivers\etc\hosts file's 127.0.0.1 entries."
            )

        self.log.info("Open browser with url: %s", self.SHORT_LINK)
        click.echo(
            "Opening page in browser, if the browser does not automatically open, "
            f"copy and paste this url into your browser:\n\n{self.SHORT_LINK}\n"
        )

        if self.open_page_in_browser(self.SHORT_LINK) is False:
            web_server.server_close()
            return

        # wait for callback from browser.
        while not web_server.completed:
            web_server.handle_request()

        click.echo("Login Succeeded")
