from tkinter import *
from PIL import Image, ImageTk
import os
import random as rand
import math
import json

# Made by: Jakob Vanky & Momo Sundbäck Brohult
# Date: 2023-10-30
# Course: Introduction to Information Technology

class GoB:
    '''The main class of GoB'''
    GAME_DIR = "D:\\Program\\Plugg\\0 VSCode scripts\\Python\\Introduktion till informationsteknologi\\M6\\Gob-Game-of-Bird"

    def __init__(self):
        os.chdir(self.GAME_DIR)
        bird_list = self.load_birds_from_file()
        (user_list, latest_user, is_save_file_created) = self.load_users_from_file()
        settings = Settings()
        self.main_window = Main_window(user_list, latest_user, bird_list, settings)

        if is_save_file_created:
            self.main_window.draw_register_first_user()
        else:
            self.main_window.draw_main_menu()

        self.main_window.mainloop()
        self.save_users_to_file(self.main_window.user_list)
        settings.save_settings()
    
    def load_users_from_file(self):
        '''Loads users from save file if a save file exists, otherwise creates a save file. Returns relevant data to the main class'''
        SAVE_FILE_PATH = str(os.getcwd())+"\\save_data\\"+"savefile.txt"
        user_list = []
        latest_user = ""
        is_save_file_created = False
        
        if not os.path.isfile(SAVE_FILE_PATH):
            open(SAVE_FILE_PATH, "x").close() # Creates a save file
            is_save_file_created = True
        else:
            with open(SAVE_FILE_PATH, "r") as f:
                text_lines = f.readlines()
                for user_line in range(0, len(text_lines)-1, 4):
                    loaded_user = User(text_lines[user_line].strip(), json.loads(text_lines[user_line+1]), json.loads(text_lines[user_line+2]))
                    user_list.append(loaded_user)
                latest_user = text_lines[-1].strip()
        return user_list, latest_user, is_save_file_created

    def load_birds_from_file(self):
        """instantiates the bird objects from the data and returns them in a list"""
        bird_list = []
        with open("birds.csv", "r") as f:
            image_paths = []
            for i, bird_line in enumerate(f):
                split_line_list = bird_line.split(",")
                image_paths.append(split_line_list[1])
                if (i+1) % 5 == 0:
                    bird = BoG(split_line_list[2], split_line_list[4].strip(), image_paths)
                    bird_list.append(bird)
                    image_paths = []
        return bird_list
    
    def save_users_to_file(self, user_list):
        """Saves all users present in the current session to the save file"""
        SAVE_FILE_PATH = str(os.getcwd())+"\\save_data\\"+"savefile.txt"
        with open (SAVE_FILE_PATH, "w") as f:
            for user in user_list:
                f.write(user.name + "\n")
                f.write(json.dumps(user.high_score) + "\n")
                f.write(json.dumps(user.skill_level) + "\n")
                f.write("\n")
            f.write(self.main_window.current_user.name)
        return
        
