Saves selections into the drive, to maintain persistence. Currently saves them as a Yaml file in the plugin's data folder. In the future we would like to save it into a database. It stores; the directory to store selections, the plugin object itself, a hash map of owner, name, selection. 

### Constructor
Stores the plugin object, and checks whether a selections directory exists within the plugin's data folder, if not it creates one.

### saveSelection
Given a selection object, check if there exists a folder for the selection owner, if not create that folder. Then create a yaml file for the selection, then save the overall selection data, such as owner and world. Save every region in the selection. Then iterate through every lore document and save that into the yaml file.