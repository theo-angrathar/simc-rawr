from bs4 import BeautifulSoup
import string, os.path, sys

# globals
item_cache_base_dir = "items"
enchant_cache_base_dir = "enchants"


"""
Converts a stat name as written in a Rawr XML file to one
readable by a SimCraft configuration file
"""
def rawr2simc_string(name):
  name = str(name).lower()
  d = {\
    "armor" : "armor", \
    "hasterating" : "haste", \
    "critrating" : "crit", \
    "hitrating" : "hit", \
    "intellect" : "int", \
    "spirit" : "spi", \
    "spellpower" : "sp", \
    "stamina" : "sta", \
    #"runic_power" : "runic", \
    
    "bonusarmor" : "barmor", \
    "strength" : "str", \
    "agility" : "agi", \
    "attackpower" : "ap", \
    "expertiserating" : "exp", \
    "armorpenetrationrating" : "arpen", \
    "defenserating" : "def", \
    "dodgerating" : "dodge", \
    "parryrating" : "parry", \
    "blockvalue" : "blockv", \
    "blockrating" : "blockr", \
    # todo feral attack power?
    "manarestore" : "mana", \
    "rangedcritrating" : "crit", \
    
    # todo dunno if these should be the same or just handle these
    # conversions manually, separately for each trinket that needs it
    # 
    # healingspellhit definitely overapproximation - should work only on
    # healing spells
    "damagespellcast" : "onspellcast", \
    "damagespellhit" : "onspelldamage", \
    "dottick" : "onspelltickdamage", \
    "damagedone" : "onattackhit", \
    "physicalhit" : "onattackhit", \
    "meleehit" : "onattackhit", \
    "physicalcrit" : "onattackcrit", \
    "spellcast" : "onspellcast", \
    "healingspellhit" : "onspellcast", \
    
    "chance" : "%", \
    "duration" : "dur", \
    "cooldown" : "cd", \
    "maxstack" : "stack", \
    
    "wrist" : "wrists", \
    "mainhand" : "main_hand", \
    "offhand" : "off_hand", \
    
    "fistweapon" : "fist", \
    "twohandaxe" : "axe2h", \
    "onehandaxe" : "axe", \
    "twohandmace" : "mace2h", \
    "onehandmace" : "mace", \
    "onehandsword" : "sword", \
    "twohandsword" : "sword2h", \
    
    "mindamage" : "min", \
    "maxdamage" : "max", \
    "speed" : "speed" \
    }
  try:
    return d[name]
  except:
    # if meta
    if ("earthsiege" in name or "skyflare" in name or "unstable" or "skyfire" or "earthstorm" or "earthshatter" or "starflare") and "diamond" in name: # possible false posititves
      return "_".join(name.split(" ")[:-1])
    return str(name).replace("'", "").replace("-", "").replace(":", "").replace(",", "").replace(" ", "_")

def is_weapon(type_str):
  return type_str.strip().lower() in \
    ["twohandsword", "onehandsword", "onehandaxe", "twohandaxe", "onehandmace", \
    "twohandmace", "wand", "fistweapon", "staff", "dagger", "polearm", "gun", "bow", "crossbow"] or \
    type_str.strip().lower() in \
    ["fist", "axe", "sword", "mace", "axe2h", "sword2h", "mace2h"]
# def is_armor(type_str):
  # return type_str.strip().lower() != "none" and not is_weapon(type_str)

def is_projectile(type_str):
  return type_str.strip().lower() in ["bullet", "arrow", "projectile"]

def get_node_stats(node, mode="item"):
  if type(node) == int:
    node = str(node)
  if type(node) == str:
    if mode == "enchant":
      path = os.path.join(enchant_cache_base_dir, str(node))
    else: # else assume it's item
      path = os.path.join(item_cache_base_dir, str(node))
    with open(path + ".xml", "r") as f:
      node = BeautifulSoup(f)
      return get_node_stats_helper(node)
  else:
    raise ValueError("'Mode' argument must be \"item\" or \"enchant\"")
  return get_node_stats_helper(node)