class Main_window(Tk):
    """GoB window class. An underclass of Tkinter that creates the game window and main menu elements"""
    BACKGROUND_IMAGE = "Background.jpg"
    BACKGROUND_IMAGE_GAME_OVER = "Nogame.jpg"
    USER_IMAGE = "User.png"
    SETTINGS_IMAGE = "Settings.jpg"
    GAME_FONT = "Courier New"
    LABEL_COLOR = "#7497e3"
    WINDOW_MIN_WIDTH = 711
    WINDOW_MIN_HEIGHT = 400

    def __init__(self, user_list, latest_user, bird_list, settings):
        super().__init__()
        self.user_list = user_list
        for user in user_list:
            if user.name == latest_user:
                self.current_user = user
        self.bird_list = bird_list
        self.settings = settings
      
        self.title("Game of Bird, the best game ever created")
        self.minsize(self.WINDOW_MIN_WIDTH, self.WINDOW_MIN_HEIGHT)
        self.background_image = Image.open(self.BACKGROUND_IMAGE)
        self.background_image_tkinter = ImageTk.PhotoImage(self.background_image)
        self.background_canvas = Canvas(self)
        self.background_canvas.pack(fill="both", expand=True)
        self.background_canvas.create_image(0, 0, anchor=NW, image=self.background_image_tkinter)

        self.wait_var = IntVar()
        self.bind("<Configure>", self.resize_image)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def resize_image(self, event):
        """Resizes the window elements. Is called when the window is resized"""
        resized_background_image = self.background_image.resize((self.winfo_width(), self.winfo_height()))
        self.background_image_tkinter = ImageTk.PhotoImage(resized_background_image)
        self.background_canvas.create_image(0, 0, anchor=NW, image=self.background_image_tkinter)
        
    def draw_main_menu(self):
        for child in self.background_canvas.winfo_children():
            child.destroy()

        self.resizable(True, True)
        self.create_game_mode_buttons()
        self.create_settings_and_user_buttons()
        return
    
    def create_game_mode_buttons(self):
        text_to_image_button = Button(self.background_canvas, text="Text to image", borderwidth=5, font=(self.GAME_FONT, 20, "bold"), width=14, command=lambda: Mode_text_to_image(self, self.background_canvas, self.bird_list, self.current_user, self.settings, self.wait_var))
        image_to_text_button = Button(self.background_canvas, text="Image to text", borderwidth=5, font=(self.GAME_FONT, 20, "bold"), width=14, command=lambda: Mode_image_to_text(self, self.background_canvas, self.bird_list, self.current_user, self.settings, self.wait_var))
        memory_button = Button(self.background_canvas, text="Memory (2p)", borderwidth=5, font=(self.GAME_FONT, 20, "bold"), width=14, command=lambda: Mode_memory(self, self.background_canvas, self.bird_list, self.current_user, self.settings, self.wait_var, self.user_list))

        text_to_image_button.place(relx=0.5, rely=0.5, y=-80, anchor=CENTER)
        image_to_text_button.place(relx=0.5, rely=0.5, anchor=CENTER)
        memory_button.place(relx=0.5, rely=0.5, y=80, anchor=CENTER)
        return
    
    def create_settings_and_user_buttons(self):
        user_image = Image.open(self.USER_IMAGE)
        user_image = user_image.resize((40, 27))
        self.user_image_tkinter = ImageTk.PhotoImage(user_image)
        user_button = Button(self.background_canvas, image=self.user_image_tkinter, borderwidth=5, command=lambda: self.draw_select_user())

        settings_image = Image.open(self.SETTINGS_IMAGE)
        settings_image = settings_image.resize((40, 27))
        self.settings_image_tkinter = ImageTk.PhotoImage(settings_image)
        settings_button = Button(self.background_canvas, image=self.settings_image_tkinter, borderwidth=5, command=lambda: self.settings.draw_settings(self))

        user_button.place(relx=1, x=-90, y=20, anchor="ne")
        settings_button.place(relx=1, x=-20, y=20, anchor="ne")
        return
    
    def draw_select_user(self):
        for child in self.background_canvas.winfo_children():
            child.destroy()

        select_user_frame = Frame(self.background_canvas)
        select_user_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.user_listbox = Listbox(select_user_frame, width=20, height=5, font=(self.GAME_FONT, 14, "bold"))
        self.user_listbox.pack(side=LEFT)

        for user in self.user_list:
            self.user_listbox.insert(END, user.name)

        if len(self.user_list) > 5:
            user_scrollbar = Scrollbar(select_user_frame)
            user_scrollbar.pack(side=RIGHT, fill="y")
            self.user_listbox.config(yscrollcommand = user_scrollbar.set)
            user_scrollbar.config(command = self.user_listbox.yview)

        self.create_select_user_widgets()
        return
        
    def create_select_user_widgets(self):
        current_user_label = Label(self.background_canvas, text=f"Current user: {self.current_user.name}", font=(self.GAME_FONT, 14, "bold"), background=self.LABEL_COLOR, relief="ridge")
        current_user_label.place(relx=0.5, rely=0, y=50, anchor=N)
        select_user_label = Label(self.background_canvas, text=f"Select user:", font=(self.GAME_FONT, 14, "bold"), background=self.LABEL_COLOR, relief="ridge")
        select_user_label.place(relx=0.5, rely=0.5, y=-70, anchor=S)
        load_user_button = Button(self.background_canvas, text="Load user", font=(self.GAME_FONT, 14, "bold"), command=lambda: self.load_user())
        load_user_button.place(relx=1, rely=1, x=-60, y=-60, anchor=SE)
        new_user_button = Button(self.background_canvas, text="Add new user", font=(self.GAME_FONT, 12, "bold"), command=self.draw_register_user)
        new_user_button.place(relx=0.5, rely=0.5, y=65, anchor=N)
        back_button = Button(self.background_canvas, text="Back", font=(self.GAME_FONT, 14, "bold"), command=self.draw_main_menu)
        back_button.place(relx=0, rely=1, x=60, y=-60, anchor=SW)
        return

    def draw_register_first_user(self):
        self.create_add_user_widgets(self.draw_main_menu)
        return
    
    def draw_register_user(self):
        for child in self.background_canvas.winfo_children():
            child.destroy()

        self.create_add_user_widgets(self.draw_select_user)
        back_button = Button(self.background_canvas, text= "← Back", borderwidth=5, font=(self.GAME_FONT, 14, "bold"), command=self.draw_select_user)
        back_button.place(relx=0, rely=1, x=60, y=-60, anchor=SW)
        return
        
    def create_add_user_widgets(self, next_draw):
        input_label = Label(self.background_canvas, text="Input your username:", font=(self.GAME_FONT, 16, "bold"), background=self.LABEL_COLOR, relief="ridge", borderwidth=5)
        input_label.place(relx=0.5, rely=0.5, y=-50, anchor=S)
        input_box = Entry(self.background_canvas, borderwidth=5, font=(self.GAME_FONT, 16, "bold"))
        input_box.place(relx=0.5, rely=0.5, anchor=CENTER)
        submit_button = Button(self.background_canvas, text="Submit", font=(self.GAME_FONT, 14, "bold"), command=lambda: [self.add_user(input_box, next_draw)])
        submit_button.place(relx=1, rely=1, x=-60, y=-60, anchor=SE)
        return
    
    def add_user(self, input_box, next_draw):
        """Creates a new user object with name set as per input_box content, if it is valid. If successful, proceeds to the next screen"""
        new_user_name = input_box.get().strip()
        if new_user_name == "":
            return

        for user in self.user_list:
            if new_user_name == user.name:
                return
        
        new_user = User(new_user_name)
        self.current_user = new_user
        self.user_list.append(new_user)
        next_draw()
        return
    
    def load_user(self):
        """Fetches the user selected in a listbox and sets it as the current user, then returns to the main menu"""
        try:
            selected_user = self.user_listbox.get(self.user_listbox.curselection()[0])
            for user in self.user_list:
                if user.name == selected_user:
                    self.current_user = user
                    self.draw_main_menu()
        except IndexError:
            return
        return

    def on_closing(self):
        self.wait_var.set(-1)
        self.destroy()
        return

class User:
    """GoB user class. Contains user data"""
    def __init__(self, name, high_score = [0, 0], skill_level = {}):
        self.name = name
        self.high_score = high_score # Score, time in seconds
        self.skill_level = skill_level # Weighted skill level dictionary for each bird that has been present in a game of GoB
        self.points_temp = 0 # Temporary score that is wiped between each match¨
    
    def change_skill_level(self, bird_name, options_chosen_from, is_correct=True):
        if bird_name in self.skill_level:
            current_skill_level = self.skill_level[bird_name]
        else:
            current_skill_level = 0.3
        
        MIN_CHANGE_RATE = 2 # minimum change rate, higher means slower change
        DEFAULT_OPTION_AMOUNT = 10 #the amount of options at which the change rate is MIN_CHANGE_RATE + 1, otherwise the skill level will change less the "easier" the result was to achieve

        if is_correct:
            change_rate = MIN_CHANGE_RATE*(DEFAULT_OPTION_AMOUNT/options_chosen_from + 1/MIN_CHANGE_RATE)
            new_skill_level = current_skill_level + (1-current_skill_level)/change_rate
        else:
            change_rate = MIN_CHANGE_RATE*(options_chosen_from/DEFAULT_OPTION_AMOUNT + 1/MIN_CHANGE_RATE)
            new_skill_level = current_skill_level - current_skill_level/change_rate

        new_skill_level = round(new_skill_level, 2)
        if new_skill_level == 0:
            new_skill_level = 0.01
        self.skill_level[bird_name] = new_skill_level
        return

