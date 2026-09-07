from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import os, errno
import sys
import json
from copy import deepcopy

import requests

# Utility Functions
def isValidPathname(pathname):
    # Tests if the given pathname is a valid name for a directory on the current OS
    # Warning: Just a bit hacky :P. Basically querying a potentially non-existant directory and seeing what errors we get back.
    ERROR_INVALID_NAME = 123 # Windows error code for invalid pathname
    
    try:
        if not isinstance(pathname, str) or not pathname: # Reject non-string objects and empty strings
            return False
        #END_IF
        root_dir = os.environ.get("HOMEDRIVE", "C:") if sys.platform == "win32" else os.path.sep
        assert os.path.isdir(root_dir) # Unfortunately, we do not support TempleOS as of this time
        
        root_dir = root_dir.rstrip(os.path.sep) + os.path.sep
        try:
            os.lstat(root_dir + pathname) # Check if path exists
        except OSError as exc:
            if hasattr(exc, "winerror"):
                if exc.winerror == ERROR_INVALID_NAME:
                    return False
                #END_IF
            elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                return False
            #END_IF
        #END_TRY
    except TypeError as exc:
        return False
    #END_TRY
    
    return True
#END_DEF
def isDuplicateEntry(new_entry, listbox):
    if new_entry in listbox.get(0, END):
        return True
    return False
#END_DEF

# Globals
pwd = os.path.dirname(os.path.abspath(sys.argv[0]))
ruleset_path = os.path.join(pwd, "src/databases")
ruleset_file = os.path.join(ruleset_path, "active_rulesets.json")
todo_file = os.path.join(ruleset_path, "todo.json")
database_list = ("Pokedex", "Attackdex", "Abilitydex", "Itemdex", "Conditiondex", "Featdex", "Classdex", "Racedex")

ruleset_listbox_selection_last = None
database_listbox_selection_last = None
entry_listbox_selection_last = None

todo_color = "light pink"

