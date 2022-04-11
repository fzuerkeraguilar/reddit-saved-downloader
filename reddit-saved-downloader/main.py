import tkinter
from reddit_preview_getter import update_preview
from bdrf_connector import BDRFConnector
import PySimpleGUI as sg
import sys
import webbrowser


class GUI:
    def __init__(self):
        self.download_conf_path: str = ""
        self.select_download_conf_layout = [
            [sg.Text("Select download configuration:")],
            [
                sg.FileBrowse(
                    button_text="Select file", file_types=(("JSON files", "*.json"),)
                )
            ],
            [sg.OK(), sg.Cancel()],
        ]
        self.select_download_conf_window = sg.Window(
            "Select download configuration", self.select_download_conf_layout
        )
        self.select_download_conf_window.finalize()
        while True:
            event, values = self.select_download_conf_window.read()
            if event == "OK":
                self.download_conf_path = values["Select file"]
                break
            elif event == "Cancel" or event == sg.WIN_CLOSED or event is None:
                sys.exit(0)
        self.select_download_conf_window.close()

        self.textbox = None
        self.listbox = None
        try:
            self.bdrf_connector = BDRFConnector(self.download_conf_path)
        except:
            sg.popup_error("Error when connecting to BDRF.")
            sys.exit(0)

        if self.bdrf_connector.oauth2_url:
            login_layout = [
                [sg.Text("Login through this link")],
                [
                    sg.Text(
                        self.bdrf_connector.oauth2_url,
                        enable_events=True,
                        font="Courier underline",
                    )
                ],
                [sg.Button("OK", key="OK")],
            ]
            login_window = sg.Window("Login", layout=login_layout)
            while True:
                event, values = login_window.read()
                if event == self.bdrf_connector.oauth2_url:
                    webbrowser.open(self.bdrf_connector.oauth2_url)
                if event == "OK":
                    login_window.close()
                    break
                elif event is None:
                    sys.exit(0)
        self.post_titles = {
            post: f"{post.id} - {post.title}"
            for post in self.bdrf_connector.saved_posts
        }
        self.selected_post = 0

        self.saved_posts_layout = [
            [
                sg.Listbox(
                    values=list(self.post_titles.values()),
                    default_values=[
                        self.post_titles[
                            self.bdrf_connector.saved_posts[self.selected_post]
                        ]
                    ],
                    size=(60, 20),
                    key="listbox",
                    select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                    enable_events=True,
                    horizontal_scroll=False,
                    bind_return_key=True,
                )
            ],
            [
                sg.InputText(enable_events=True, key="input"),
                sg.FolderBrowse(target="input", key="browse"),
            ],
        ]

        self.preview_layout = [
            [sg.Image(filename="", key="preview", size=(500, 500))],
        ]

        self.complete_layout = [
            [
                sg.Column(self.saved_posts_layout),
                sg.VSeparator(),
                sg.Column(self.preview_layout),
            ]
        ]

        self.window = sg.Window(
            "reddit-saved-downloader",
            self.complete_layout,
            return_keyboard_events=True,
            keep_on_top=True,
            finalize=True,
        )

    def start(self):
        self.listbox = self.window["listbox"].Widget
        self.textbox = self.window["input"].Widget
        self.textbox.bind("<Down>", self.on_press_down)
        self.textbox.bind("<Up>", self.on_press_up)
        self.listbox.bind("<Down>", self.on_press_down)
        self.listbox.bind("<Up>", self.on_press_up)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        self.textbox.bind("<Return>", self.on_enter)
        update_preview(
            self.bdrf_connector.saved_posts[self.selected_post], self.window["preview"]
        )
        # ---===--- Loop taking in user input --- #
        while True:
            event, values = self.window.read()
            if event == sg.WIN_CLOSED or event == "Exit" or event is None:
                break
        self.window.close()

    def on_press_down(self, event):
        if self.selected_post < self.listbox.size() - 1:
            self.listbox.select_clear(self.selected_post)
            self.selected_post += 1
            self.listbox.select_set(self.selected_post)
            if self.selected_post % 20 == 0:
                self.listbox.yview_scroll(20, tkinter.UNITS)
            update_preview(
                self.bdrf_connector.saved_posts[self.selected_post],
                self.window["preview"],
            )

    def on_press_up(self, event):
        if self.selected_post > 0:
            self.listbox.select_clear(self.selected_post)
            self.selected_post -= 1
            self.listbox.select_set(self.selected_post)
            if self.selected_post % 20 == 19:
                self.listbox.yview_scroll(-20, tkinter.UNITS)
            update_preview(
                self.bdrf_connector.saved_posts[self.selected_post],
                self.window["preview"],
            )

    def on_select(self, event):
        self.selected_post = event.widget.curselection()[0]
        update_preview(
            self.bdrf_connector.saved_posts[self.selected_post], self.window["preview"]
        )

    def on_enter(self, event):
        if self.textbox.get() == "":
            return
        else:
            self.bdrf_connector.download_post(
                self.bdrf_connector.saved_posts[self.selected_post], self.textbox.get()
            )
        self.textbox.delete(0, "end")


if __name__ == "__main__":
    GUI().start()
