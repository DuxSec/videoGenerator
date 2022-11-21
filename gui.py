import customtkinter as ctk
import json
import os


class App(ctk.CTk):
    config_data = None

    def __init__(self):
        super().__init__()
        self.title("Video Generator")
        self.geometry(f"{768}x{576}")
        self.minsize(400, 400)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.configure(fg_color="#1c1917")

        with open('config.json', 'r') as file:
            self.config_data = json.load(file)
        os.system('cls' if os.name == 'nt' else 'clear')

        pexels_api_key = self.config_data['pexelsAPIKey']
        api_key_set = (pexels_api_key != ""
                       and pexels_api_key != "Not set"
                       and pexels_api_key != "None")
        if not api_key_set:
            self.setApiKey(text="You've not set your Pexels API Key yet.")

        self.frame_left = ctk.CTkFrame(master=self,
                                       width=180,
                                       fg_color="#292524",
                                       corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nswe")
        self.frame_left.grid_rowconfigure(1, minsize=10)
        self.frame_left.grid_rowconfigure(3, minsize=10)

        current_config_label = ctk.CTkLabel(self.frame_left,
                                            text="Current Config",
                                            text_font=("Helvetica", 14, "bold"),
                                            width=20,
                                            height=1,
                                            anchor=ctk.W,
                                            corner_radius=0)
        current_config_label.grid(row=0, column=0, sticky=ctk.W, padx=5, pady=5)

        change_apikey_button = ctk.CTkButton(self.frame_left,
                                             text="Change API Key",
                                             text_font=("Helvetica", 10),
                                             fg_color="#047857",
                                             hover_color="#059669",
                                             command=lambda: self.setApiKey(text="Change your Pexels API Key."))
        change_apikey_button.grid(row=2, column=0, padx=5)

        amount_of_videos_label = ctk.CTkLabel(self.frame_left,
                                              text="Amount of videos",
                                              text_font=("Helvetica", 10),
                                              anchor=ctk.W,)
        amount_of_videos_label.grid(row=5, column=0, padx=(5))

        amount_of_videos_entry = ctk.CTkEntry(self.frame_left,
                                              text_font=("Helvetica", 10))
        amount_of_videos_entry.grid(row=6, column=0, padx=(5))
        amount_of_videos_entry.insert(
            0, f"{self.config_data['amountOfVideosToMake']}")

    def setApiKey(self, text):
        window = ctk.CTkToplevel(self)
        window.title("Pexels API Key")
        window.geometry(f"{300}x{100}")
        window.minsize(300, 100)
        window.configure(fg_color="#1c1917")

        label = ctk.CTkLabel(window,
                             text=text,
                             justify="left",
                             anchor=ctk.W,
                             text_font=("Helvetica", 10, "bold"),
                             )
        label.grid(row=0, column=0, sticky=ctk.W, padx=(5))

        api_key_entry = ctk.CTkEntry(window,
                                     textvariable=ctk.StringVar(),
                                     width=290,
                                     placeholder_text="Pexels API Key"
                                     )
        api_key_entry.insert(0, self.config_data['pexelsAPIKey'])
        api_key_entry.grid(row=1, column=0, padx=(5))

        save_button = ctk.CTkButton(window,
                                    text="Save",
                                    fg_color="#15803d",
                                    hover_color="#16a34a",
                                    text_font=("Helvetica", 10, "bold"),
                                    text_color="white",
                                    width=10,
                                    command=lambda: self.saveApiKey(
                                        api_key_entry.get(), window)
                                    )
        save_button.grid(row=2, column=0, sticky=ctk.W, padx=5)

        quit_button = ctk.CTkButton(window,
                                    text="Quit",
                                    fg_color="#991b1b",
                                    hover_color="#b91c1c",
                                    text_font=("Helvetica", 10, "bold"),
                                    text_color="white",
                                    width=12,
                                    command=lambda: self.quit()
                                    )
        quit_button.grid(row=2, column=0, sticky=ctk.E, padx=5, pady=5)

    def saveApiKey(self, api_key, window):
        self.config_data['pexelsAPIKey'] = api_key
        with open('config.json', 'w') as file:
            json.dump(self.config_data, file, indent=4)
        window.destroy()

    def quit(self):
        super().quit()


if __name__ == "__main__":
    gui = App()
    gui.mainloop()
