from PySimpleGUI import WIN_CLOSED
from reddit_preview_getter import update_preview
from bdrf_connector import BDRFConnector
import PySimpleGUI as sg
import sys
import webbrowser


class GUI:
    def __init__(self):
        self.textbox = None
        self.listbox = None
        self.bdrf_connector = BDRFConnector()

        if self.bdrf_connector.oauth2_url:
            login_layout = [
                [sg.Text("Login through this link")],
                [sg.Text(self.bdrf_connector.oauth2_url, enable_events=True)],
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

        self.posts = self.bdrf_connector.get_saved_posts()
        self.post_titles = {post: f"{post.id} - {post.title}" for post in self.posts}
        self.selected_post = 0

        self.saved_posts_layout = [
            [
                sg.Listbox(
                    values=list(self.post_titles.values()),
                    default_values=[self.post_titles[self.posts[self.selected_post]]],
                    size=(60, 20),
                    key="listbox",
                    select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                    enable_events=True,
                    horizontal_scroll=False,
                    bind_return_key=True,
                )
            ],
            [sg.InputText(enable_events=True, key="input")],
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
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        update_preview(self.posts[self.selected_post], self.window["preview"])
        # ---===--- Loop taking in user input --- #
        while True:
            event, values = self.window.read()
            print(event, values)
            if event == "Down:40":
                update_preview(self.posts[self.selected_post], self.window["preview"])
                continue
            if event == "Up:38":
                update_preview(self.posts[self.selected_post], self.window["preview"])
                continue
            if event == WIN_CLOSED:
                break
        self.window.close()

    def on_press_down(self, event):
        if self.selected_post < self.listbox.size() - 1:
            self.listbox.select_clear(self.selected_post)
            self.selected_post += 1
            self.listbox.select_set(self.selected_post)

    def on_press_up(self, event):
        if self.selected_post > 0:
            self.listbox.select_clear(self.selected_post)
            self.selected_post -= 1
            self.listbox.select_set(self.selected_post)

    def on_select(self, event):
        self.selected_post = event.widget.curselection()[0]
        update_preview(self.posts[self.selected_post], self.window["preview"])


if __name__ == "__main__":
    GUI().start()
