from .DesiredStuffTab import DesiredStuffTab
from .PopupBar import PopupBarOrganizerTab
from .IRFManagerTab import IRFManagerTab
from MultiTools import GlobalEventsTab, GSVManagerTab, ScriptEditorTab, NodeColorRegistryTab

# compile list of tabs
tabs_list = [
    DesiredStuffTab,
    IRFManagerTab,
    NodeColorRegistryTab.Tab,
    PopupBarOrganizerTab,
    GlobalEventsTab.Tab,
    GSVManagerTab.Tab,
    ScriptEditorTab.Tab
]

# register all tabs
PluginRegistry = []
for tab in tabs_list:
    PluginRegistry.append(("KatanaPanel", 2, tab.NAME, tab))


# register PiP Tabs
from .PopupBar.PopupBarTabInitializer import popup_bar_tabs

for popup_bar_tab in popup_bar_tabs:
    tab_name = "/". join(["Popup Bar Displays", popup_bar_tab["filename"], popup_bar_tab["popup_bar_widget_name"]])
    PluginRegistry.append(("KatanaPanel", 2, tab_name, popup_bar_tab["constructor"]))
    #print(popup_bar_tab)


# LOG
print("""\t|____  TABS""")
for tab in tabs_list:
    print("\t|\t|__  Loading...  {tab_name}".format(tab_name=tab.NAME))
    if tab == PopupBarOrganizerTab:
        for popup_bar_tab in popup_bar_tabs:
            tab_name = "/".join([popup_bar_tab["filename"], popup_bar_tab["popup_bar_widget_name"]])
            print("\t|\t|\t|__  Loading...  {tab_name}".format(tab_name=tab_name))