def get_node_stats_helper(node):
  d = {}
  try:
    d["itemlevel"] = rawr2simc_string(node.itemlevel.string)
  except:
    pass
  try:
    d["slot"] = rawr2simc_string(node.slot.string)
  except:
    pass
  try:
    d["type"] = rawr2simc_string(node.find("type").string)
    if is_weapon(d["type"]):
      d["min"] = rawr2simc_string(node.mindamage.string)
      d["max"] = rawr2simc_string(node.maxdamage.string)
      d["speed"] = rawr2simc_string(node.speed.string)
    elif is_projectile(d["type"]):
      d["min"] = rawr2simc_string(node.mindamage.string)
      d["max"] = rawr2simc_string(node.maxdamage.string)
  except:
    pass
  try:
    d["itemname"] = rawr2simc_string(node.find("name").string)
  except:
    pass
  for i in range(1, 3):
    try:
      d["socketcolor" + str(i)] = rawr2simc_string(str(node.find("socketcolor" + str(i)).string))
    except:
      pass
  try:
    d["socketbonus"] = {rawr2simc_string(node.socketbonus.contents[1].name) : str(node.socketbonus.contents[1].string)}
  except:
    pass
  for stat in [s for s in node.stats.contents if len(str(s).strip()) > 0 and \
               s.name.strip().lower() not in ["specialeffectcount"]]:
    if str(stat.name).strip().lower() == "specialeffects":
      d["specialeffects"] = []
      for special in [s for s in stat.contents if len(str(s).strip()) > 0]:
        special_stats = {}
        for s in [e for e in special.contents if len(str(e).strip().lower()) > 0 and \
                  str(e.name).strip().lower() != "stats"]:
          try:
            if int(str(s.string)) != 0 and float(str(s.string)) != 0.0:
              special_stats[rawr2simc_string(str(s.name).strip().lower())] = \
                      rawr2simc_string(str(s.string).strip().lower())
          except:
              special_stats[rawr2simc_string(str(s.name).strip().lower())] = \
                      rawr2simc_string(str(s.string).strip().lower())
        special_stats["stats"] = get_node_stats_helper(special)
        d["specialeffects"].append(special_stats)
    else:
      try:
        if int(str(stat.string)) != 0 and float(str(stat.string)) != 0.0:
          d[rawr2simc_string(stat.name)] = str(stat.string)
      except:
        d[rawr2simc_string(stat.name)] = str(stat.string)
  return d

def stats_dict_to_string(d):
  stats_str = ""
  # some are fake stats used by me internally, some aren't modelled by simc
  # - e.g. movementspeed/tuskarr's vitality
  stats_str = "_".join([d[stat_name] + stat_name for stat_name in d if stat_name not in \
   ["specialeffects", "itemname", "slot", "socketbonus", "movementspeed", "socketcolor1", \
    "socketcolor2", "socketcolor3", "heroic", "itemlevel", "type", "min", "max", "speed", "resilience"] and "resistance" not in stat_name])
  try:
    if d["slot"] == "meta":
      stats_str = d["itemname"]
    # elif is_projectile(d["slot"]):
      # print str((int(d["min"]) + int(d["max"]))/2.0)
      # print "LMFAO!!!!"
      # return "ammo_dps=" + str((int(d["min"]) + int(d["max"]))/2.0) # return - no sfx for projectiles
  except:
    pass
  sfx_str = ""
  try:
    if d["itemname"] not in ["darkmoon_card_greatness", "nitro_boosts"]: # hack, easier to handle here than later
      for sfx in d["specialeffects"]:
        sfx_str += ",equip="
        try:
          if rawr2simc_string(sfx["trigger"]) != "use":
            sfx_str += sfx["trigger"] + "_"
          del sfx["trigger"]
        except KeyError:
          pass
        try:
          del sfx["heroic"]
        except KeyError:
          pass
        try:
          for stat in sfx["stats"]:
            sfx_str += sfx["stats"][stat] + stat + "_"
          del sfx["stats"]
        except KeyError:
          pass
        try: # !!!!!! TODO PROBABLY NOT sfx[...] FOR THESE... PROBABLY node[...] OR WHATEVS
          del sfx["itemname"] # ONLY IF NOT META??
        except:
          pass
        try:
          del sfx["slot"] # slot also means socket color - no need in final string
        except:
          pass
        try:
          del sfx["socketbonus"]
        except:
          pass
        for s in sfx:
          if s == "%":
            sfx_probability = int(round(float(sfx[s])*100))
            if sfx_probability != 100:
              sfx_str += str(sfx_probability) + s + "_" # could raise error, or possibly round incorrectly
          elif not ((s == "stack" and sfx[s] == "1") or (s == "cd" and sfx[s] == "0")):
            sfx_str += sfx[s] + s + "_"
        sfx_str = sfx_str[:-1]
  # TODO hopefully stat order doesn't matter - i.e. 45cd_3stack = 3stack_45cd
  except KeyError:
    pass
  try:
    if is_weapon(d["type"]) and rawr2simc_string(d["type"]) != "wand":
      stats_str += ",weapon=" + rawr2simc_string(d["type"]) + "_" + \
        d["speed"] + "speed_" + d["min"] + "min_" + d["max"] + "max"
  except:
    pass
  if d["slot"] not in ["meta"]:
    stats_str += sfx_str
  return stats_str