class BoG: 
    '''Bird of Game of Bird'''
    times_existed = 0
    def __init__(self, common_name, scientific_name, image_paths):
        self.common_name = common_name
        self.scientific_name = scientific_name
        self.image_paths = image_paths

class Game_mode:
    """Parent class for the GoB game modes. Contains variables and methods that are shared between the different game modes."""
    def __init__(self, main_window, background_canvas, bird_list, current_user, grid_dimensions, settings, wait_var):
        self.main_window = main_window
        self.main_window.resizable(False, False)
        self.GAME_FONT = self.main_window.GAME_FONT
        self.LABEL_COLOR = self.main_window.LABEL_COLOR
        self.background_canvas = background_canvas
        self.bird_list = bird_list
        self.current_user = current_user
        self.grid_dimensions = grid_dimensions
        self.tile_amount = self.grid_dimensions[0]*self.grid_dimensions[1]
        self.window_size = (main_window.winfo_width(), main_window.winfo_height())
        self.window_ratio = main_window.winfo_height()/main_window.winfo_width()
        self.frame_ratio = self.grid_dimensions[0]/self.grid_dimensions[1]
        self.settings = settings
        self.old_bird_percent = 50 # Future setting
        self.wait_var = wait_var

    def start_one_player_mode(self):
        self.is_game_over = False
        for child in self.background_canvas.winfo_children():
            child.destroy()

        bird_amount = self.settings.one_player_rounds
        self.pick_birds_for_game(bird_amount)
        self.draw_game_mode_essentials()
        self.bird_label = Label(self.background_canvas, font=(self.GAME_FONT, 14, "bold"), bg=self.LABEL_COLOR, relief=RAISED)
        self.bird_label.place(relx=0.5, rely=0, y=20, anchor=N)
        self.point_label = Label(self.background_canvas, text=f"Points: {self.current_user.points_temp}", bg=self.main_window.LABEL_COLOR, relief=RIDGE, font=(self.main_window.GAME_FONT, 14, "bold"))
        self.point_label.place(relx=0.5, rely=1, y=-40, anchor=S)
        return
    
    def pick_birds_for_game(self, bird_amount):
        """Randomizes the birds to be used for the current game"""
        bird_list_shuffled = self.bird_list.copy()
        rand.shuffle(bird_list_shuffled) # Shuffles the bird in use list to make picking random birds easier

        if len(self.current_user.skill_level) == 0: # If one player modes have not been played by the current user before
            self.bird_in_use_list = bird_list_shuffled[0:bird_amount]
        else:
            self.bird_in_use_list = []
            self.add_old_birds(bird_amount)
            self.add_new_birds(bird_amount, bird_list_shuffled)
            rand.shuffle(self.bird_in_use_list) # Sets the order that the birds will appear in
        return

    def add_old_birds(self, total_bird_amount):
        """Adds birds previously seen by the user to active birds. These birds are weighted based on user skill level (if the user has seen enough birds)"""
        skill_total = self.calculate_skill_total()
        old_bird_amount = (total_bird_amount*self.old_bird_percent)//100

        if old_bird_amount > len(self.current_user.skill_level): # If the user has previously seen less birds than the amount of old birds to be added, add all the user's seen birds to list.
            # old_bird_amount = len(self.current_user.skill_level)
            for bird in self.bird_list:
                for bird_name in self.current_user.skill_level:
                    if bird_name == bird.common_name:
                        self.bird_in_use_list.append(bird)
        else:
            while len(self.bird_in_use_list) < old_bird_amount:
                bird = self.pick_old_bird(skill_total)
                if bird not in self.bird_in_use_list: # Duplicates not allowed
                    self.bird_in_use_list.append(bird)
        return
    
    def calculate_skill_total(self):
        """Calculates and returns the current user's skill total"""
        skill_total = 0
        self.SKILL_WEIGHT = 2 # Higher numbers mean skill level differences will make a bigger difference when choosing birds (a value of 1 will mean x*skill level gives x*chance)

        for old_bird in self.current_user.skill_level:
            skill_level = self.current_user.skill_level[old_bird]
            if not skill_level == 0:
                skill_total += (1/skill_level)**self.SKILL_WEIGHT
            else:
                skill_total += 100**self.SKILL_WEIGHT
        return skill_total
    
    def pick_old_bird(self, skill_total):
        """Selects and returns a random bird from previously seen birds in one player modes, weighted against current user skill level"""
        skill_sum = 0

        randomized = rand.uniform(0, skill_total)
        for old_bird in self.current_user.skill_level:
            skill_level = self.current_user.skill_level[old_bird]
            if not skill_level == 0:
                skill_sum += (1/skill_level)**self.SKILL_WEIGHT
            else:
                skill_sum += 100**self.SKILL_WEIGHT
            if skill_sum >= randomized:
                for bird in self.bird_list: # To get the bird object from the name
                    if bird.common_name == old_bird:
                        return bird
        return
    
    def add_new_birds(self, total_bird_amount, bird_list_shuffled):
        """Adds birds which have not previously been seen by the current user to active birds. If no such bird exists, instead randomly adds birds that are not yet active"""
        for bird in bird_list_shuffled:
            if len(self.bird_in_use_list) >= total_bird_amount:
                return
            else:
                if bird.common_name not in self.current_user.skill_level: # No previously seen birds allowed
                    self.bird_in_use_list.append(bird)

        for bird in bird_list_shuffled: # If there are no more birds not seen by user
            if bird not in self.bird_in_use_list: # Duplicates not allowed but previously seen birds are
                self.bird_in_use_list.append(bird)
        return
    
    def draw_game_mode_essentials(self):
        self.draw_frame()
        self.draw_button_grid()
        self.create_back_button()
        return
    
    def draw_frame(self):
        self.button_frame = Frame(self.background_canvas)
        if self.window_ratio < self.frame_ratio:
            pady = 100
            height = self.window_size[1] - 2*pady
            width = height/self.frame_ratio
            self.button_frame.place(width=width, height=height, relx=0.5, rely=0.5, anchor=CENTER)
        else:
            padx = 100
            width = self.window_size[0] - 2*padx
            height = width*self.frame_ratio
            self.button_frame.place(width=width, height=height, relx=0.5, rely=0.5, anchor=CENTER)
        return

    def draw_button_grid(self):
        self.tile_list = []
        for row in range(self.grid_dimensions[0]):
            row_of_tiles = []
            for column in range(self.grid_dimensions[1]):
                tile = Button(self.button_frame)
                tile["font"] = ("Open Sans Condensed Medium", 9)
                tile.grid(row=row, column=column, sticky="nsew")
                row_of_tiles.append(tile)
                self.button_frame.columnconfigure(column, weight=1)
            self.tile_list.append(row_of_tiles)
            self.button_frame.rowconfigure(row, weight=1)
            
        self.button_frame.update()
        width = self.button_frame.winfo_height()
        self.button_frame.config(height=width, width=width*self.frame_ratio)
        self.get_tile_size()
        self.set_button_sizes()
        return
    
    def get_tile_size(self):
        """Fetches tile size for the current grid size from the tile at row=0 and column=0"""
        example_tile = self.tile_list[0][0]
        example_tile.update()
        self.tile_width = example_tile.winfo_width()
        self.tile_height = self.tile_width
        return
    
    def set_button_sizes(self):
        """Configures the size of all buttons"""
        # max_font_size = (self.tile_width)//10
        for tile_row in self.tile_list:
            for tile in tile_row:
                # tile.config(height=self.tile_height, width=self.tile_width)
                tile.config(height=3, width=3)
                tile["wraplength"] = self.tile_width - 6
                # tile["font"] = ("Open Sans Condensed Medium", max_font_size)
        return

    def create_back_button(self):
        back_button = Button(self.background_canvas, text="Exit to main menu", font=(self.main_window.GAME_FONT, 12, "bold"), command=lambda: [self.reset_user_points(), self.main_window.draw_main_menu()])
        back_button.place(relx=0, rely=1, x=40, y=-40, anchor=SW)
        return
    
    def get_birds_to_display(self, bird_index):
        """Returns a list of randomized birds and one specific bird with the index of the specific bird"""
        bird_list_shuffled = self.bird_list.copy()
        rand.shuffle(bird_list_shuffled)
        birds_to_display = [self.bird_in_use_list[bird_index]]

        i=0
        while len(birds_to_display) < self.tile_amount:
            bird = bird_list_shuffled[i]
            if not bird in birds_to_display:
                birds_to_display.append(bird)
            i += 1

        rand.shuffle(birds_to_display)
        return birds_to_display
    
    def await_keypress(self):
        """Waits until next keypress"""
        self.main_window.bind("<Button>", lambda e: self.wait_var.set(0), add="+")
        self.main_window.wait_variable(self.wait_var)
        self.main_window.unbind("<Button>")
        self.main_window.after(100) # To prevent the click that activates the window from clicking the buttons as well
        for tile_row in self.tile_list: # Needed so the buttons don't take clicks from when the window is waiting
            for tile in tile_row:
                tile.update()
        return
    
    def disable_buttons(self, dont_disable=[]):
        """Disables all buttons except the ones in passed list"""
        for tile_row in self.tile_list:
                for tile in tile_row:
                    if not tile in dont_disable:
                        tile["state"] = DISABLED

    def activate_buttons(self, dont_activate=[]):
        """Activates all buttons"""
        for tile_row in self.tile_list:
                for tile in tile_row:
                    if not tile in dont_activate:
                        tile["state"] = ACTIVE

    def evaluate_guess(self, tile):
        is_correct = self.check_if_correct(tile)
        current_bird_name = getattr(self.bird_in_use_list[self.current_bird_index], "common_name")
        self.current_user.change_skill_level(current_bird_name, self.tile_amount, is_correct)

    def check_if_correct(self, tile):
        if tile == self.current_correct_tile:
            self.bird_label["image"] = ""
            self.bird_label["text"] = "Correct!"
            self.current_user.points_temp += 1
            self.point_label["text"] = f"Points: {self.current_user.points_temp}"
            is_correct = True
        else:
            self.bird_label["image"] = ""
            self.bird_label["text"] = "Wrong :("
            is_correct = False
        return is_correct
    
    def reset_user_points(self):
        self.current_user.points_temp = 0
        return
    
    def draw_game_over(self):
        """Displays score and an exit button which resets user points"""
        self.point_label.destroy()
        for child in self.button_frame.winfo_children():
            child.destroy()

        game_over_label = Label(self.button_frame, text=f"Game finished!\n You got {self.current_user.points_temp} points out of {len(self.bird_in_use_list)} possible", font=(self.GAME_FONT, 14, "bold"), background=self.LABEL_COLOR, relief="ridge", wraplength=self.button_frame.winfo_width())
        game_over_label.place(relx=0.5, rely=0.5, anchor=CENTER)
        return

