import threading
import tkinter
from reddit_preview_getter import update_preview
from bdrf_connector import BDRFConnector
from login_window import LoginWindow
import PySimpleGUI as sg
import webbrowser


class GUI:
    def __init__(self):
        self.textbox = None
        self.listbox = None
        self.bdrf_connector: BDRFConnector = BDRFConnector()
        self.post_titles: list[str] = []
        self.thread_list: list[threading.Thread] = []
        self.selected_post: int = 0

        self.saved_posts_layout = [
            [
                sg.Listbox(
                    values=[],
                    default_values=[],
                    size=(60, 20),
                    key="listbox",
                    select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                    enable_events=True,
                    horizontal_scroll=False,
                    bind_return_key=True,
                )
            ],
            [
                sg.InputText(enable_events=True, key="input", do_not_clear=False),
                sg.FolderBrowse(
                    button_text="Select download folder", target="input", key="browse"
                ),
            ],
            [
                sg.Checkbox("Clear after download", key="clear"),
                sg.Input(
                    key="_json_path_",
                    enable_events=True,
                    do_not_clear=True,
                    visible=False,
                ),
                sg.FileBrowse(
                    button_text="Select download abbreviations",
                    key="select-json",
                    file_types=(("JSON files", "*.json"),),
                    target="_json_path_",
                ),
            ],
        ]

        self.preview_layout = [
            [sg.Image(filename="", key="preview", size=(500, 500))],
            [
                sg.Button(
                    "Open in browser",
                    key="open_in_browser",
                ),
                sg.Checkbox("Unsave after download", key="unsave-after-download"),
                sg.Checkbox(
                    "Remove from list after download", key="remove-after-download"
                ),
            ],
        ]

        self.complete_layout = [
            [
                sg.Column(self.saved_posts_layout),
                sg.VSeparator(),
                sg.Column(self.preview_layout),
            ]
        ]
        # ---===--- Create the window --- #
        self.window = sg.Window(
            "reddit-saved-downloader", self.complete_layout, return_keyboard_events=True
        )

    def start(self):

        if self.bdrf_connector.oauth2_url:
            LoginWindow(self.bdrf_connector.oauth2_url).start()
        self.post_titles = [
            f"{post.id} - {post.title}"
            for post in self.bdrf_connector.get_saved_posts()
        ]

        self.window.finalize()
        self.window["listbox"].update(values=self.post_titles, set_to_index=0)

        self.listbox = self.window["listbox"].Widget
        self.textbox = self.window["input"].Widget
        self.textbox.bind("<Down>", self.on_press_down)
        self.textbox.bind("<Up>", self.on_press_up)
        self.listbox.bind("<Down>", self.on_press_down)
        self.listbox.bind("<Up>", self.on_press_up)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        self.textbox.bind("<Return>", self.on_enter)
        self.textbox.bind("<Tab>", self.on_enter)

        update_preview(
            self.bdrf_connector.get_saved_posts()[self.selected_post],
            self.window["preview"],
        )
        # ---===--- Loop taking in user input --- #
        while True:
            event, values = self.window.read()
            if event == "_json_path_":
                self.bdrf_connector.set_download_config(values["select-json"])
            if event == "open_in_browser":
                webbrowser.open(
                    self.bdrf_connector.get_saved_posts()[self.selected_post].url
                )
            if event == sg.WIN_CLOSED or event == "Exit" or event is None:
                break
        for thread in self.thread_list:
            thread.join()
        self.window.close()

    def on_press_down(self, event):
        if self.selected_post < self.listbox.size() - 1:
            self.listbox.select_clear(self.selected_post)
            self.selected_post += 1
            self.listbox.select_set(self.selected_post)
            if self.selected_post % 20 == 0:
                self.listbox.yview_scroll(20, tkinter.UNITS)
            update_preview(
                self.bdrf_connector.get_saved_posts()[self.selected_post],
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
                self.bdrf_connector.get_saved_posts()[self.selected_post],
                self.window["preview"],
            )

    def on_select(self, event):
        self.selected_post = event.widget.curselection()[0]
        update_preview(
            self.bdrf_connector.get_saved_posts()[self.selected_post],
            self.window["preview"],
        )

    def on_enter(self, event):
        if self.textbox.get() == "":
            return
        else:
            thread = self.bdrf_connector.download_post(
                self.bdrf_connector.get_saved_posts()[self.selected_post],
                self.textbox.get(),
            )
            self.thread_list.append(thread)
            if self.window["clear"].get():
                self.textbox.delete(0, tkinter.END)
            if self.window["unsave-after-download"].get():
                self.bdrf_connector.get_saved_posts()[self.selected_post].unsave()
            if self.window["remove-after-download"].get():
                self.bdrf_connector.get_saved_posts().pop(self.selected_post)
                self.listbox.delete(self.selected_post)
                if self.selected_post > self.listbox.size() - 1:
                    self.selected_post -= 1
                self.listbox.select_set(self.selected_post)


if __name__ == "__main__":
    GUI().start()
