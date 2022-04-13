import tkinter as tk
import PySimpleGUI as sg
import webbrowser


class LoginWindow:
    def __init__(self, oauth2_url: str):
        self.oauth2_url: str = oauth2_url
        underline_font = tk.font.Font(family="Helvetica", size=12, underline=True)
        self.layout: list[list[sg.Element]] = [
            [sg.Text("Login through this link")],
            [sg.Text(self.oauth2_url, enable_events=True, font=underline_font)],
            [sg.Button("OK", key="OK")],
        ]

    def start(self):
        login_window = sg.Window("Login", layout=self.layout, keep_on_top=True)
        while True:
            event, values = login_window.read()
            if event == self.oauth2_url:
                webbrowser.open(self.oauth2_url)
            if event == "OK" or event is sg.WIN_CLOSED or event is None:
                login_window.close()
                break