class Mode_text_to_image(Game_mode):
    """GoB text to image game mode. Inherits variables and methods from the Game_mode class"""
    def __init__(self, main_window, background_canvas, bird_list, current_user, settings, wait_var):
        grid_dimensions = settings.text_to_image_size
        super().__init__(main_window, background_canvas, bird_list, current_user, grid_dimensions, settings, wait_var)
        
        self.start_text_to_image()
        
    def start_text_to_image(self):
        self.start_one_player_mode()
        self.assign_button_commands()
        self.current_correct_tile = None
        self.current_bird_index = 0
        # self.bird_label = Label(self.background_canvas, font=(self.GAME_FONT, 14, "bold"), bg=self.LABEL_COLOR, relief=RAISED)
        # self.bird_label.place(relx=0.5, rely=0, y=20, anchor=N)
        
        self.new_bird()
        return
    
    def assign_button_commands(self):
        for tile_row in self.tile_list:
            for tile in tile_row:
                tile["command"] = lambda tile=tile: self.image_clicked(tile)
        return
    
    def image_clicked(self, tile):
        self.wait_var.set(0)
        self.evaluate_guess(tile)
        self.current_correct_tile["command"] = ""
        self.disable_buttons([self.current_correct_tile])
        self.await_keypress()
        self.activate_buttons()
        self.current_correct_tile["command"] = lambda tile=self.current_correct_tile: self.image_clicked(tile)

        self.current_bird_index += 1
        if self.current_bird_index >= len(self.bird_in_use_list):
            self.draw_game_over()
        else:
            self.new_bird()
        return
    
    def new_bird(self):
        self.show_new_bird_name(self.current_bird_index)
        birds_to_display = self.get_birds_to_display(self.current_bird_index)
        self.show_new_bird_images(self.current_bird_index, birds_to_display)
        self.main_window.wait_variable(self.wait_var)
    
    def show_new_bird_name(self, bird_index):
        self.bird_label["text"] = f"{getattr(self.bird_in_use_list[bird_index], self.settings.name_type)}"
        return

    def show_new_bird_images(self, bird_index, birds_to_display):
        self.displayed_images = [] # for anti-garbage-collection purposes

        i = 0
        for tile_row in self.tile_list:
            for tile in tile_row:
                bird = birds_to_display[i]
                bird_img = Image.open(rand.choice(bird.image_paths))
                bird_img = bird_img.resize((self.tile_width, self.tile_height))
                bird_img_tkinter = ImageTk.PhotoImage(bird_img)
                if bird == self.bird_in_use_list[bird_index]:
                    self.current_correct_tile = tile
                    # print(tile.grid_info() ["column"])
                self.displayed_images.append(bird_img_tkinter)
                tile["image"] = bird_img_tkinter
                i += 1
        return
    
    def draw_game_over(self):
        super().draw_game_over()
        play_again_button = Button(self.button_frame, text="Play again", font=(self.main_window.GAME_FONT, 14, "bold"), command=lambda: [self.reset_user_points(), self.start_text_to_image()])
        play_again_button.place(relx=0.5, rely=1, y=-20, anchor=S)
        return

