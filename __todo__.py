"""
TODO: Enhancement
    *   PopupBar Widget closing nodegraphs
            Closing tabs in general needs to run some sort of cleanup handler
    *   VariableManager | Can load multiple patterns
            Remake this?
    *   Swipe Interaction
            * Add/Remove selection
                - Fix output sorting algorithm
                - Tab node creation auto connection
            * Add colors to links that have been hit
                - need to write something custom in the paint handler
                    1.) Get i/o ports, store as attr
                    2.) Draw line between ports
                    3.) Reset i/o ports attr
                    4.) Clear color
    *   Backdrop lock
            * Lock all items in a backdrop
                - Lock toggle button
                    popup password, store in cypher
                - Lock all nodes in backdrop
    *   Gesture Layers
            - NMC
                Hit box detection
                Not sure if this is worth supporting.  The API is very closed off.
            - Extract API
                    1 Layer
                    Do x on hit
                    Do x on release
    *   Popup Widgets
            Move tidy this up
TODO: cgwidgets
    *   List handler is driving me up the walls
            When typing from empty, after it shows the first time, after the first key, if there are no
            valid options, it will close.
    *   PopupBar Widget (performance)
        - Move this to a StackWidget that hides/shows on hover
    *   PopupBar Widget (bug)
        - Pin widget for some reason doesn't disappear all the time
                Maybe something to do with the timer?  In theory this might resolve after
                moving to a stacked widget.
TODO: BUGS
    *   Node Graph
            If no nodegraphs found, will fail on init
    *   Node Graph Pins
            - Deleting a reference and re adding the same reference does not work
                probably needs to update internal meta data
            - Move to stand alone popup widget API
    *   GSV Manager
            - Events doesn't properly show new scripts
            - View breaks after reordering variables
"""
