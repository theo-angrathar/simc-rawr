#!/usr/bin/python
import Tkinter, tkFileDialog, shutil, os, subprocess, sys
import rawr2simc

tk_root = None

config = {}
config["tmpdir"] = "tmp"
config["default_config_file"] = "simc_rawr.conf"

""" parse the config file """
def parse_config():
  # TODO: parse_config should automatically pass on stuff to simc without me checking for it (i.e. I should automatically accept all options taken by simc)
  try:
    config["config_file"] = sys.argv[1]
  except IndexError:
    print("Couldn't read config file, trying the default config file (" + config["default_config_file"] + ")")
    config["config_file"] = config["default_config_file"]
  def get_boolean_entry(entry):
    if config[entry].lower() not in ["0", "1", "true", "false", "t", "f", "yes", "no", "y", "n"]:
      raise ValueError("could not recognize config entry's value " + config[entry] + " as a boolean")
    return config[entry].lower() in ["1", "true", "t", "yes", "y"]
  def get_integer_entry(entry): # todo support all numeric types, will need to be careful to check for float == int (check error bound? is there a pythonic way to do it?)
    try:
      num = int(config[entry])
      if num > 0:
        return num
    except:
      pass
    raise ValueError("could not recognize config entry's value " + config[entry] + " as a positive integer")
    #raise ValueError("could not recognize config entry's value " + config[entry] + " as a positive number")
   
  # read in key=value pairs in the config
  with open(config["config_file"], "r") as conf:
    for line in conf:
      # config comments start with "#"
      stripped = line.lstrip()
      if len(stripped) == 0 or stripped[0] == '#':
        continue
      try:
        if line is not None:
          [key, value] = [e.strip() for e in line.split("=") if e.strip() != ""]
          config[key] = value.strip()
      except:
        #print("parsing config line \"" + str(line).rstrip("\n").rstrip("\r") + "\" failed")
        pass
  try:
    # handle the entries here, prettying them up, etc. and checking for existence
    try:
      config["simc_dir"] = os.path.normpath(config["simc_dir"])
    except:
      config["simc_dir"] = os.path.normpath("..")
    try:
      config["rawr_char_dir"] = os.path.normpath(config["rawr_char_dir"])
    except:
      config["rawr_char_dir"] = os.path.normpath(".")
      
    # optionals (i.e. entries that have defaults)
    try:
      config["calculate_scale_factors"] = get_boolean_entry("calculate_scale_factors")
    except KeyError:
      config["calculate_scale_factors"] = False
    try:
      config["normalization_stat"]
    except KeyError:
      config["normalization_stat"] = None
    try:
      config["single_line_print"] = get_boolean_entry("single_line_print")
    except KeyError:
      config["single_line_print"] = True
    try:
      config["full_buffs"] = get_boolean_entry("full_buffs")
    except KeyError:
      config["full_buffs"] = True
    try:
      config["iterations"] = get_integer_entry("iterations")
    except KeyError:
      config["iterations"] = 10000

  except:
    raise #KeyError("missing required config entries or bad entry format")

""" return list of selected files from file dialog """
def get_rawr_files():
  tk_root = Tkinter.Tk()
  tk_root.withdraw()
  filenames = tkFileDialog.askopenfilenames(title="Choose Rawr character files", initialdir=config["rawr_char_dir"])
  if filenames == None or len(filenames) == 0:
    print("no files specified or couldn't open a file")
    sys.exit(1)
  return tk_root.tk.splitlist(filenames)
    