def is_gem_matching_socket(gem_color, socket_color):
  if gem_color == "prismatic":
    return True
  if socket_color == "blue":
    return gem_color in ["purple", "blue", "green"]
  elif socket_color == "red":
    return gem_color in ["red", "orange", "purple"]
  elif socket_color == "yellow":
    return gem_color in ["yellow", "green", "orange"]
  raise ValueError("incorrect socket or gem name")

def convert_char_items(fn):
  char_str = ""
  with open(fn, "r") as f:
    item_slots = ["head", "neck", "shoulders", "back", "chest", "wrist", "hands", "waist", \
                  "legs", "feet", "finger1", "finger2", "trinket1", "trinket2", "mainhand", \
                  "offhand", "ranged", "projectile"]
    xml = BeautifulSoup(f)
    for slot in item_slots:
      is_socket_matched = True # can become false if any socket doesn't match
      if not xml.find(slot): # if no item equipped in that slot (e.g. no offhand when wearing 2H)
        continue
      rawr_item_str = str(xml.find(slot).string).split(".")
      item_id = rawr_item_str[0]
      item = get_node_stats(item_id)
      item_name = rawr2simc_string(item["itemname"])
      
      if is_projectile(item["slot"]): # bit of a hack
        char_str += "ammo_dps=" + str((int(item["min"]) + int(item["max"]))/2.0) + "\n"
        continue
      else:
        item_str = rawr2simc_string(slot) + "=" + item_name
      
      
      # TODO add all totems/idols/librams/etc that are included in the simcraft
      # models as special items
      if item_name not in \
         ["idol_of_the_lunar_eclipse", "idol_of_lunar_fury", \
          "idol_of_steadfast_renewal", "idol_of_terror", \
          "idol_of_the_corruptor", "idol_of_the_crying_wind", \
          "idol_of_mutilation", "idol_of_the_raven_goddess", \
          "idol_of_the_ravenous_beast", "idol_of_the_shooting_star", \
          "idol_of_the_unseen_moon", "idol_of_worship", \
          "idol_of_the_crying_moon", "idol_of_awakening", \
          "idol_of_flaring_growth", "idol_of_lush_moss", \
          "idol_of_the_black_willow", "idol_of_the_flourishing_life", \
          "harolds_rejuvenating_broach", \
         
          "stonebreakers_totem", "totem_of_dueling", "totem_of_hex", \
          "totem_of_indomitability", "totem_of_splintering", \
          "totem_of_the_dancing_flame", "totem_of_the_tundra", \
          "thunderfall_totem",  "bizuris_totem_of_shattered_ice", \
          "totem_of_the_avalanche", "totem_of_quaking_earth", \
          "totem_of_electrifying_wind", "steamcallers_totem", \
          "totem_of_calming_tides", "totem_of_forest_growth", \
          "totem_of_healing_rains", "totem_of_the_surging_sea", \
          "deadly_gladiators_totem_of_the_third_wind", \
          
          "deadly_gladiators_libram_of_fortitude", \
          "furious_gladiators_libram_of_fortitude", \
          "relentless_gladiators_libram_of_fortitude", \
          "libram_of_avengement", "libram_of_discord", \
          "libram_of_divine_judgement", "libram_of_divine_purpose", \
          "libram_of_furious_blows", "libram_of_radiance", \
          "libram_of_reciprocation", "libram_of_resurgence", \
          "libram_of_three_truths", "libram_of_valiance", \
          "libram_of_wracking", "venture_co._libram_of_protection", \
          "venture_co._libram_of_retribution", "blessed_book_of_nagrand", \
          "brutal_gladiators_libram_of_fortitude", "brutal_gladiators_libram_of_justice", \
          "brutal_gladiators_libram_of_vengeance", "deadly_gladiators_libram_of_justice", \
          "furious_gladiators_libram_of_justice", "gladiators_libram_of_fortitude", \
          "gladiators_libram_of_justice", "gladiators_libram_of_vengeance", \
          "hateful_gladiators_libram_of_justice", "libram_of_absolute_truth", \
          "libram_of_defiance", "libram_of_mending", "libram_of_obstruction", \
          "libram_of_renewal", "libram_of_repentance", "libram_of_souls_redeemed", \
          "libram_of_the_eternal_tower", "libram_of_the_lightbringer", "libram_of_the_resolute", \
          "libram_of_the_sacred_shield", "libram_of_tolerance", "libram_of_veracity", \
          "mericiless_gladiators_libram_of_fortitude", "mericiless_gladiators_libram_of_justice", \
          "mericiless_gladiators_libram_of_vengeance", "savage_gladiators_libram_of_justice", \
          "savage_gladiators_libram_of_justice", "vengeful_gladiators_libram_of_fortitude", \
          "vengeful_gladiators_libram_of_justice", "vengeful_gladiators_libram_of_vengeance", \
          "venture_co_libram_of_mostly_holy_deeds"
          
          "sigil_of_the_hanged_man", "deadly_gladiators_sigil_of_strife",
          "furious_gladiators_sigil_of_strife", \
          "hateful_gladiators_sigil_of_strife", \
          "relentless_gladiators_sigil_of_strife", "sigil_of_arthritic_binding", \
          "sigil_of_awareness", "sigil_of_deflection", "sigil_of_haunted_dreams", \
          "sigil_of_insolence", "sigil_of_the_dark_rider", "sigil_of_virulence", \
          "sigil_of_the_frozen_conscience", "sigil_of_the_unfaltering_knight", \
          "sigil_of_the_vengeful_heart", "sigil_of_the_wild_buck"]:
        item_str += ",stats=" + stats_dict_to_string(item)
      i = 0
      gem_str = ""
      for gem in rawr_item_str[1:-1]:
        if gem != "0":
          i += 1
          gem_stats = get_node_stats(gem)
          if gem_stats["slot"] == "meta":
            pass # TODO for meta I only need the name to give to simc... for now I'll assume meta is matched... TODO: fix

          else:
            try:
              if not is_gem_matching_socket(gem_stats["slot"], item["socketcolor" + str(i)]):
                is_socket_matched = False
            except:
              pass # REST MUST BE PRISMATIC SOCKET - DON'T AFFECT BONUS
          gem_str += stats_dict_to_string(gem_stats) + "_"
      gem_str = gem_str[:-1]
      if is_socket_matched:
        try:
          key = item["socketbonus"].keys()[0] # assuming only a single socket bonus
          gem_str += "_" + item["socketbonus"][key] + key
        except:
          pass
      item_enchant_id = rawr_item_str[-1] # ignore this? I think simc already figures this out so grab from there, split the char file from that # NOPE... TODO: Read Rawr EnchantCache too
      enchant_str = ""
      if item_enchant_id != "0":
        enchant_stats = get_node_stats(item_enchant_id, mode="enchant")
        # TODO do these work?
        if enchant_stats["itemname"] in \
          ["lightweave_embroidery", "darkglow_embroidery", "swordguard_embroidery", \
          "berserking", "mongoose", "black_magic", "hyperspeed_accelerators", \
          "hand_mounted_pyro_rocket", "rune_of_razorice", \
          "rune_of_the_fallen_crusader", "executioner", "spellsurge"]:
          enchant_str = enchant_stats["itemname"]
        else:
        # for pure stat enchants, just include the stats
          enchant_str += stats_dict_to_string(enchant_stats)

      # Hardcoded special case handling for items with unique effects
      # ###############################
      if item_name == "dislodged_foreign_object": # TODO volatile power too
        if rawr2simc_string(item["itemlevel"]) == "264":
          char_str += rawr2simc_string(slot) + "=" + item_name + ",stats=155haste,equip=onspellcast_105sp_10stack_10%_20dur_45cd_2tick\n"
          continue
        elif rawr2simc_string(item["itemlevel"]) == "277":
          char_str += rawr2simc_string(slot) + "=" + item_name + ",stats=170haste,equip=onspellcast_121sp_10stack_10%_20dur_45cd_2tick\n"
          continue
      elif item_name == "tiny_abomination_in_a_jar": # TODO volatile power too
        if rawr2simc_string(item["itemlevel"]) == "264":
          char_str += rawr2simc_string(slot) + "=" + item_name + ",stats=85hit\n"
          continue
        elif rawr2simc_string(item["itemlevel"]) == "277":
          char_str += rawr2simc_string(slot) + "=" + item_name + ",stats=85hit\n"
          continue
      elif item_name in ["deaths_choice", "deaths_verdict"]: # TODO volatile power too
        if rawr2simc_string(item["itemlevel"]) == "245":
          char_str += rawr2simc_string(slot) + "=" + item_name + ",stats= 256ap\n"
          continue
        elif rawr2simc_string(item["itemlevel"]) == "258":
          char_str += rawr2simc_string(slot) + "=" + item_name + ",stats=288ap\n"
          continue
      elif item_name in ["reign_of_the_dead", "reign_of_the_unliving"]: # TODO volatile power too
        if rawr2simc_string(item["itemlevel"]) == "245":
          char_str += rawr2simc_string(slot) + "=" + item_name + ",stats=150sp,equip=onspelldirectcrit_1882fire_3stack_2.0cd\n"
          continue
        elif rawr2simc_string(item["itemlevel"]) == "258":
          char_str += rawr2simc_string(slot) + "=" + item_name + ",stats=168sp,equip=onspelldirectcrit_2117fire_3stack_2.0cd\n"
          continue
      elif item_name == "nevermelting_ice_crystal": # TODO volatile power too
        char_str += rawr2simc_string(slot) + "=" + item_name + ",stats=111sp,equip=onspelldirectcrit_184crit_5stack_20dur_180cd_reverse\n"
        continue
      # TODO may have to use empowered_deathbringer and raging_deathbringer,
      # not sure it works
      elif item_name == "deathbringers_will": # TODO volatile power too
        if rawr2simc_string(item["itemlevel"]) == "264":
          char_str += rawr2simc_string(slot) + "=" + item_name + ",stats=155arpen\n"
          continue
        elif rawr2simc_string(item["itemlevel"]) == "277":
          char_str += rawr2simc_string(slot) + "=" + item_name + ",stats=167arpen\n"
          continue
      elif item_name == "black_bruise":
        if rawr2simc_string(item["itemlevel"]) == "264":
          char_str += "main_hand=black_bruise,stats=69sta_93ap,weapon=fist_2.6speed_471min_707max"
          # no gems for normal version
          if len(enchant_str) > 0:
            char_str += ",enchant=" + enchant_str + "\n"
          continue
        elif rawr2simc_string(item["itemlevel"]) == "277":
          char_str += "main_hand=black_bruise,heroic=1,stats=78sta_72ap,weapon=fist_2.6speed_521min_782max"
          if len(gem_str) > 0:
            char_str += ",gems=" + gem_str
          if len(enchant_str) > 0:
            char_str += ",enchant=" + enchant_str + "\n"
          continue
      elif item_name == "zods_repeating_longbow":
        if rawr2simc_string(item["itemlevel"]) == "264":
          char_str += "ranged=zods_repeating_longbow,stats=51sta_34agi,weapon=bow_2.8speed_542min_887max"
          # no gems for normal version
          if len(enchant_str) > 0:
            char_str += ",enchant=" + enchant_str + "\n"
          continue
        elif rawr2simc_string(item["itemlevel"]) == "277":
          char_str += "ranged=zods_repeating_longbow,heroic=1,stats=57sta_22agi,weapon=bow_2.8speed_618min_999max"
          if len(gem_str) > 0:
            char_str += ",gems=" + gem_str
          if len(enchant_str) > 0:
            char_str += ",enchant=" + enchant_str + "\n"
          continue
      elif item_name == "nibelung":
        if rawr2simc_string(item["itemlevel"]) == "264":
          char_str += "main_hand=nibelung,stats=99sta_107int_741sp,weapon=staff_2.1speed_294min_542max"
          if len(gem_str) > 0:
            char_str += ",gems=" + gem_str
          if len(enchant_str) > 0:
            char_str += ",enchant=" + enchant_str + "\n"
          continue
        elif rawr2simc_string(item["itemlevel"]) == "277":
          char_str += "main_hand=nibelung,heroic=1,stats=103sta_115int_837sp,weapon=staff_2.1speed_346min_620max"
          if len(gem_str) > 0:
            char_str += ",gems=" + gem_str
          if len(enchant_str) > 0:
            char_str += ",enchant=" + enchant_str + "\n"
          continue
      elif item_name == "shadowmourne":
        char_str += "main_hand=shadowmourne,stats=198sta_233str_114crit_114arpen,weapon=axe2h_3.7speed_954min_1592max"
        if len(gem_str) > 0:
          char_str += ",gems=" + gem_str
        if len(enchant_str) > 0:
          char_str += ",enchant=" + enchant_str + "\n"
        continue
      elif item_name == "bryntroll_the_bone_arbiter":
        if rawr2simc_string(item["itemlevel"]) == "264":
          char_str += "main_hand=bryntroll,stats=161sta_169str,equip=onattackhit_2250Drain_11%,weapon=axe2h_3.4speed_801min_1203max"
          if len(gem_str) > 0:
            char_str += ",gems=" + gem_str
          if len(enchant_str) > 0:
            char_str += ",enchant=" + enchant_str + "\n"
          continue
        if rawr2simc_string(item["itemlevel"]) == "277":
          char_str += "main_hand=bryntroll,stats=173sta_185str,equip=onattackhit_2538Drain_11%,weapon=axe2h_3.4speed_886min_1329max"
          if len(gem_str) > 0:
            char_str += ",gems=" + gem_str
          if len(enchant_str) > 0:
            char_str += ",enchant=" + enchant_str + "\n"
          continue
      # ###############################
      
          
      if len(gem_str) > 0:
        item_str += ",gems=" + gem_str
      if len(enchant_str) > 0:
        item_str += ",enchant=" + enchant_str
      char_str += item_str + "\n"
  char_str = char_str.rstrip()
  return char_str

