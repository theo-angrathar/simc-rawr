# simc-rawr
Python scripts to make SimulationCraft usable for WoW WotLK Servers

The WotLK version of SimulationCraft grabs data from Wowhead even when choosing a local Rawr character file in XML format.
Unfortunately, Wowhead lists item stats as they are after Blizzard's stat squish in WoD. As a result, the item stats that
SimulationCraft uses are are incorrect for WotLK, and simulation results for characters are invalid.

This set of Python scripts forces local Rawr item and enchant caches to be used.

I wrote this hackscript several years ago while playing on a WotLK server, with lots of messy code, no documentation, and poor
usability. I only ever intended it for personal use, but I've had several requests over the years for these scripts.

I'm providing them here "as-is", with no promises that they will work. Not all possible green/blue items are contained in the item
XMLs -- I only added ones I needed for my own characters. Many items pre-ToC and pre-ICC are missing special proc effects and the like.

Use at your own risk. I have not touched this in years and don't plan to make any further changes. If anyone wishes to improve them,
feel free (and please share any work with the community).

# Quick Start

Requirements: Python 2.7, SimulationCraft for WotLK, Rawr for WotLK.

Clone the repo or download the zip from here, extracting into <<your_simcraft_directory>>/simc_rawr_launcher

To run, open a command-line window and navigate to the directory where you extracted this. Run "python simc_rawr.py"

# (Optional) Make a Windows shortcut

Alternatively, make a Windows shortcut to get Python to launch the script. For example, on my machine the shortcut has the "Target" line

"C:\Program Files\Python27\python.exe" "C:\Games\World of Warcraft (WotLK)\Utilities\SimulationCraft\simc_rawr_launcher\simc_rawr.py"

The "start in" line is.

"C:\Games\World of Warcraft (WotLK)\Utilities\SimulationCraft\simc_rawr_launcher"

# Configuration

simc_rawr.conf contains the following (optional) configuration parameters:

simc_dir: The directory where SimulationCraft is (where simc.exe is) located. Defaults to .. (the previous directory), which is fine if you placed these files in <<your simcraft folder>>/simc_rawr_launcher

rawr_char_dir: The folder where your XML Rawr characters are. This is used for simc_rawr_launcher to default to this folder when displaying the "choose character" dialog.

iterations: number of iterations to perform in SimC

calculate_scale_factors: True or False. Whether to compute the relative value of each stat, normalized to either attack power or spell power.

normalization_stat: ap (attack power) or sp (spell power). Defaults to attack power. This stat will have a value of 1 when calculating scale factors, and other stats will have a value relative to this stat.
