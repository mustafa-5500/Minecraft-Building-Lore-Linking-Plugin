The entry point for the plugin, where the plugin class is defined.

### OnEnable
The function called by the server to enable the plugin, this initializes the plugin object. Creating the selectionManager, storageManager, visualizer, and loreManager for the plugin. Registering event listeners; Wandlistener, LoreChatListener. The listeners take the manager objects corresponding to their constructor. The commands are registered through the plugin's command executor function, and the bukkit plugin command object.
To register listeners you need to get the server, then get the pluginManager, then use the register events function to register the listeners.
- When thinking about this, if we have a sharded set up the initialization will already be good to go, a seperate plugin object will be created per sever, with the listeners and commands registered to the plugin's corresponding server. All we need to do is make sure the any shared information the plugin uses does not have race conditions. The simplest implementation of this would be semaphores during write. I wonder technically would a read get corrupted while a write is happening? Well I don't think we are bringing in large amounts of data at once, it would be 1 "page" of text send to the user's chat box. Which should then be saved locally for the user.

### OnDisable
Shuts down the plugin, so we need to shutdown managers and listeners I believe, currently it only shutsdown the visualizer and logs that the plugin is disabled.

### Getters
The only varaibles in the plugin object are the managers, all 4 managers have a getter.

### [[Development/Notes/SelectionManager|SelectionManager]]
### [[Development/Notes/SelectionStorageManager|SelectionStorageManager]]
### [[Development/Notes/SelectionVisualizer|SelectionVisualizer]]
