import logging
import os
from enum import StrEnum
from pathlib import Path
from urllib.parse import ParseResult, urlparse

from mitmproxy import http

logger = logging.getLogger(Path(__file__).with_suffix("").name)
PROXY_HOST = os.environ.get("PROXY_HOST")
PROXY_PORT = os.environ.get("PROXY_PORT")
PROXY_NETLOC: str | None = None
if PROXY_HOST and PROXY_PORT:
    PROXY_NETLOC = f"{PROXY_HOST}:{PROXY_PORT}"


class ReqHdr(StrEnum):
    referer = "Referer"


class RspHdr(StrEnum):
    alt_svc = "Alt-Svc"
    via = "via"


def remove_header(message: http.Message, key: str) -> str | None:
    value = message.headers.pop(key, None)
    if value:
        logger.debug(f"Removed header - '{key}: {value}'")
    return value


class Plugin:
    referer: ParseResult | None = None

    @property
    def request_netloc(self) -> str | None:
        if PROXY_NETLOC:
            return PROXY_NETLOC
        elif self.referer:
            return self.referer.netloc
        else:
            return None

    def request(self, flow: http.HTTPFlow):
        assert flow.request
        referer = remove_header(flow.request, ReqHdr.referer)
        if referer:
            self.referer = urlparse(referer)

    def response(self, flow: http.HTTPFlow):
        assert flow.response
        for key in RspHdr:
            remove_header(flow.response, key)

        if flow.response.text and flow.server_conn.address and self.request_netloc:
            logger.info(f"{flow.response.text[:1024] = }")
            host = flow.server_conn.address[0]
            netloc = f"{host}:{flow.server_conn.address[1]}"
            logger.info(f"{host = } {netloc = }")
            # if netloc in flow.response.text:
            #     logger.info(f"'{netloc}' found in response text")
            #     flow.response.text = flow.response.text.replace(netloc, self.request_netloc)
            if host in flow.response.text:
                logger.info(f"'{host}' found in response text")
                flow.response.text = flow.response.text.replace(
                    host, self.request_netloc
                )
            logger.info(f"{flow.response.text[:1024] = }")


addons = [Plugin()]
