from PySimpleGUI import WIN_CLOSED
import itertools
from bdrf_connector import BDRFConnector
import PySimpleGUI as sg
import sys
import webbrowser

bdrf_connector = BDRFConnector()

if bdrf_connector.oauth2_url:
    login_layout = [
        [sg.Text("Login through this link")],
        [sg.Text(bdrf_connector.oauth2_url, enable_events=True)],
        [sg.Button("OK", key="OK")],
    ]
    login_window = sg.Window("Login", layout=login_layout)
    while True:
        event, values = login_window.read()
        if event == bdrf_connector.oauth2_url:
            webbrowser.open(bdrf_connector.oauth2_url)
        if event == "OK":
            login_window.close()
            break
        elif event is None:
            sys.exit(0)

saved_posts = bdrf_connector.get_saved_posts()
print(saved_posts, len(saved_posts))

layout = [
    [
        sg.Listbox(
            values=[f"{e.id} - {e.title}" for e in saved_posts],
            size=(60, 20),
            key="listbox",
        )
    ]
]

window = sg.Window(
    "Keyboard Test", layout, return_keyboard_events=True, use_default_focus=False
)

# ---===--- Loop taking in user input --- #
while True:
    event, values = window.read()
    if event == WIN_CLOSED:
        break


window.close()