# Pokedex
classification = ("Tiny", "Small", "Medium", "Large", "Huge", "Gargantuan")
sr = ("1/8", "1/4", "1/2", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30")
hit_dice = ("1d4", "1d6", "1d8", "1d10", "1d12", "1d20", "1d100")
saves = ("Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma")
skills = ("Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception", "History", "Insight", "Intimidation", "Investigation", "Medicine", "Nature", "Perception", "Performance", "Persuasion", "Religion", "Sleight of Hand", "Stealth", "Survival")
default_evo_text = "{name1} can evolve into {name2} at level {lvl} and above. When it evolves, its health increases by double its level, and it gains {asi} points to add to its ability scores (max 20)."

# Attackdex
power = ("STR", "DEX", "CON", "INT", "WIS", "CHA")
type = ("???", "Normal", "Fighting", "Flying", "Poison", "Ground", "Rock", "Bug", "Ghost", "Steel", "Fire", "Water", "Grass", "Electric", "Psychic", "Ice", "Dragon", "Dark", "Fairy")
exhaustion = ("S+", "S", "S-", "A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-")

# Ruleset and Database Object Definitions
default_pokedex_entry = {
    "Redirect": "",
    "ID": 0,
    "Name": "",
    "Classification": classification[0],
    "SR": sr[0],
    "Min_Level": 1,
    "Hit_Dice": hit_dice[0],
    "Movement": "",
    "Senses": "",
    "Stats": {
        "HP": 0,
        "AC": 10,
        "STR": 10,
        "DEX": 10,
        "CON": 10,
        "INT": 10,
        "WIS": 10,
        "CHA": 10
    },
    "Skills": [],
    "Saves": [],
    "Evolution": "",
    "Legendary": 0,
    "Legendary_Resistances": "",
    "Legendary_Traits": "",
    "Legendary_Actions": ""
}
default_attack_entry = {
    "Redirect": "",
    "Name": "",
    "Type": type[0],
    "Power": [],
    "Time": "",
    "Duration": "",
    "Range": "",
    "Exhaustion": exhaustion[-1],
    "Description": "",
    "Higher_Levels": ""
}
default_ability_entry = {
    "Name": "",
    "Description": ""
}
default_item_entry = {
    "Redirect": "",
    "Name": "",
    "Cost": 0,
    "Category": "",
    "Description": ""
}
default_feat_entry = {
    "Name": "",
    "Category": "",
    "Description": ""
}
default_trainer_path_entry = {
    "Name": "",
    "Traits": {
        "LVL-2": {
            "Name": "",
            "Description": ""
        },
        "LVL-5": {
            "Name": "",
            "Description": ""
        },
        "LVL-5_Action": {
            "Name": "",
            "Description": ""
        },
        "LVL-9": {
            "Name": "",
            "Description": ""
        },
        "LVL-15": {
            "Name": "",
            "Description": ""
        }
    }
}
default_race_entry = {
    "Name": "",
    "Proficiency": "",
    "Specialty": ""
}
default_status_entry = {
    "Name": "",
    "Description": "",
    "Levels": []
}
default_database_library = {}
for database in database_list:
    default_database_library[database] = {}
#END_FOR

ruleset_library = {}

# Read in Ruleset List
if not os.path.isfile(ruleset_file):
    ruleset_library["rulesets"] = {};
    ruleset_library["todo"] = {};
else:
    ruleset_library["rulesets"] = {};
    active_rulesets = {}
    with open(ruleset_file, "r") as jfile:
        active_rulesets = json.load(jfile)
    
    for key,_ in active_rulesets["Rulesets"].items():
        current_ruleset_path = os.path.join(ruleset_path, key)
        ruleset_library["rulesets"][key] = deepcopy(default_database_library)
        for db in database_list:
            database_path = os.path.join(current_ruleset_path, db)
            database_file = os.path.join(database_path, db + ".json")
            with open(database_file, "r") as jfile:
                ruleset_library["rulesets"][key][db] = json.load(jfile)
        #END_FOR
    #END_FOR
#END_IF

if (not os.path.isfile(todo_file)) or (not os.path.isfile(ruleset_file)):
    ruleset_library["todo"] = {};
else:
    with open(todo_file, "r") as jfile:
        ruleset_library["todo"] = json.load(jfile)
#END_IF





# Create Window
# Needed here to enable class functionality
root = Tk()
frame_library = Frame(root, padx = 3, pady = 3)
frame_ruleset = LabelFrame(frame_library, text = "Ruleset")
frame_database = LabelFrame(frame_library, text = "Databases")
frame_entries = LabelFrame(root, text = "Entries")
frame_content = Frame(root, padx = 10, pady = 10)



scrollbar_ruleset = Scrollbar(frame_ruleset)
listbox_ruleset = Listbox(frame_ruleset, yscrollcommand = scrollbar_ruleset.set, selectmode = SINGLE, width = 20)
scrollbar_database = Scrollbar(frame_database)
listbox_database = Listbox(frame_database, yscrollcommand = scrollbar_database.set, selectmode = SINGLE, width = 20)
scrollbar_entries = Scrollbar(frame_entries)
listbox_entries = Listbox(frame_entries, yscrollcommand = scrollbar_entries.set, selectmode = SINGLE, width = 30)


# Initialize Ruleset Listbox with data loaded from file
for key, _ in ruleset_library["rulesets"].items():
    listbox_ruleset.insert("end", key)

# Classes to interface between JSON objects and entry forms
# Basically just stores the TKInter var objects globally
class EntryInterface:
    def callbackNumericOnly(self, P):
        return str.isdigit(P) or P == ""
    #END_DEF
    def createFrame(self, parent):
        pass
    def setFrameData(self, entry):
        pass
    def getFrameData(self, entry):
        pass
#END_CLASS
class PokedexEntryInterface(EntryInterface):
    redirect = StringVar()
    id = StringVar()
    name = StringVar()
    classification = StringVar()
    sr = StringVar()
    min_level = StringVar()
    hit_dice = StringVar()
    movement = StringVar()
    senses = StringVar()
    hp = StringVar()
    ac = StringVar()
    str = StringVar()
    dex = StringVar()
    con = StringVar()
    int = StringVar()
    wis = StringVar()
    cha = StringVar()
    saves = tuple(IntVar() for i in range(len(saves)))
    skills = tuple(IntVar() for i in range(len(skills)))
    evo_text = None
    legendary = IntVar()
    legendary_resist = None
    legendary_trait = None
    legendary_action = None
    
    combo_redirect = None
    def updateRedirectCombo(self):
        global listbox_entries
        redirect_values = [""]
        redirect_values.extend(listbox_entries.get(0, "end"))
        self.combo_redirect.configure(values = redirect_values)
    #END_DEF
    def createFrame(self, parent):
        global saves, skills, classification, sr, hit_dice
        
        vcmd = parent.register(self.callbackNumericOnly)
        
        # Configure Container Grid
        container = Frame(parent)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
        container.grid_columnconfigure(1, weight = 1)
        
        # Configure Skills and Saves Grid
        frame_profs = Frame(container)
        frame_profs.grid_columnconfigure(0, weight = 1)
        frame_profs.grid_rowconfigure(0, weight = 1)
        frame_profs.grid_rowconfigure(1, weight = 1)
        
        frame_saves = LabelFrame(frame_profs, text = "Saves")
        button_saves = tuple(Checkbutton(frame_saves, text = saves[i], variable = self.saves[i]) for i in range(len(saves)))
        for button in button_saves:
            button.pack(anchor = "w")
        
        frame_skills = LabelFrame(frame_profs, text = "Skills")
        button_skills = tuple(Checkbutton(frame_skills, text = skills[i], variable = self.skills[i]) for i in range(len(skills)))
        for button in button_skills:
            button.pack(anchor = "w")
        
        frame_saves.grid(row = 0, column = 0, sticky = "nsew", padx = 3, pady = 3)
        frame_skills.grid(row = 1, column = 0, sticky = "nsew", padx = 3, pady = 3)
        frame_profs.grid(row = 0, column = 1, sticky = "nsew", padx = 3, pady = 3)
        
        # Configure Stats and Info Grid
        frame_stats_info = Frame(container)
        frame_stats_info.grid_columnconfigure(0, weight = 1)
        frame_stats_info.grid_rowconfigure(0, weight = 1)
        frame_stats_info.grid_rowconfigure(1, weight = 1)
        frame_stats_info.grid_rowconfigure(2, weight = 1)
        frame_stats_info.grid_rowconfigure(3, weight = 1)
        frame_stats_info.grid_rowconfigure(4, weight = 1)
        frame_stats_info.grid_rowconfigure(5, weight = 1)
        frame_stats_info.grid_rowconfigure(6, weight = 1)
        frame_stats_info.grid_rowconfigure(7, weight = 1)
        frame_stats_info.grid_rowconfigure(8, weight = 1)
        frame_stats_info.grid_rowconfigure(9, weight = 1)
        frame_stats_info.grid_rowconfigure(10, weight = 1)
        frame_stats_info.grid_rowconfigure(11, weight = 1)
        frame_stats_info.grid_rowconfigure(12, weight = 1)
        frame_stats_info.grid_rowconfigure(13, weight = 1)
        

        
        # Redirection Entry
        frame_redirect = Frame(frame_stats_info)
        Label(frame_redirect, text = "Redirect: ").pack(side = "left")
        self.combo_redirect = ttk.Combobox(frame_redirect, textvariable = self.redirect, values = [""], width = 40, state = "readonly", postcommand = self.updateRedirectCombo)
        self.combo_redirect.pack(side = "left")
        
        Label(frame_redirect, textvariable = StringVar(frame_redirect, "     ID: ")).pack(side = "left")
        Entry(frame_redirect, textvariable = self.id, width = 10, validate='all', validatecommand = (vcmd, "%P")).pack(side = "left")
        frame_redirect.grid(row = 0, column = 0, sticky = "nsew")
        
        def entryWrapper(parent, title, box_width, interface, row, col, validatecommand = None):
            frame = Frame(parent)
            Label(frame, textvariable = StringVar(frame, title)).pack(side = "left")
            Entry(frame, textvariable = interface, width = box_width, validate='all', validatecommand = validatecommand).pack(side = "left")
            frame.grid(row = row, column = col, sticky = "nsew", padx = 3, pady = 3)
        #END_DEF
        
        def comboWrapper(parent, title, box_width, interface, values, row, col):
            frame = Frame(parent)
            Label(frame, textvariable = StringVar(frame, title)).pack(side = "left")
            ttk.Combobox(frame, textvariable = interface, values = values, width = box_width, state="readonly").pack(side = "left")
            frame.grid(row = row, column = col, sticky = "nsew", padx = 3, pady = 3)
        #END_DEF
        
        entryWrapper(frame_stats_info, "Name:                  ", 40, self.name, 1, 0)
        #entryWrapper(frame_stats_info, "     ID: ", 10, self.id, 1, 0)
        comboWrapper(frame_stats_info, "Classification:     ", 30, self.classification, classification, 2, 0)
        comboWrapper(frame_stats_info, "SR:                        ", 30, self.sr, sr, 3, 0)
        entryWrapper(frame_stats_info, "Minimum Level: ", 10, self.min_level, 4, 0, validatecommand = (vcmd, "%P"))
        comboWrapper(frame_stats_info, "Hit Dice:              ", 30, self.hit_dice, hit_dice, 5, 0)
        entryWrapper(frame_stats_info, "Movement:         ", 70, self.movement, 6, 0)
        entryWrapper(frame_stats_info, "Senses:                 ", 70, self.senses, 7, 0)
        
        # Configure Stats Grid
        frame_stats = Frame(frame_stats_info)
        frame_stats.grid_rowconfigure(0, weight = 1)
        frame_stats.grid_columnconfigure(0, weight = 1)
        frame_stats.grid_columnconfigure(1, weight = 1)
        frame_stats.grid_columnconfigure(2, weight = 1)
        frame_stats.grid_columnconfigure(3, weight = 1)
        frame_stats.grid_columnconfigure(4, weight = 1)
        frame_stats.grid_columnconfigure(5, weight = 1)
        frame_stats.grid_columnconfigure(6, weight = 1)
        frame_stats.grid_columnconfigure(7, weight = 1)
        
        entryWrapper(frame_stats, "HP: ", 4, self.hp, 0, 0, validatecommand = (vcmd, "%P"))
        entryWrapper(frame_stats, "AC: ", 4, self.ac, 0, 1, validatecommand = (vcmd, "%P"))
        entryWrapper(frame_stats, "STR: ", 4, self.str, 0, 2, validatecommand = (vcmd, "%P"))
        entryWrapper(frame_stats, "DEX: ", 4, self.dex, 0, 3, validatecommand = (vcmd, "%P"))
        entryWrapper(frame_stats, "CON: ", 4, self.con, 0, 4, validatecommand = (vcmd, "%P"))
        entryWrapper(frame_stats, "INT: ", 4, self.int, 0, 5, validatecommand = (vcmd, "%P"))
        entryWrapper(frame_stats, "WIS: ", 4, self.wis, 0, 6, validatecommand = (vcmd, "%P"))
        entryWrapper(frame_stats, "CHA: ", 4, self.cha, 0, 7, validatecommand = (vcmd, "%P"))
        
        frame_stats.grid(row = 8, column = 0, sticky = "nsew")
        
        #def textWrapper(parent, interface, title, box_width, box_height, row, column):
        #    frame = Frame(parent)
        #    Label(frame, textvariable = StringVar(frame, title)).pack(side = "top", anchor = "w")
        #    interface[0] = Text(frame, width = box_width, height = box_height, wrap = WORD)
        #    interface[0].pack(side = "left")
        #    frame.grid(row = row, column = column, sticky = "nsew")
        ##END_DEF
        
        # Evolution Text
        #textWrapper(frame_stats_info, [self.evo_text], "Evolution Description", 65, 2, 9, 0)
        frame1 = Frame(frame_stats_info)
        Label(frame1, textvariable = StringVar(frame1, "Evolution Description")).pack(side = "top", anchor = "w")
        self.evo_text = Text(frame1, width = 65, height = 2, wrap = WORD)
        self.evo_text.pack(side = "left")
        frame1.grid(row = 9, column = 0, sticky = "nsew")
        
        # Legendary Info
        frame_check = Frame(frame_stats_info)
        Checkbutton(frame_check, text = "Legendary", variable = self.legendary).pack(side = "left")
        frame_check.grid(row = 10, column = 0, sticky = "nsew")
        
        #textWrapper(frame_stats_info, self.legendary_resist, "Legendary Resistances", 65, 6, 11, 0)
        frame2 = Frame(frame_stats_info)
        Label(frame2, textvariable = StringVar(frame2, "Legendary Resistances")).pack(side = "top", anchor = "w")
        self.legendary_resist = Text(frame2, width = 65, height = 6, wrap = WORD)
        self.legendary_resist.pack(side = "left")
        frame2.grid(row = 11, column = 0, sticky = "nsew")
        
        #textWrapper(frame_stats_info, self.legendary_trait, "Legendary Traits", 65, 6, 12, 0)
        frame3 = Frame(frame_stats_info)
        Label(frame3, textvariable = StringVar(frame3, "Legendary Traits")).pack(side = "top", anchor = "w")
        self.legendary_trait = Text(frame3, width = 65, height = 6, wrap = WORD)
        self.legendary_trait.pack(side = "left")
        frame3.grid(row = 12, column = 0, sticky = "nsew")
        
        #textWrapper(frame_stats_info, self.legendary_action, "Legendary Actions", 65, 6, 13, 0)
        frame4 = Frame(frame_stats_info)
        Label(frame4, textvariable = StringVar(frame4, "Legendary Actions")).pack(side = "top", anchor = "w")
        self.legendary_action = Text(frame4, width = 65, height = 6, wrap = WORD)
        self.legendary_action.pack(side = "left")
        frame4.grid(row = 13, column = 0, sticky = "nsew")
        
        # Return Main Container
        frame_stats_info.grid(row = 0, column = 0, sticky = "nsew")
        return container
    #END_DEF
    def setFrameData(self, entry):
        global saves, skills
        
        self.redirect.set(entry["Redirect"])
        self.id.set(entry["ID"])
        self.name.set(entry["Name"])
        self.classification.set(entry["Classification"])
        self.sr.set(entry["SR"])
        self.min_level.set(entry["Min_Level"])
        self.hit_dice.set(entry["Hit_Dice"])
        self.movement.set(entry["Movement"])
        self.senses.set(entry["Senses"])
        self.hp.set(entry["Stats"]["HP"])
        self.ac.set(entry["Stats"]["AC"])
        self.str.set(entry["Stats"]["STR"])
        self.dex.set(entry["Stats"]["DEX"])
        self.con.set(entry["Stats"]["CON"])
        self.int.set(entry["Stats"]["INT"])
        self.wis.set(entry["Stats"]["WIS"])
        self.cha.set(entry["Stats"]["CHA"])
        
        for index, save in enumerate(saves):
            if save in entry["Saves"]:
                self.saves[index].set(1)
            else:
                self.saves[index].set(0)
                
        for index, skill in enumerate(skills):
            if skill in entry["Skills"]:
                self.skills[index].set(1)
            else:
                self.skills[index].set(0)
                
        self.evo_text.delete("1.0", END)
        self.evo_text.insert(END, entry["Evolution"])
        
        self.legendary.set(entry["Legendary"])
        
        #self.legendary_resist.set(entry["Legendary_Resistances"])
        self.legendary_resist.delete("1.0", END)
        self.legendary_resist.insert(END, entry["Legendary_Resistances"])
        
        #self.legendary_trait.set(entry["Legendary_Traits"])
        self.legendary_trait.delete("1.0", END)
        self.legendary_trait.insert(END, entry["Legendary_Traits"])
        
        #self.legendary_action.set(entry["Legendary_Actions"])
        self.legendary_action.delete("1.0", END)
        self.legendary_action.insert(END, entry["Legendary_Actions"])
    #END_DEF
    def getFrameData(self, entry):
        global saves, skills
        
        entry["Redirect"] = self.redirect.get()
        entry["ID"] = int(self.id.get())
        entry["Name"] = self.name.get()
        entry["Classification"] = self.classification.get()
        entry["SR"] = self.sr.get()
        entry["Min_Level"] = int(self.min_level.get())
        entry["Hit_Dice"] = self.hit_dice.get()
        entry["Movement"] = self.movement.get()
        entry["Senses"] = self.senses.get()
        entry["Stats"]["HP"] = int(self.hp.get())
        entry["Stats"]["AC"] = int(self.ac.get())
        entry["Stats"]["STR"] = int(self.str.get())
        entry["Stats"]["DEX"] = int(self.dex.get())
        entry["Stats"]["CON"] = int(self.con.get())
        entry["Stats"]["INT"] = int(self.int.get())
        entry["Stats"]["WIS"] = int(self.wis.get())
        entry["Stats"]["CHA"] = int(self.cha.get())
        
        saves_list = []
        for index, save in enumerate(saves):
            if self.saves[index].get() == 1:
                saves_list.append(save)
        entry["Saves"] = saves_list
        
        skills_list = []
        for index, skill in enumerate(skills):
            if self.skills[index].get() == 1:
                skills_list.append(skill)
        entry["Skills"] = skills_list
        
        entry["Evolution"] = self.evo_text.get("1.0", "end-1c")
        entry["Legendary"] = self.legendary.get()
        entry["Legendary_Resistances"] = self.legendary_resist.get("1.0", "end-1c")
        entry["Legendary_Traits"] = self.legendary_trait.get("1.0", "end-1c")
        entry["Legendary_Actions"] = self.legendary_action.get("1.0", "end-1c")
#END_CLASS
class AttackEntryInterface(EntryInterface):
    redirect = StringVar()
    name = StringVar()
    type = StringVar()
    power = tuple(IntVar() for i in range(len(power)))
    time = StringVar()
    duration = StringVar()
    range = StringVar()
    exhaustion = StringVar()
    description = None
    higher_levels = None
    
    combo_redirect = None
    def updateRedirectCombo(self):
        global listbox_entries
        redirect_values = [""]
        redirect_values.extend(listbox_entries.get(0, "end"))
        self.combo_redirect.configure(values = redirect_values)
    #END_DEF
    def createFrame(self, parent):
        global power, type, exhaustion
        
        container = Frame(parent)
        
        frame_redirect = Frame(container)
        frame_name = Frame(container)
        frame_type = Frame(container)
        frame_power = Frame(container)
        frame_time = Frame(container)
        frame_duration = Frame(container)
        frame_range = Frame(container)
        frame_exhaustion = Frame(container)
        frame_description = Frame(container)
        frame_higher_level = Frame(container)
        
        Label(frame_redirect, text = "Redirect: ").pack(side = "left")
        self.combo_redirect = ttk.Combobox(frame_redirect, textvariable = self.redirect, values = [""], width = 40, state = "readonly", postcommand = self.updateRedirectCombo)
        self.combo_redirect.pack(side = "left")
        
        Label(frame_name, text = "Name: ").pack(side = "left")
        Entry(frame_name, textvariable = self.name, width = 50).pack(side = "left")
        
        Label(frame_type, text = "Type: ").pack(side = "left")
        ttk.Combobox(frame_type, textvariable = self.type, values = type, width = 30, state = "readonly").pack(side = "left")
        
        Label(frame_power, text = "Move Power: ").pack(side = "left")
        frame_power_list = Frame(frame_power, borderwidth = 1, relief="solid")
        for i, p in enumerate(power):
            Checkbutton(frame_power_list, text = p, variable = self.power[i]).pack(side = "left", padx = (0, 20))
        frame_power_list.pack(side = "left")
        
        Label(frame_time, text = "Move Time: ").pack(side = "left")
        Entry(frame_time, textvariable = self.time, width = 50).pack(side = "left")
        
        Label(frame_duration, text = "Move Duration: ").pack(side = "left")
        Entry(frame_duration, textvariable = self.duration, width = 50).pack(side = "left")
        
        Label(frame_range, text = "Range: ").pack(side = "left")
        Entry(frame_range, textvariable = self.range, width = 50).pack(side = "left")
        
        Label(frame_exhaustion, text = "Exhaustion Tier: ").pack(side = "left")
        ttk.Combobox(frame_exhaustion, textvariable = self.exhaustion, values = exhaustion, width = 5, state = "readonly").pack(side = "left")
        
        Label(frame_description, text = "Description:").pack(side = "top", anchor = "w")
        self.description = Text(frame_description, width = 65, height = 6, wrap = WORD)
        self.description.pack(side = "top", anchor = "w")
        
        Label(frame_higher_level, text = "Higher Levels:").pack(side = "top", anchor = "w")
        self.higher_levels = Text(frame_higher_level, width = 65, height = 6, wrap = WORD)
        self.higher_levels.pack(side = "top", anchor = "w")
        
        frame_redirect.pack(side = "top", anchor = "w", pady = 3)
        frame_name.pack(side = "top", anchor = "w", pady = 3)
        frame_type.pack(side = "top", anchor = "w", pady = 3)
        frame_power.pack(side = "top", anchor = "w", pady = 3)
        frame_time.pack(side = "top", anchor = "w", pady = 3)
        frame_duration.pack(side = "top", anchor = "w", pady = 3)
        frame_range.pack(side = "top", anchor = "w", pady = 3)
        frame_exhaustion.pack(side = "top", anchor = "w", pady = 3)
        frame_description.pack(side = "top", anchor = "w", pady = 3)
        frame_higher_level.pack(side = "top", anchor = "w", pady = 3)
        
        return container
    #END_DEF
    def setFrameData(self, entry):
        global power
        
        self.redirect.set(entry["Redirect"])
        self.name.set(entry["Name"])
        self.type.set(entry["Type"])
        for i, p in enumerate(power):
            if p in entry["Power"]:
                self.power[i].set(1)
            else:
                self.power[i].set(0)
        #END_FOR
        self.time.set(entry["Time"])
        self.duration.set(entry["Duration"])
        self.range.set(entry["Range"])
        self.exhaustion.set(entry["Exhaustion"])
        
        self.description.delete("1.0", END)
        self.description.insert(END, entry["Description"])
        
        self.higher_levels.delete("1.0", END)
        self.higher_levels.insert(END, entry["Higher_Levels"])
    #END_DEF
    def getFrameData(self, entry):
        global power
        
        entry["Redirect"] = self.redirect.get()
        entry["Name"] = self.name.get()
        entry["Type"] = self.type.get()
        
        power_list = []
        for i, p in enumerate(power):
            if self.power[i].get() == 1:
                power_list.append(p)
        entry["Power"] = power_list
        
        entry["Time"] = self.time.get()
        entry["Duration"] = self.duration.get()
        entry["Range"] = self.range.get()
        entry["Exhaustion"] = self.exhaustion.get()
        entry["Description"] = self.description.get("1.0", "end-1c")
        entry["Higher_Levels"] = self.higher_levels.get("1.0", "end-1c")
#END_CLASS
class AbilityEntryInterface(EntryInterface):
    name = StringVar()
    description = None
    
    def createFrame(self, parent):
        container = Frame(parent)
        
        frame_name = Frame(container)
        frame_description = Frame(container)
        
        Label(frame_name, text = "Name: ").pack(side = "left")
        Entry(frame_name, textvariable = self.name, width = 50).pack(side = "left")
        
        Label(frame_description, text = "Description:").pack(side = "top", anchor = "w")
        self.description = Text(frame_description, width = 65, height = 6, wrap = WORD)
        self.description.pack(side = "top", anchor = "w")
        
        frame_name.pack(side = "top", anchor = "w", pady = 3)
        frame_description.pack(side = "top", anchor = "w", pady = 3)
        
        return container
    #END_DEF
    def setFrameData(self, entry):
        self.name.set(entry["Name"])
        
        self.description.delete("1.0", END)
        self.description.insert(END, entry["Description"])
    #END_DEF
    def getFrameData(self, entry):
        entry["Name"] = self.name.get()
        entry["Description"] = self.description.get("1.0", "end-1c")
#END_CLASS
# TODO!!! Complete interfaces

pokedexInterface = PokedexEntryInterface()
attackdexInterface = AttackEntryInterface()
abilitydexInterface = AbilityEntryInterface()

pokedex_frame = pokedexInterface.createFrame(frame_content)
attackdex_frame = attackdexInterface.createFrame(frame_content)
abilitydex_frame = abilitydexInterface.createFrame(frame_content)

current_content_frame = None
current_interface = None

frame_list = ((pokedex_frame, pokedexInterface),\
              (attackdex_frame, attackdexInterface),\
              (abilitydex_frame, abilitydexInterface))

default_entry_list = (default_pokedex_entry,\
                      default_attack_entry,\
                      default_ability_entry)

def switchContent(database = None, entry = None):
    global database_list, current_content_frame, current_interface, frame_list
    
    if not current_content_frame is None:
        current_content_frame.pack_forget()
        current_content_frame = None
        current_interface = None
    #END_IF
    
    if database in database_list:
        index = database_list.index(database)
        
        current_content_frame = frame_list[index][0]
        current_interface = frame_list[index][1]
        
        current_interface.setFrameData(entry)
        current_content_frame.pack(side = "left", anchor = "n")
    else:
        current_content_frame = None
        current_interface = None
#END_DEF

# Listbox Selection Callback Functions
def rulesetSelectionCallback(event):
    global ruleset_library, listbox_database, listbox_entries,\
           ruleset_listbox_selection_last, database_listbox_selection_last, entry_listbox_selection_last
    
    selection = event.widget.curselection()
    if selection:
        if selection[0] == ruleset_listbox_selection_last:
            return
        #END_IF
        
        ruleset_listbox_selection_last = selection[0]
        database_listbox_selection_last = None
        entry_listbox_selection_last = None
        
        listbox_database.delete(0, "end")
        listbox_entries.delete(0, "end")
        
        ruleset = event.widget.get(selection)
        for key, value in ruleset_library["rulesets"][ruleset].items():
            listbox_database.insert("end", key)
        #END_FOR
        
        switchContent()
#END_DEF
def databaseSelectionCallback(event):
    global ruleset_library, listbox_ruleset, listbox_database, listbox_entries,\
           ruleset_listbox_selection_last, database_listbox_selection_last, entry_listbox_selection_last
    
    selection = event.widget.curselection()
    if selection:
        if selection[0] == database_listbox_selection_last:
            return
        #END_IF
        
        database_listbox_selection_last = selection[0]
        entry_listbox_selection_last = None
        
        listbox_entries.delete(0, "end")
        
        ruleset = listbox_ruleset.get(ruleset_listbox_selection_last)
        database = event.widget.get(selection)
        for key, value in ruleset_library["rulesets"][ruleset][database].items():
            listbox_entries.insert("end", key)
            if ruleset_library["todo"][ruleset][database][key] == 1:
                listbox_entries.itemconfig("end", {"bg": todo_color})
        #END_FOR
        
        switchContent()
#END_DEF
def entrySelectionCallback(event):
    global ruleset_library, listbox_ruleset, listbox_database, listbox_entries,\
           ruleset_listbox_selection_last, database_listbox_selection_last, entry_listbox_selection_last,\
           current_interface
    
    selection = event.widget.curselection()
    if selection:
        if selection[0] == entry_listbox_selection_last:
            return
        #END_IF
        
        entry_listbox_selection_last = selection[0]
        
        ruleset = listbox_ruleset.get(ruleset_listbox_selection_last)
        database = listbox_database.get(database_listbox_selection_last)
        entry = event.widget.get(selection)
        
        switchContent(database, ruleset_library["rulesets"][ruleset][database][entry])
#END_DEF

listbox_ruleset.bind("<<ListboxSelect>>", rulesetSelectionCallback)
listbox_database.bind("<<ListboxSelect>>", databaseSelectionCallback)
listbox_entries.bind("<<ListboxSelect>>", entrySelectionCallback)
        



# Entry Management Functions
def addEntry(ruleset, database, entry_name):
    global ruleset_library, database_list, default_entry_list
    
    ruleset_library["todo"][ruleset][database][entry_name] = 1
    
    database_index = database_list.index(database)
    ruleset_library["rulesets"][ruleset][database][entry_name] = deepcopy(default_entry_list[database_index])
#END_DEF


def fillPokedexAPI(ruleset, database):
    global ruleset_library, listbox_entries, default_evo_text
    
    pokeAPI_data = requests.get("https://pokeapi.co/api/v2/pokemon?limit=100000&offset=0").json()
    count = pokeAPI_data["count"]
    results = pokeAPI_data["results"]
    for i in range(count):
        name = results[i]["name"]
        id = results[i]["url"].split("/")[-2]
        
        if not name in ruleset_library["rulesets"][ruleset][database]:
            addEntry(ruleset, database, name)
            listbox_entries.insert("end", name)
            listbox_entries.itemconfig("end", {"bg": todo_color})
            
            ruleset_library["rulesets"][ruleset][database][name]["Name"] = name.capitalize()
            ruleset_library["rulesets"][ruleset][database][name]["ID"] = id
            ruleset_library["rulesets"][ruleset][database][name]["Evolution"] = default_evo_text.format(name1 = name.capitalize(), name2 = "NAME", lvl = "LVL", asi = "ASI")
#END_DEF
def fillAttackdexAPI(ruleset, database):
    global ruleset_library, listbox_entries
    
    pokeAPI_data = requests.get("https://pokeapi.co/api/v2/move?limit=100000&offset=0").json()
    count = pokeAPI_data["count"]
    results = pokeAPI_data["results"]
    for i in range(count):
        name = results[i]["name"]
        
        if not name in ruleset_library["rulesets"][ruleset][database]:
            addEntry(ruleset, database, name)
            listbox_entries.insert("end", name)
            listbox_entries.itemconfig("end", {"bg": todo_color})
            
            ruleset_library["rulesets"][ruleset][database][name]["Name"] = name.capitalize()
#END_DEF
def fillAbilitydexAPI(ruleset, database):
    global ruleset_library, listbox_entries
    
    pokeAPI_data = requests.get("https://pokeapi.co/api/v2/ability?limit=100000&offset=0").json()
    count = pokeAPI_data["count"]
    results = pokeAPI_data["results"]
    for i in range(count):
        name = results[i]["name"]
        
        if not name in ruleset_library["rulesets"][ruleset][database]:
            addEntry(ruleset, database, name)
            listbox_entries.insert("end", name)
            listbox_entries.itemconfig("end", {"bg": todo_color})
            
            ruleset_library["rulesets"][ruleset][database][name]["Name"] = name.capitalize()
#END_DEF




# Menubar Item Commands
def newRuleset():
    global ruleset_library, listbox_ruleset, default_database_library
    
    win = Toplevel()
    win.grab_set()
    win.wm_title("New Ruleset")
    
    text_label = Label(win, text="Ruleset Name: ")
    text_var = StringVar(win)
    text_entry = Entry(win, textvariable = text_var, width = 40)
    text_entry.focus()
    
    def onOkay(win, text_var):
        global ruleset_library, listbox_ruleset, default_database_library
        
        value = text_var.get()
        if not isValidPathname(value):
            messagebox.showinfo("Warning", '"{0}" is not a valid name.'.format(value))
        elif isDuplicateEntry(value, listbox_ruleset):
            messagebox.showinfo("Warning", '"{0}" already exists.'.format(value))
        else:
            ruleset_library["rulesets"][value] = deepcopy(default_database_library)
            ruleset_library["todo"][value] = deepcopy(default_database_library)
            
            listbox_ruleset.insert("end", value)
            win.destroy()
        #END_IF
    #END_DEF
    
    button_okay = ttk.Button(win, text = "Okay", command = lambda: onOkay(win, text_var))
    button_cancel = ttk.Button(win, text = "Cancel", command = win.destroy)
    
    win.bind("<Return>", lambda event: onOkay(win, text_var))
    
    text_label.pack(side = "left")
    text_entry.pack(side = "left")
    button_okay.pack(anchor = "s")
    button_cancel.pack(anchor = "s")
#END_DEF

def renameRuleset():
    global ruleset_library, listbox_ruleset, listbox_database, listbox_entries,\
           ruleset_listbox_selection_last, database_listbox_selection_last, entry_listbox_selection_last
    
    if listbox_ruleset.index("end") == 0 or len(listbox_ruleset.curselection()) == 0:
        messagebox.showinfo("Info", "Please select the ruleset to be renamed.")
        return
    
    win = Toplevel()
    win.grab_set()
    win.wm_title("Rename Ruleset")
    
    text_label = Label(win, text="Ruleset Name: ")
    text_var = StringVar(win)
    text_entry = Entry(win, textvariable = text_var, width = 40)
    text_entry.focus()
    
    def onOkay(win, text_var):
        global ruleset_library, listbox_ruleset, listbox_database, listbox_entries
        
        value = text_var.get()
        if not isValidPathname(value):
            messagebox.showinfo("Warning", '"{0}" is not a valid name.'.format(value))
        elif isDuplicateEntry(value, listbox_ruleset):
            messagebox.showinfo("Warning", '"{0}" already exists.'.format(value))
        else:
            ruleset_listbox_selection_last = None
            database_listbox_selection_last = None
            entry_listbox_selection_last = None
            
            index = listbox_ruleset.curselection()
            selected_ruleset = listbox_ruleset.get(index)
            ruleset_library["rulesets"][value] = ruleset_library["rulesets"].pop(selected_ruleset)
            ruleset_library["todo"][value] = ruleset_library["todo"].pop(selected_ruleset)
            
            listbox_ruleset.delete(index)
            listbox_ruleset.insert(index, value)
            
            listbox_database.delete(0, "end")
            listbox_entries.delete(0, "end")
            
            switchContent()
            
            win.destroy()
        #END_IF
    #END_DEF
    
    button_okay = ttk.Button(win, text = "Okay", command = lambda: onOkay(win, text_var))
    button_cancel = ttk.Button(win, text = "Cancel", command = win.destroy)
    
    win.bind("<Return>", lambda event: onOkay(win, text_var))
    
    text_label.pack(side = "left")
    text_entry.pack(side = "left")
    button_okay.pack(anchor = "s")
    button_cancel.pack(anchor = "s")
#END_DEF

def deleteRuleset():
    global ruleset_library, listbox_ruleset, listbox_database, listbox_entries,\
           ruleset_listbox_selection_last, database_listbox_selection_last, entry_listbox_selection_last
    
    if listbox_ruleset.index("end") == 0 or len(listbox_ruleset.curselection()) == 0:
        messagebox.showinfo("Info", "Please select the ruleset to be deleted.")
        return
    
    if not messagebox.askokcancel("Confirm", 'Are you sure that you want to delete ruleset "{0}"?'.format(listbox_ruleset.get(listbox_ruleset.curselection()))):
        return
    ruleset_listbox_selection_last = None
    database_listbox_selection_last = None
    entry_listbox_selection_last = None
    
    index = listbox_ruleset.curselection()
    selected_ruleset = listbox_ruleset.get(index)
    ruleset_library["rulesets"].pop(selected_ruleset)
    ruleset_library["todo"].pop(selected_ruleset)
    listbox_ruleset.delete(index)
    
    listbox_database.delete(0, "end")
    listbox_entries.delete(0, "end")
    
    switchContent()
#END_DEF

def saveDatabase():
    global ruleset_library, ruleset_path, ruleset_file, todo_file
    
    active_rulesets = {"Default": "", "Rulesets": {}}
    
    for rs, database in ruleset_library["rulesets"].items():
        if active_rulesets["Default"] == "":
            active_rulesets["Default"] = rs
        active_rulesets["Rulesets"][rs] = rs
        
        dir_path = os.path.join(ruleset_path, rs)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        
        for db, entry_list in database.items():
            db_path = os.path.join(dir_path, db)
            if not os.path.exists(db_path):
                os.makedirs(db_path)
            
            file_name = os.path.join(db_path, db + ".json")
            with open(file_name, "w") as jfile:
                json.dump(entry_list, jfile, indent = 4)
        #END_FOR
    #END_FOR
    
    ar_file_name = os.path.join(ruleset_path, "active_rulesets.json")
    with open(ruleset_file, "w") as jfile:
        json.dump(active_rulesets, jfile, indent = 4)
    
    with open(todo_file, "w") as jfile:
        json.dump(ruleset_library["todo"], jfile, indent = 4)
#END_DEF

def newEntry():
    global ruleset_library, listbox_ruleset, listbox_database, listbox_entries,\
           ruleset_listbox_selection_last, database_listbox_selection_last, entry_listbox_selection_last
    
    if listbox_ruleset.index("end") == 0 or ruleset_listbox_selection_last is None:
        messagebox.showinfo("Info", "Please select a ruleset.")
        return
    
    if listbox_database.index("end") == 0 or database_listbox_selection_last is None:
        messagebox.showinfo("Info", "Please select a database.")
        return
    
    win = Toplevel()
    win.grab_set()
    win.wm_title("New Entry")
    
    text_label = Label(win, text="Entry Name: ")
    text_var = StringVar(win)
    text_entry = Entry(win, textvariable = text_var, width = 40)
    text_entry.focus()
    
    def onOkay(win, text_var):
        global ruleset_library, listbox_ruleset, listbox_database, listbox_entries
        
        value = text_var.get()
        if isDuplicateEntry(value, listbox_entries):
            messagebox.showinfo("Warning", '"{0}" already exists.'.format(value))
        else:
            selected_ruleset = listbox_ruleset.get(ruleset_listbox_selection_last)
            selected_databse = listbox_database.get(database_listbox_selection_last)
            addEntry(selected_ruleset, selected_databse, value)
            
            listbox_entries.insert("end", value)
            listbox_entries.itemconfig("end", {"bg": todo_color})
            win.destroy()
        #END_IF
    #END_DEF
    
    button_okay = ttk.Button(win, text = "Okay", command = lambda: onOkay(win, text_var))
    button_cancel = ttk.Button(win, text = "Cancel", command = win.destroy)
    
    win.bind("<Return>", lambda event: onOkay(win, text_var))
    
    text_label.pack(side = "left")
    text_entry.pack(side = "left")
    button_okay.pack(anchor = "s")
    button_cancel.pack(anchor = "s")
#END_DEF

def fillEntry():
    global ruleset_library, listbox_ruleset, listbox_database, listbox_entries,\
           ruleset_listbox_selection_last, database_listbox_selection_last
    
    if listbox_ruleset.index("end") == 0 or ruleset_listbox_selection_last is None:
        messagebox.showinfo("Info", "Please select a ruleset.")
        return
    
    if listbox_database.index("end") == 0 or database_listbox_selection_last is None:
        messagebox.showinfo("Info", "Please select a database.")
        return
    
    selected_ruleset = listbox_ruleset.get(ruleset_listbox_selection_last)
    selected_database = listbox_database.get(database_listbox_selection_last)
    
    if selected_database == database_list[0]: # Pokedex
        fillPokedexAPI(selected_ruleset, selected_database)
    elif selected_database == database_list[1]: # Attackdex
        fillAttackdexAPI(selected_ruleset, selected_database)
    elif selected_database == database_list[2]: # Abilitydex
        fillAbilitydexAPI(selected_ruleset, selected_database)
    # TODO!!! Behavior for other database types
#END_DEF

def saveEntry():
    global ruleset_library, listbox_ruleset, listbox_database, listbox_entries,\
           ruleset_listbox_selection_last, database_listbox_selection_last, entry_listbox_selection_last,\
           current_interface
    
    if listbox_ruleset.index("end") == 0 or ruleset_listbox_selection_last is None:
        return
    if listbox_database.index("end") == 0 or database_listbox_selection_last is None:
        return
    if listbox_entries.index("end") == 0 or entry_listbox_selection_last is None:
        return
    
    selected_ruleset = listbox_ruleset.get(ruleset_listbox_selection_last)
    selected_databse = listbox_database.get(database_listbox_selection_last)
    selected_entry = listbox_entries.get(entry_listbox_selection_last)
    
    ruleset_library["todo"][selected_ruleset][selected_databse][selected_entry] = 0
    
    listbox_entries.itemconfig(entry_listbox_selection_last, {"bg": "white"})
    
    current_interface.getFrameData(ruleset_library["rulesets"][selected_ruleset][selected_databse][selected_entry])
#END_DEF

def deleteEntry():
    global ruleset_library, listbox_ruleset, listbox_database, listbox_entries,\
           ruleset_listbox_selection_last, database_listbox_selection_last, entry_listbox_selection_last
    
    if listbox_ruleset.index("end") == 0 or ruleset_listbox_selection_last is None:
        messagebox.showinfo("Info", "No entry selected for deletion.")
        return
    if listbox_database.index("end") == 0 or database_listbox_selection_last is None:
        messagebox.showinfo("Info", "No entry selected for deletion.")
        return
    if listbox_entries.index("end") == 0 or entry_listbox_selection_last is None:
        messagebox.showinfo("Info", "No entry selected for deletion.")
        return
    
    if not messagebox.askokcancel("Confirm", 'Are you sure that you want to delete entry "{0}"?'.format(listbox_entries.get(listbox_entries.curselection()))):
        return
    entry_listbox_selection_last = None
    
    index = listbox_entries.curselection()
    selected_entry = listbox_entries.get(index)
    selected_ruleset = listbox_ruleset.get(ruleset_listbox_selection_last)
    selected_database = listbox_database.get(database_listbox_selection_last)
    ruleset_library["rulesets"][selected_ruleset][selected_database].pop(selected_entry)
    ruleset_library["todo"][selected_ruleset][selected_database].pop(selected_entry)
    listbox_entries.delete(index)
    
    switchContent()
#END_DEF

def addToDo():
    global ruleset_library, listbox_ruleset, listbox_database, listbox_entries,\
           ruleset_listbox_selection_last, database_listbox_selection_last, entry_listbox_selection_last,\
           current_interface
    
    if listbox_ruleset.index("end") == 0 or ruleset_listbox_selection_last is None:
        return
    if listbox_database.index("end") == 0 or database_listbox_selection_last is None:
        return
    if listbox_entries.index("end") == 0 or entry_listbox_selection_last is None:
        return
    
    selected_ruleset = listbox_ruleset.get(ruleset_listbox_selection_last)
    selected_databse = listbox_database.get(database_listbox_selection_last)
    selected_entry = listbox_entries.get(entry_listbox_selection_last)
    
    ruleset_library["todo"][selected_ruleset][selected_databse][selected_entry] = 1
    
    listbox_entries.itemconfig(entry_listbox_selection_last, {"bg": todo_color})
#END_DEF

def removeToDo():
    global ruleset_library, listbox_ruleset, listbox_database, listbox_entries,\
           ruleset_listbox_selection_last, database_listbox_selection_last, entry_listbox_selection_last,\
           current_interface
    
    if listbox_ruleset.index("end") == 0 or ruleset_listbox_selection_last is None:
        return
    if listbox_database.index("end") == 0 or database_listbox_selection_last is None:
        return
    if listbox_entries.index("end") == 0 or entry_listbox_selection_last is None:
        return
    
    selected_ruleset = listbox_ruleset.get(ruleset_listbox_selection_last)
    selected_databse = listbox_database.get(database_listbox_selection_last)
    selected_entry = listbox_entries.get(entry_listbox_selection_last)
    
    ruleset_library["todo"][selected_ruleset][selected_databse][selected_entry] = 0
    
    listbox_entries.itemconfig(entry_listbox_selection_last, {"bg": "white"})
#END_DEF

def editToDo():
    global ruleset_library, database_list
    
    win = Toplevel()
    win.grab_set()
    win.wm_title("Edit To-Do List")
    win.resizable(False, False)
    
    selected_ruleset = StringVar()
    selected_database = StringVar()
    
    frame_combos = Frame(win)
    frame_combos_rule = Frame(frame_combos)
    frame_combos_data = Frame(frame_combos)
    
    frame_lists = Frame(win)
    frame_buttons = Frame(win)
    
    frame_list1 = Frame(frame_lists)
    frame_list_buttons = Frame(frame_lists)
    frame_list2 = Frame(frame_lists)
    
    scrollbar_finished = Scrollbar(frame_list1)
    scrollbar_todo = Scrollbar(frame_list2)
    list_finished = Listbox(frame_list1, selectmode = "multiple", yscrollcommand = scrollbar_finished.set, width = 35, height = 35)
    list_todo = Listbox(frame_list2, selectmode = "multiple", yscrollcommand = scrollbar_todo.set, width = 35, height = 35)
    
    combo_ruleset = ttk.Combobox(frame_combos_rule, textvariable = selected_ruleset, values = [k  for  k in  ruleset_library["rulesets"].keys()], state="readonly")
    combo_database = ttk.Combobox(frame_combos_data, textvariable = selected_database, values = database_list, state="readonly")
    
    
    def comboSelect(event):
        global ruleset_library
        rs = selected_ruleset.get()
        db = selected_database.get()
        if (rs == "") or (db == ""):
            return
        list_todo.delete(0, "end")
        list_finished.delete(0, "end")
        for key in ruleset_library["rulesets"][rs][db].keys():
            if ruleset_library["todo"][rs][db][key] == 1:
                list_todo.insert("end", key)
            else:
                list_finished.insert("end", key)
    #END_DEF
    def todoAll():
        for i, entry in enumerate(list_finished.get(0, END)):
            list_todo.insert("end", entry)
        list_finished.delete(0, END)
    #END_DEF
    def todoSet():
        for i in list_finished.curselection()[::-1]:
            list_todo.insert("end", list_finished.get(i))
            list_finished.delete(i)
    #END_DEF
    def finishedSet():
        for i in list_todo.curselection()[::-1]:
            list_finished.insert("end", list_todo.get(i))
            list_todo.delete(i)
    #END_DEF
    def finishedAll():
        for i, entry in enumerate(list_todo.get(0, END)):
            list_finished.insert("end", entry)
        list_todo.delete(0, END)
        print(ruleset_listbox_selection_last)
        print(database_listbox_selection_last)
        print(entry_listbox_selection_last)
    #END_DEF
    def applyChanges(close = False):
        global ruleset_library, ruleset_listbox_selection_last, database_listbox_selection_last,\
               listbox_ruleset, listbox_database, listbox_entries
        rs = selected_ruleset.get()
        db = selected_database.get()
        for i, entry in enumerate(list_finished.get(0, END)):
            ruleset_library["todo"][rs][db][entry] = 0
            if (rs == listbox_ruleset.get(ruleset_listbox_selection_last)) and (db == listbox_database.get(database_listbox_selection_last)):
                listbox_entries.itemconfig(listbox_entries.get(0, END).index(entry), {"bg": "white"})
        for i, entry in enumerate(list_todo.get(0, END)):
            ruleset_library["todo"][rs][db][entry] = 1
            if (rs == listbox_ruleset.get(ruleset_listbox_selection_last)) and (db == listbox_database.get(database_listbox_selection_last)):
                listbox_entries.itemconfig(listbox_entries.get(0, END).index(entry), {"bg": todo_color})
        if close:
            win.destroy()
    #END_DEF
    combo_ruleset.bind("<<ComboboxSelected>>", comboSelect)
    combo_database.bind("<<ComboboxSelected>>", comboSelect)
    
    
    
    button_todo_all = ttk.Button(frame_list_buttons, text = "-->", command = todoAll)
    button_todo_sel = ttk.Button(frame_list_buttons, text = ">", command = todoSet)
    button_fin_sel = ttk.Button(frame_list_buttons, text = "<", command = finishedSet)
    button_fin_all = ttk.Button(frame_list_buttons, text = "<--", command = finishedAll)
    
    button_apply = ttk.Button(frame_buttons, text = "Apply", command = lambda: applyChanges(False))
    button_ok = ttk.Button(frame_buttons, text = "Okay", command = lambda: applyChanges(True))
    button_cancel = ttk.Button(frame_buttons, text = "Cancel", command = lambda: win.destroy())
    
    label_ruleset = Label(frame_combos_rule, text = "Ruleset: ")
    label_database = Label(frame_combos_data, text = "Database: ")
    
    
    
    label_ruleset.pack(side = "left", anchor = "n")
    combo_ruleset.pack(side = "right", anchor = "n")
    label_database.pack(side = "left", anchor = "n")
    combo_database.pack(side = "right", anchor = "n")
    
    frame_combos_rule.pack(side = "top", anchor = "n")
    frame_combos_data.pack(side = "top", anchor = "n")
    
    Label(frame_list1, text = "Completed").pack(side = "top", anchor = "n")
    list_finished.pack(side = "left", anchor = "n")
    Label(frame_list2, text = "To-Do").pack(side = "top", anchor = "n")
    list_todo.pack(side = "left", anchor = "n")
    
    button_todo_all.pack(side = "top", anchor = "n")
    button_todo_sel.pack(side = "top", anchor = "n")
    button_fin_sel.pack(side = "top", anchor = "n")
    button_fin_all.pack(side = "top", anchor = "n")
    
    
    frame_list1.pack(side = "left", anchor = "n")
    scrollbar_finished.pack(side = "right", fill = Y)
    scrollbar_finished.config(command = list_finished.yview)
    frame_list_buttons.pack(side = "left", anchor = "e")
    frame_list2.pack(side = "left", anchor = "n")
    scrollbar_todo.pack(side = "right", fill = Y)
    scrollbar_todo.config(command = list_todo.yview)
    
    button_cancel.pack(side = "right", anchor = "e")
    button_ok.pack(side = "right", anchor = "e")
    button_apply.pack(side = "right" , anchor = "e")
    
    frame_combos.pack(side = "top", anchor = "n")
    frame_lists.pack(side = "top", anchor = "n")
    frame_buttons.pack(side = "top", anchor = "n")
#END_DEF

# Configure Menubar Items
def createMenubar(root):
    # Create Menu
    menubar = Menu(root)
    
    # Add File Menu Options
    file = Menu(menubar, tearoff = 0)
    file.add_command(label = "New Ruleset", command = newRuleset)
    file.add_command(label = "Rename Ruleset", command = renameRuleset)
    file.add_command(label = "Delete Ruleset", command = deleteRuleset)
    file.add_command(label = "Save", command = saveDatabase, accelerator = "Alt+S")
    file.add_separator()
    file.add_command(label = "Exit", command = None, accelerator = "Ctrl+Q") # TODO!!! Add quit function
    menubar.add_cascade(label = "File", menu = file)
    
    # Add Database Menu Options
    database = Menu(menubar, tearoff = 0)
    database.add_command(label = "New Entry", command = newEntry)
    database.add_command(label = "Save Entry", command = saveEntry, accelerator = "Ctrl+S")
    database.add_command(label = "Delete Entry", command = deleteEntry)
    database.add_separator()
    database.add_command(label = "API Entry Fill", command = fillEntry)
    database.add_separator()
    database.add_command(label = "Add To To-Do List", command = addToDo, accelerator = "Ctrl+T")
    database.add_command(label = "Remove From To-Do List", command = removeToDo, accelerator = "Ctrl+R")
    database.add_command(label = "Edit To-Do List", command = editToDo)
    database.add_separator()
    database.add_command(label = "Audit Current Database", command = None) # TODO!!! Add audit function
    database.add_command(label = "Audit Current Ruleset", command = None)
    database.add_command(label = "Audit Everything", command = None)
    menubar.add_cascade(label = "Database", menu = database)
    
    # Add Help Menu Options
    help_ = Menu(menubar, tearoff = 0)
    help_.add_command(label = "About", command = None)
    menubar.add_cascade(label = "Help", menu = help_) # TODO!!! Add help and about
    
    return menubar
#END_DEF

# Configure Window
root.title("Scarlet League PHB Database Editor")
root.geometry('1050x670')
root.resizable(False, False)
root.config(menu = createMenubar(root))

root.bind("<Control-s>", lambda event: saveEntry())
root.bind("<Control-t>", lambda event: addToDo())
root.bind("<Control-r>", lambda event: removeToDo())
root.bind("<Alt-s>", lambda event: saveDatabase())

# Configure Main Layout
frame_library.pack(side = LEFT, fill = Y)
frame_entries.pack(side = LEFT, fill = Y)
frame_content.pack(side = LEFT, fill = BOTH, expand = True)

# Configure Library Grid Layout
frame_library.grid_columnconfigure(0, weight = 1)
frame_library.grid_rowconfigure(0, weight = 1)
frame_library.grid_rowconfigure(1, weight = 1)

frame_ruleset.grid(row = 0, column = 0, sticky = "nsew")
frame_database.grid(row = 1, column = 0, sticky = "nsew")

# Configure Ruleset Listbox
scrollbar_ruleset.pack(side = RIGHT, fill = Y)
listbox_ruleset.pack(side = TOP, fill = Y, expand = True)
scrollbar_ruleset.config(command = listbox_ruleset.yview)

# Configure Database Listbox
scrollbar_database.pack(side = RIGHT, fill = Y)
listbox_database.pack(side = TOP, fill = Y, expand = True)
scrollbar_database.config(command = listbox_database.yview)

# Configure Entry Listbox
scrollbar_entries.pack(side = RIGHT, fill = Y)
listbox_entries.pack(side = TOP, fill = Y, expand = True)
scrollbar_entries.config(command = listbox_entries.yview)



# Run Main Loop
root.mainloop()