""" main function """
def do_simc():
  def exit_with_cleanup(rc):
    #shutil.remove("simc_cache.dat")
    exit(rc)
  
  parse_config()
  filenames = get_rawr_files()

  # create tmp folder
  try:
  #  shutil.rmtree(config["tmpdir"])
    os.mkdir(config["tmpdir"])
  except:
    pass
  
  # maps original filename to file in working dir, except I use a hack to make it easier to keep
  # the dict in the original order - the key is a tuple (idx, original_filename) where idx is the
  # index in the order of the original filename - so to get the "real" key, use the second element of
  # the tuple, but the dictionary is iterated and accessed through the whole tuple (so the accessor
  # of the dict must have kept a record of the order in some way to access a random element)
  filenames_map = {}
  index = 1
  for name in filenames:
    filenames_map[(index, name)] = os.path.join(config["tmpdir"], str(index) + ".xml")
    shutil.copy(name, filenames_map[(index, name)])
    index += 1
  
  #try:
  #  os.rmtree(config["tmpdir"])
  #except:
  #  pass
  def get_char_class_spec(lines):
    for line in lines:
      line = line.strip().lower()
      for st in ["spirit_wolf", "stormstrike", "shamanistic_rage", "lava_lash"]:
        if line.startswith("actions+=/" + st):
          return ("shaman", "enh")
      for st in ["lava_burst", "totem_of_wrath", "elemental_mastery", "thunderstorm"]:
        if line.startswith("actions+=/" + st):
          return ("shaman", "ele")
      for st in ["mortal_strike", "bladestorm"]:#, "sweeping_strikes"]:
        if line.startswith("actions+=/" + st):
          return ("warrior", "arms")
      for st in ["death_wish", "bloodthirst"]:
        if line.startswith("actions+=/" + st):
          return ("warrior", "fury")
      for st in ["frostbolt", "deep_freeze", "water_elemental"]:#, "cold_snap"]:
        if line.startswith("actions+=/" + st):
          return ("mage", "frost")
      for st in ["fire_ball", "frostfire_bolt", "combustion", "living_bomb", "pyroblast,if=buff.hot_streak.react"]:#, "scorch"]:
        if line.startswith("actions+=/" + st):
          return ("mage", "fire")
      for st in ["arcane_barrage", "arcane_power", "arcane_blast", "arcane_missiles"]:
        if line.startswith("actions+=/" + st):
          return ("mage", "arcane")
      for st in ["haunt", "unstable_affliction"]:
        if line.startswith("actions+=/" + st):
          return ("warlock", "affli")
      for st in ["metamorphosis", "soul_fire", "demonic_empowerment"]:
        if line.startswith("actions+=/" + st):
          return ("warlock", "demo")
      for st in ["conflagrate", "chaos_bolt", "shadowfury"]:
        if line.startswith("actions+=/" + st):
          return ("warlock", "destro")
      for st in ["howling_blast", "frost_strike", "hungering_cold"]:#, "obliterate"]
        if line.startswith("actions+=/" + st):
          return ("deathknight", "frost")
      for st in ["summon_gargoyle", "scourge_strike", "bone_shield"]:
        if line.startswith("actions+=/" + st):
          return ("deathknight", "unholy")
      for st in ["dancing_rune_weapon", "heart_strike", "vampiric_blood", "hysteria"]:
        if line.startswith("actions+=/" + st):
          return ("deathknight", "blood")
      for st in ["shred", "rip", "mangle", "rake", "savage_roar", "berserk", "ferocious_bite"]:
        if line.startswith("actions+=/" + st):
          return ("druid", "feral")
      for st in ["moonfire", "starfire", "wrath", "starfall", "force_of_nature", "typhoon"]:
        if line.startswith("actions+=/" + st):
          return ("druid", "balance")
      for st in ["chimera_shot", "silencing_shot", "trueshot_aura"]:
        if line.startswith("actions+=/" + st):
          return ("hunter", "mm")
      for st in ["the_beast_within", "beast_within", "bestial_wrath"]:
        if line.startswith("actions+=/" + st):
          return ("hunter", "bm")
      for st in ["explosive_shot", "black_arrow", "wyvern_sting"]:
        if line.startswith("actions+=/" + st):
          return ("hunter", "survival")
      for st in ["killing_spree", "adrenaline_rush"]:
        if line.startswith("actions+=/" + st):
          return ("rogue", "combat")
      for st in ["mutilate", "hunger_for_blood"]:#, "envenom"]
        if line.startswith("actions+=/" + st):
          return ("rogue", "assa")
      for st in ["shadow_dance", "shadowstep", "premeditation"]:#, "hemorrhage"]
        if line.startswith("actions+=/" + st):
          return ("rogue", "sub")
      if line.startswith("paladin="):
          return ("paladin", "ret")
      elif line.startswith("priest="):
          return ("priest", "shadow")
    for line in lines:
      for c in ["warrior", "paladin", "priest", "mage", "warlock", "deathknight", "druid", "shaman", "hunter", "rogue"]:
        if line.startswith(c + "="):
          return (c, None) # default when spec detection failed, must do 2nd pass or will return before others
          
  def get_default_normalization_stat(lines):
    (char_class, char_spec) = get_char_class_spec(lines)
    stat = None
    if char_class in ["warrior", "deathknight", "paladin"]:
      stat = "str"
    elif char_class in ["mage", "warlock", "priest"]:
      stat = "sp"
    elif char_class == "shaman":
      if char_spec == "enh":
        stat = "ap"
      else:
        stat = "sp"
    elif char_class in ["hunter", "rogue"]:
      stat = "ap"
    elif char_class == "druid":
      if char_spec == "feral":
        stat = "ap"
      else:
        stat = "sp"
    return stat

  simc_exe = os.path.join(config["simc_dir"], "simc.exe")
  for name_tuple in sorted(filenames_map):
    args = [simc_exe, "rawr=" + filenames_map[name_tuple]]
    
    # First, generate the intermediate simc configuration file
    new_temp_simc_config_fn = filenames_map[name_tuple] + ".simc"
    temp_simc_config_fn = new_temp_simc_config_fn + "_tmp"
    args.append("save=" + temp_simc_config_fn)
    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    [out, err] = p.communicate()
    if err:
      print("simc returned an error:")
      print(err)
      exit_with_cleanup(1)
    
    # Now add in the rawr item stats converted to simc format to the end of that simc char
    # config file, replacing any lines that were already there

    new_items_str = rawr2simc.convert_char_items(filenames_map[name_tuple]) + "\n"
    new_items_lines = [line for line in new_items_str.split("\n") if len(line.strip()) > 0]
    new_items_map = {}
    for line in new_items_lines:
      new_items_map[line.split("=")[0].lower()] = line
    
    new_file_lines = [] # Read the whole simc config file to memory, they should be small
    with open(temp_simc_config_fn, "r") as f:
      for line in f:
        if len(line.strip()) > 0:
          if line.lstrip()[0] == "#":
            continue
        header = line.split("=")[0].lower()
        if header in new_items_map:
          new_file_lines.append(new_items_map[header])
        else:
          new_file_lines.append(line)
    
    # Remove the one grabbed from WoWhead now that we have the correct stats from Rawr's cache
    os.remove(temp_simc_config_fn)
    
    # Write the new one
    with open(new_temp_simc_config_fn, "w+") as f:
      for line in new_file_lines:
        f.write(line.strip() + "\n")
    
    # Now, do the simulation
    args = [simc_exe, new_temp_simc_config_fn]
    if config["calculate_scale_factors"]:
      args.append("calculate_scale_factors=1")
    if config["full_buffs"]:
      args.append("optimal_raid=1")
    if config["iterations"]:
      args.append("iterations=" + str(config["iterations"]))
    p = subprocess.Popen(args, stdout=subprocess.PIPE)

    print("Running simc on " + os.path.basename(name_tuple[1]) + "..." + os.linesep)
    [out, err] = p.communicate()
    if err:
      print("simc returned an error:")
      print(err)
      exit_with_cleanup(1)
    else:
      dps_line = None
      stat_weights_line = None
      for line in out.split("\n"):
        if "DPS" in line and "Error" in line:
          dps_line = line
        elif "Weights" in line:
          stat_weights_line = line
        bad_conf_str = ""
        if "unknown" in line and "token" in line:
          bad_conf_str += line.strip() + "\n"
        if "Unable to initialize" in line:
          bad_conf_str += line.strip()
        print bad_conf_str,

      dps = dps_line.split("Error")[0].split(":")[1].strip()
      # Print stat weights in descending sorted order, so since the dictionary is 1-1, use the weight as the key
      # get a bunch of [weight, stat] pairs, and record the value of spellpower so we can normalize it
      print_string = ""
      indent = "    "
      if config["single_line_print"]:
        print_string += "DPS: " + dps
      else:
        print_string += "DPS: " + os.linesep + indent + dps
      
      if config["calculate_scale_factors"]:
        # Figure out a good default normalization stat if we have none read in from config
        #if not config["normalization_stat"]: # TEMP: got rid of ability to specify stat completely (this if guarded only the line config["normalization_stat"] = get_default_normalization_stat(new_file_lines) )
        config["normalization_stat"] = get_default_normalization_stat(new_file_lines)

        stat_weights = {}
        normalization_weight = None
        entries = stat_weights_line.split(":")[1].split()

        for i in range(len(entries)):
          entries[i] = [e.strip() for e in entries[i].split("=") if e.strip() != ""]
          if entries[i][0].lower() == config["normalization_stat"].lower():
            normalization_weight = float(entries[i][1])
            
        try:
          for entry in entries:
            stat = entry[0]
            weight = round(float(entry[1])/normalization_weight, 2)
            stat_weights[weight] = stat
          if config["single_line_print"]:
            print_string += ", Stat weights: {" + ", ".join([stat_weights[w] + "=" + str(w) for w in sorted(stat_weights, reverse=True)]) + "}"
          else:
            print_string += "\nStat weights:\n"
            print_string += "\n".join([indent + stat_weights[weight] + "=" + str(weight) for weight in sorted(stat_weights, reverse=True)])
        except TypeError:
          raise ValueError
      
      print print_string.strip()
      print "====================="
      
  print("")
  raw_input("Finished. Press any key to exit..." + os.linesep)
  exit_with_cleanup(0)

if __name__ == "__main__":
  try:
    do_simc()
  except Exception as e:
    raw_input("SimC Rawr launcher encountered an error")
    