class Mode_image_to_text(Game_mode):
    """GoB image to text game mode. Inherits variables and methods from the Game_mode class"""
    def __init__(self, main_window, background_canvas, bird_list, current_user, settings, wait_var):
        grid_dimensions = settings.image_to_text_size
        super().__init__(main_window, background_canvas, bird_list, current_user, grid_dimensions, settings, wait_var)

        self.start_image_to_text()
        
    def start_image_to_text(self):
        self.start_one_player_mode()
        self.assign_button_commands()
        self.current_correct_tile = None
        self.current_bird_index = 0
        # self.bird_label = Label(self.background_canvas, font=(self.GAME_FONT, 14, "bold"), bg=self.LABEL_COLOR, relief=RAISED)
        # self.bird_label.place(relx=0.5, rely=0, y=20, anchor=N)
        
        self.new_bird()
        return
    
    def assign_button_commands(self):
        for tile_row in self.tile_list:
            for tile in tile_row:
                tile["command"] = lambda tile=tile: self.name_clicked(tile)
        return
    
    def name_clicked(self, tile):
        self.wait_var.set(0)
        self.evaluate_guess(tile)
        self.current_correct_tile["command"] = ""
        self.disable_buttons([self.current_correct_tile])
        self.await_keypress()
        self.activate_buttons()
        self.current_correct_tile["command"] = lambda tile=self.current_correct_tile: self.name_clicked(tile)

        self.current_bird_index += 1
        if self.current_bird_index >= len(self.bird_in_use_list):
            self.draw_game_over()
        else:
            self.new_bird()
        return
    
    def new_bird(self):
        self.show_new_bird_image(self.current_bird_index)
        birds_to_display = self.get_birds_to_display(self.current_bird_index)
        self.show_new_bird_names(self.current_bird_index, birds_to_display)
        self.main_window.wait_variable(self.wait_var)
    
    def show_new_bird_image(self, bird_index):
        bird = self.bird_in_use_list[bird_index]
        bird_img = Image.open(rand.choice(bird.image_paths))
        bird_img = bird_img.resize((100, 100))
        bird_img_tkinter = ImageTk.PhotoImage(bird_img)
        self.bird_label["image"] = bird_img_tkinter
        self.current_bird_image = bird_img_tkinter # for anti-garbage-collection purposes
        return

    def show_new_bird_names(self, bird_index, birds_to_display):
        i = 0
        for tile_row in self.tile_list:
            for tile in tile_row:
                bird = birds_to_display[i]
                bird_name = getattr(bird, self.settings.name_type)
                if bird_name == getattr(self.bird_in_use_list[bird_index], self.settings.name_type):
                    self.current_correct_tile = tile
                tile["text"] = bird_name
                i += 1
        return
    
    def draw_game_over(self):
        super().draw_game_over()
        play_again_button = Button(self.button_frame, text="Play again", font=(self.main_window.GAME_FONT, 14, "bold"), command=lambda: [self.reset_user_points(), self.start_image_to_text()])
        play_again_button.place(relx=0.5, rely=1, y=-20, anchor=S)
        return

