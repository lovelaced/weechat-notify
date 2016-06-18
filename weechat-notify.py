#    Copyright 2013 Josh Kearney <josh@jk0.org>
#    edited by lovelaced
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import requests
import weechat
import json

SCRIPT_NAME = "weechat-notify"
SCRIPT_AUTHOR = "Josh Kearney (jk0), lovelaced"
SCRIPT_VERSION = "0.4"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC = "Send Pushbullet, Prowl, or NMA notifications upon new mentions or PMs when away."

OPTIONS = {
    "service": "",
    "api_key": "",
    "force_send": "off"
}


def send_notification(event, channel, prefix, message):
    service = weechat.config_get_plugin("service")
    api_key = weechat.config_get_plugin("api_key")
    params = {}
    data = {}
    if service == "nma":
        endpoint = "https://www.notifymyandroid.com/publicapi/notify?"
        if channel:
            description = "[" + channel + "] " + prefix + ": " + message
        else:
            description = prefix + ": " + message
        params = {
            "apikey": api_key,
            "application": "WeeChat",
            "event": event,
            "description": description
    }
    elif service == "prowl":
        endpoint = "https://api.prowlapp.com/publicapi/add?"
        params = {
            "apikey": api_key,
            "application": "WeeChat",
            "event": event,
            "description": description
    }
    elif service == "pushbullet":
        endpoint = "https://api.pushbullet.com/v2/pushes"

        if channel:
            title = channel
            message = prefix + ": " + message
        else:
            title = prefix

        headers = {
            "Content-type": "application/json",
        }
        params = {
            "Access-Token": api_key,
        }
        data = {
            "body": message,
            "title:": title,
            "type": "note",
            "guid": message
        }
        print headers, data, params
    else:
        return weechat.WEECHAT_RC_OK

    if not api_key:
        return weechat.WEECHAT_RC_OK

    if service == "pushbullet":
        requests.post(endpoint, params=params, data=json.dumps(data), headers=headers)

    requests.post(endpoint, params=params)


def signal_cb(data, buffer, date, tags, displayed, highlight, prefix, message):
    is_away = weechat.buffer_get_string(buffer, "localvar_away")
    is_private = weechat.buffer_get_string(buffer, "localvar_type") == "private"
    force_send = weechat.config_get_plugin("force_send") == "on"

    if is_away:
        pass
    elif force_send:
        pass
    else:
        return weechat.WEECHAT_RC_OK

    network = weechat.buffer_get_string(buffer, "localvar_server")
    channel = weechat.buffer_get_string(buffer, "localvar_channel")

    if str(highlight) == "1":
        send_notification(network, "[%s:%s] %s" % (channel, prefix, message))
    elif is_private:
        send_notification(network, "[%s] %s" % (prefix, message))

    return weechat.WEECHAT_RC_OK


if __name__ == "__main__":
    weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
                     SCRIPT_LICENSE, SCRIPT_DESC, "", "")

    for option, default_value in OPTIONS.items():
        if not weechat.config_get_plugin(option):
            if default_value:
                weechat.config_set_plugin(option, default_value)
            else:
                error = weechat.prefix("error")
                weechat.prnt("", "%s%s: /set plugins.var.python.%s.%s" % (
                    error,
                    SCRIPT_NAME,
                    SCRIPT_NAME,
                    option))

    weechat.hook_print("", "notify_message", "", 1, "signal_cb", "")
    weechat.hook_print("", "notify_private", "", 1, "signal_cb", "")