"""
Utility function to generate a file for each item in a Rawr item cache
"""
def generate_item_files(rawr_cache):
  with open(rawr_cache, "r") as f:
    xml = BeautifulSoup(f)

    for node in xml.arrayofitem.children:
      try:
        if len(node.stats.contents) == 0 and len(node.mindamage.contents) == 0 and len(node.maxdamage.contents):
          continue
        id = node.id.string
        # TODO should create dir if it doesn't exist
        with open(item_cache_base_dir + "/" + str(id) + ".xml", "w+") as item_file:
          item_file.write(str(node))
      except AttributeError:
        pass

"""
Utility function to generate a file for each enchant in a Rawr enchant cache
"""
def generate_enchant_files(rawr_cache):
  with open(rawr_cache, "r") as f:
    xml = BeautifulSoup(f)
    for node in xml.arrayofenchant.children:
      try:
        if len(node.stats.contents) == 0:
          continue
        id = node.id.string
        # TODO should create dir if it doesn't exist
        with open(enchant_cache_base_dir + "/" + str(id) + ".xml", "w+") as enchant_file:
          enchant_file.write(str(node))
      except AttributeError:
        pass

if __name__ == "__main__":
  if len(sys.argv) > 1:
    print convert_char_items(sys.argv[1])
  else:
    generate_item_files("ItemCache.xml")
    generate_enchant_files("EnchantCache.xml")