class Mode_memory(Game_mode):
    """GoB memory game mode. Inherits variables and methods from the Game_mode class"""
    def __init__(self, main_window, background_canvas, bird_list, current_user, settings, wait_var, user_list):
        grid_dimensions = settings.memory_size
        super().__init__(main_window, background_canvas, bird_list, current_user, grid_dimensions, settings, wait_var)
        self.revealed_tiles = []
        self.revealed_tile_content = []
        self.user_list = user_list
        self.player_1 = current_user
        self.active_player = self.player_1

        self.draw_select_player_two()

    def draw_select_player_two(self):
        for child in self.background_canvas.winfo_children():
            child.destroy()
            
        select_user_frame = Frame(self.background_canvas)
        select_user_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.draw_select_player_two_widgets(select_user_frame)

        for user in self.user_list:
            if not user == self.player_1:
                self.user_listbox.insert(END, user.name)

        if len(self.user_list) > 5:
            user_scrollbar = Scrollbar(select_user_frame)
            user_scrollbar.pack(side=RIGHT, fill="y")
            self.user_listbox.config(yscrollcommand = user_scrollbar.set)
            user_scrollbar.config(command = self.user_listbox.yview)
        return
    
    def draw_select_player_two_widgets(self, select_user_frame):
        select_player_two_label = Label(self.background_canvas, text=f"Select player 2:", font=(self.GAME_FONT, 14, "bold"), background=self.LABEL_COLOR, relief="ridge")
        select_player_two_label.place(relx=0.5, rely=0.5, y=-70, anchor=S)
        load_user_button = Button(self.background_canvas, text="Load user", font=(self.GAME_FONT, 14, "bold"), command=lambda: self.select_player_two())
        load_user_button.place(relx=1, rely=1, x=-60, y=-60, anchor=SE)
        back_button = Button(self.background_canvas, text="Back", font=(self.GAME_FONT, 14, "bold"), command=self.main_window.draw_main_menu)
        back_button.place(relx=0, rely=1, x=60, y=-60, anchor=SW)
        self.user_listbox = Listbox(select_user_frame, width=20, height=5, font=(self.GAME_FONT, 14, "bold"))
        self.user_listbox.pack(side=LEFT)
        return
    
    def select_player_two(self):
        """Fetches the user selected in a listbox and sets it as player 2, then initiates the game mode"""
        try:
            selected_user = self.user_listbox.get(self.user_listbox.curselection()[0])
            for user in self.user_list:
                if user.name == selected_user:
                    self.player_2 = user
                    self.start_memory_game()
        except IndexError:
            return
        return
    
    def start_memory_game(self):
        self.is_game_over = False
        self.dont_activate = []
        bird_amount = math.ceil(self.tile_amount/2)
        self.bird_in_use_list = self.bird_list.copy()
        rand.shuffle(self.bird_in_use_list)
        self.bird_in_use_list = self.bird_in_use_list[0:bird_amount]

        for child in self.background_canvas.winfo_children():
            child.destroy()

        self.draw_game_mode_essentials()
        self.draw_memory_labels()
        self.set_button_sizes()
        self.assign_button_commands()
        self.create_tile_data()
        return

    def draw_memory_labels(self):
        self.active_player_label = Label(self.background_canvas, text=f"{self.active_player.name}'s turn:", font=(self.GAME_FONT, 16, "bold"), bg=self.LABEL_COLOR, relief="ridge")
        self.active_player_label.place(relx=0.5, rely=0, y=20, anchor=N)
        self.player_1_score_label = Label(self.background_canvas, text=f"{self.player_1.name}:\n{self.player_1.points_temp} points", font=(self.GAME_FONT, 16, "bold"), bg=self.LABEL_COLOR, relief="ridge")
        self.player_1_score_label.place(relx=0, rely=0.5, x=50, anchor=W)
        self.player_2_score_label = Label(self.background_canvas, text=f"{self.player_2.name}:\n{self.player_2.points_temp} points", font=(self.GAME_FONT, 16, "bold"), bg=self.LABEL_COLOR, relief="ridge")
        self.player_2_score_label.place(relx=1, rely=0.5, x=-50, anchor=E)
        return
    
    def assign_button_commands(self):
        """Configures the buttons to show their contents once pressed"""
        for tile_row in self.tile_list:
            for tile in tile_row:
                tile["command"] = lambda tile=tile: self.show_tile_identity(tile)
        return
    
    def create_tile_data(self):
        '''Creates image objects, resizes them to tile size and saves tile/pair data'''
        self.tile_content_list = []
        self.tile_pair_dict = {}
        for bird in self.bird_in_use_list:
            bird_img = Image.open(rand.choice(bird.image_paths))
            bird_img = bird_img.resize((self.tile_width, self.tile_height))
            bird_img_tkinter = ImageTk.PhotoImage(bird_img)
            self.tile_content_list.append(bird_img_tkinter)
            self.tile_content_list.append(getattr(bird, self.settings.name_type))
            self.tile_pair_dict[getattr(bird, self.settings.name_type)] = bird_img_tkinter

        rand.shuffle(self.tile_content_list)
        return
    
    def show_tile_identity(self, tile):
        '''Shows bird image/name on tile depending on its contents. Also checks if two tiles have been revealed'''
        i = tile.grid_info()["row"]*self.grid_dimensions[1] + tile.grid_info()["column"]
        if type(self.tile_content_list[i]) == str:
            # tile.config(text=(self.tile_content_list[i]).replace(" ", "\n"), command="", relief=SUNKEN)
            tile.config(text=(self.tile_content_list[i]), command="", relief=SUNKEN)
            # tile.config(text="ERYTHROPHTHALMUS\nERYTHROPHTHALMUS", command="", relief=SUNKEN)
        else:
            tile.config(image=self.tile_content_list[i], command="", relief=SUNKEN)

        self.revealed_tiles.append(tile)
        self.revealed_tile_content.append(self.tile_content_list[i])
        if len(self.revealed_tile_content) == 2:
            self.two_tiles_revealed()
        return
    
    def two_tiles_revealed(self):
        """Checks if the two revealed tiles are a pair and if it is game over"""
        revealed_1 = self.revealed_tile_content[0]
        revealed_2 = self.revealed_tile_content[1]
        
        if (type(revealed_1) == str and self.tile_pair_dict[revealed_1] == revealed_2) or (type(revealed_2) == str and self.tile_pair_dict[revealed_2] == revealed_1):
            is_pair = True
            self.revealed_pair()
        else:
            is_pair = False
            self.revealed_not_pair()

        self.disable_buttons(self.revealed_tiles)
        self.await_keypress()

        if self.is_game_over:
            self.draw_game_over()
        else:
            self.active_player_label["text"] = f"{self.active_player.name}'s turn:"
            self.next_turn(is_pair)
            # self.activate_buttons(is_pair)
        
        self.revealed_tiles.clear()
        self.revealed_tile_content.clear()
        return
    
    def next_turn(self, is_pair):
        if is_pair:
            self.remove_buttons(self.revealed_tiles)
            for tile in self.revealed_tiles:
                self.dont_activate.append(tile)
            self.activate_buttons(self.dont_activate)
        else:
            self.remove_button_content(self.revealed_tiles)
            self.activate_buttons(self.dont_activate)

        return

    def revealed_pair(self):
        """If tiles are a pair: Assign a point to current player, remove revealed tiles and update if game is over"""
        self.active_player.points_temp += 1
        self.player_1_score_label["text"] = f"{self.player_1.name}:\n{self.player_1.points_temp} points"
        self.player_2_score_label["text"] = f"{self.player_2.name}:\n{self.player_2.points_temp} points"
        point_total = self.player_1.points_temp + self.player_2.points_temp
        self.active_player_label["text"] = "Pair found!"

        if point_total >= self.tile_amount//2:
            self.is_game_over = True
        return
    
    def revealed_not_pair(self):
        """If tiles are not a pair: Hide revealed tiles and change active player"""
        self.active_player_label["text"] = "No pair :("
        self.change_active_player()
        return
    
    def change_active_player(self):
        if self.active_player == self.player_1:
            self.active_player = self.player_2
        else:
            self.active_player = self.player_1
    
    def reset_user_points(self):
        """"Resets both user object's temporary points. Function is called when quitting to main menu"""
        self.player_1.points_temp = 0
        self.player_2.points_temp = 0
        return

    def remove_buttons(self, tiles):
        for tile in tiles:
            tile.config(text="", image="", relief=RIDGE, state=DISABLED, bg="#648a55") #62a858, #598f51, #597a4c, #648a55

    def remove_button_content(self, tiles):
        """Removes content of clicked tiles and reassigns their commands"""
        for tile in tiles:
            tile.config(text="", image="", relief=RAISED, command=lambda tile=tile: self.show_tile_identity(tile))
        return
    
    def draw_game_over(self):
        for child in self.button_frame.winfo_children():
            child.destroy()

        winner = self.determine_winner()
        self.active_player_label["text"] = f"Game over!"
        
        game_over_label = Label(self.button_frame, text=f"Congratulations\n{winner}!!!\n You have won!", font=(self.GAME_FONT, 14, "bold"), background=self.LABEL_COLOR, relief="ridge")
        if winner == None:
            game_over_label["text"] = f"It's a draw!"
        game_over_label.place(relx=0.5, rely=0.5, anchor=CENTER)
        
        play_again_button = Button(self.button_frame, text="Play again", font=(self.main_window.GAME_FONT, 14, "bold"), command=lambda: [self.reset_user_points(), self.start_memory_game()])
        play_again_button.place(relx=0.5, rely=1, y=-20, anchor=S)
        return
    
    def determine_winner(self):
        if self.player_1.points_temp > self.player_2.points_temp:
            winner = self.player_1.name
        elif self.player_2.points_temp > self.player_1.points_temp:
            winner = self.player_2.name
        else:
            winner = None
        return winner
    
class Settings():
    """GoB file manager class. Used to save/load data to/from text files"""
    def __init__(self):
        SETTINGS_FILE_PATH = str(os.getcwd())+"\\"+"settings.txt"

        self.one_player_rounds = 5
        self.text_to_image_size = (2, 4)
        self.image_to_text_size = (2, 4)
        self.memory_size = (4, 4)
        self.name_type = "common_name"

        if not os.path.isfile(SETTINGS_FILE_PATH):
            open("settings.txt", "x").close() # Creates a settings file
        else:
            with open("settings.txt", "r") as f:
                text_lines = f.readlines()
                if len(text_lines) > 0: # In case of a corrupt file
                    line = text_lines[0]
                    dct = json.loads(line)
                    if type(dct) == dict:
                        for key in dct:
                            setattr(self, key, dct[key])

    def save_settings(self):
        with open("settings.txt", "w") as f:
            json.dump(vars(self), f)
        return

    def draw_settings(self, main_window):
        for child in main_window.background_canvas.winfo_children():
            child.destroy()

        back_button = Button(main_window.background_canvas, text="Back", font=(main_window.GAME_FONT, 14, "bold"), command=main_window.draw_main_menu)
        back_button.place(relx=0, rely=1, x=40, y=-40, anchor=SW)

        self.draw_one_player_round_settings(main_window)
        self.draw_text_to_image_settings(main_window)
        self.draw_image_to_text_settings(main_window)
        self.draw_memory_settings(main_window)
        self.draw_name_type_settings(main_window)

        main_window.background_canvas.rowconfigure((0, 1, 2, 3, 4), weight=1)
        main_window.background_canvas.columnconfigure((0, 1), weight=1)

        # settings_scrollbar = Scrollbar(main_window)
        # settings_scrollbar.place(relx=1, relheight=1, anchor=NE)
        # main_window.background_canvas.config(yscrollcommand = settings_scrollbar.set)
        # settings_scrollbar.config(command = main_window.background_canvas.yview)
        return
    
    def draw_one_player_round_settings(self, main_window):
        one_player_rounds_label = Label(main_window.background_canvas, text="Rounds of game of GoB:", font=(main_window.GAME_FONT, 14, "bold"))
        one_player_rounds_label.grid(row=0, column=0, padx=20, pady=(100, 10), sticky="e")
        one_player_rounds_input_frame = Frame(main_window.background_canvas)
        one_player_rounds_input_frame.grid(row=0, column=1, padx=20, pady=(100, 10), sticky="w")
        one_player_rounds_input = Entry(one_player_rounds_input_frame, width=2, font=(main_window.GAME_FONT, 14, "bold"))
        one_player_rounds_input.pack(side=LEFT)
        one_player_rounds_button = Button(one_player_rounds_input_frame, text="OK", font=(main_window.GAME_FONT, 10, "bold"), command=lambda: self.set_one_player_rounds(one_player_rounds_input))
        one_player_rounds_button.pack(side=LEFT)

    def set_one_player_rounds(self, input):
        try:
            if 0 < int(input.get()) < 999: # Maximum 999 rounds because I hate fun
                self.one_player_rounds = int(input.get())
                input.delete(0, END)
        except ValueError:
            return

    def draw_text_to_image_settings(self, main_window):
        text_to_image_size_label = Label(main_window.background_canvas, text="Set text to image grid size:", font=(main_window.GAME_FONT, 14, "bold"))
        text_to_image_size_label.grid(row=1, column=0, padx=20, pady=10, sticky="e")
        text_to_image_size_input_frame = Frame(main_window.background_canvas)
        text_to_image_size_input_frame.grid(row=1, column=1, padx=20, pady=10, sticky="w")
        text_to_image_x_input = Entry(text_to_image_size_input_frame, width=2, font=(main_window.GAME_FONT, 14, "bold"))
        text_to_image_x_input.pack(side=LEFT)
        text_to_image_x_label = Label(text_to_image_size_input_frame, text="x", font=(main_window.GAME_FONT, 14, "bold"))
        text_to_image_x_label.pack(side=LEFT)
        text_to_image_y_input = Entry(text_to_image_size_input_frame, width=2, font=(main_window.GAME_FONT, 14, "bold"))
        text_to_image_y_input.pack(side=LEFT)
        text_to_image_size_button = Button(text_to_image_size_input_frame, text="OK", font=(main_window.GAME_FONT, 10, "bold"), command=lambda: self.set_text_to_image_size(text_to_image_y_input, text_to_image_x_input))
        text_to_image_size_button.pack(side=LEFT)
        return

    def set_text_to_image_size(self, input1, input2):
        try:
            if int(input1.get())*int(input2.get()) < 526:
                self.text_to_image_size = (int(input1.get()), int(input2.get()))
                input1.delete(0, END)
                input2.delete(0, END)
        except ValueError:
            return
        return

    def draw_image_to_text_settings(self, main_window):
        image_to_text_size_label = Label(main_window.background_canvas, text="Set image to text grid size:", font=(main_window.GAME_FONT, 14, "bold"))
        image_to_text_size_label.grid(row=2, column=0, padx=20, pady=10, sticky="e")
        image_to_text_size_input_frame = Frame(main_window.background_canvas)
        image_to_text_size_input_frame.grid(row=2, column=1, padx=20, pady=10, sticky="w")
        image_to_text_x_input = Entry(image_to_text_size_input_frame, width=2, font=(main_window.GAME_FONT, 14, "bold"))
        image_to_text_x_input.pack(side=LEFT)
        image_to_text_x_label = Label(image_to_text_size_input_frame, text="x", font=(main_window.GAME_FONT, 14, "bold"))
        image_to_text_x_label.pack(side=LEFT)
        image_to_text_y_input = Entry(image_to_text_size_input_frame, width=2, font=(main_window.GAME_FONT, 14, "bold"))
        image_to_text_y_input.pack(side=LEFT)
        image_to_text_size_button = Button(image_to_text_size_input_frame, text="OK", font=(main_window.GAME_FONT, 10, "bold"), command=lambda: self.set_image_to_text_size(image_to_text_y_input, image_to_text_x_input))
        image_to_text_size_button.pack(side=LEFT)
        return

    def set_image_to_text_size(self, input1, input2):
        try:
            if 1 < int(input1.get())*int(input2.get()) < 1051:
                self.image_to_text_size = (int(input1.get()), int(input2.get()))
                input1.delete(0, END)
                input2.delete(0, END)
        except ValueError:
            return
        return

    def draw_memory_settings(self, main_window):
        memory_size_label = Label(main_window.background_canvas, text="Set memory grid size:", font=(main_window.GAME_FONT, 14, "bold"))
        memory_size_label.grid(row=3, column=0, padx=20, pady=10, sticky="e")
        memory_size_input_frame = Frame(main_window.background_canvas)
        memory_size_input_frame.grid(row=3, column=1, padx=20, pady=10, sticky="w")
        memory_x_input = Entry(memory_size_input_frame, width=2, font=(main_window.GAME_FONT, 14, "bold"))
        memory_x_input.pack(side=LEFT)
        memory_x_label = Label(memory_size_input_frame, text="x", font=(main_window.GAME_FONT, 14, "bold"))
        memory_x_label.pack(side=LEFT)
        memory_y_input = Entry(memory_size_input_frame, width=2, font=(main_window.GAME_FONT, 14, "bold"))
        memory_y_input.pack(side=LEFT)
        memory_size_button = Button(memory_size_input_frame, text="OK", font=(main_window.GAME_FONT, 10, "bold"), command=lambda: self.set_memory_size(memory_y_input, memory_x_input))
        memory_size_button.pack(side=LEFT)
        return

    def set_memory_size(self, input1, input2):
        try:
            if 1 < int(input1.get())*int(input2.get()) < 526:
                self.memory_size = (int(input1.get()), int(input2.get()))
                input1.delete(0, END)
                input2.delete(0, END)
        except ValueError:
            return
        return
    
    def draw_name_type_settings(self, main_window):
        name_type_label =  Label(main_window.background_canvas, text="Choose name type:", font=(main_window.GAME_FONT, 14, "bold"))
        name_type_label.grid(row=4, column=0, padx=20, pady=(10, 100), sticky="e")
        name_type_input_frame = Frame(main_window.background_canvas)
        name_type_input_frame.grid(row=4, column=1, padx=20, pady=(10, 100), sticky="w")
        buttonvar = StringVar(value=self.name_type)
        common_name_button = Radiobutton(name_type_input_frame, text="Common name", variable=buttonvar, value="common_name", font=(main_window.GAME_FONT, 12, "bold"), command=lambda: self.set_name_type(buttonvar))
        common_name_button.pack(side=LEFT)
        scientific_name_button = Radiobutton(name_type_input_frame, text="Scientific name", variable=buttonvar, value="scientific_name", font=(main_window.GAME_FONT, 12, "bold"), command=lambda: self.set_name_type(buttonvar))
        scientific_name_button.pack(side=LEFT)

    def set_name_type(self, buttonvar):
        self.name_type = buttonvar.get()

GoB()
