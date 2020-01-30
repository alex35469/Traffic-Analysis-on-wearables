#! python3
"""Classes in this file represents applications"""
from watch_moves import button_click_func, swipe_left, swipe_up, swipe_down, swipe_right
from time import sleep

class Action:
    "Action that can be performed within an application"
    def __init__(self, name, description, commands, wait = 1):
        """Args:
                name: name of the action
                description: desc. of the action
                command perform the action
                wait: wait between 2 actions commands
                """
        self.name = name
        self.description = description
        self.commands = commands
        self.wait = wait

    def launch(self, device, display):
        for i, command in enumerate(self.commands):
            command(device, display)
            # Sleep only if it is not the last command
            if i != len(self.commands) - 1:
                sleep(self.wait)


class Endomondo:
    "Endomondo Application. List all the actions that "
    PLAY = Action("play", "push the green play button", [button_click_func((200,200))])
    STOP = Action("stop", "Press the stop button", [swipe_left, button_click_func((190,190))])
    MAP = Action("see map", "see the map", [swipe_left])
    SEE_STATS_1 = Action("see stats 1", "open the statistics page on duration and distance", [swipe_down])
    SEE_STATS_2 = Action("see stats 2", "open the statistics page on duration and distance", [swipe_down, swipe_down])

    def __init__(self, device, display):
        self.device = device
        self.display = display

    def simulate(self, actions, print_action=False, wait=2):
        # Simulate a sequence of action
        for action in actions:
            action.launch(self.device, self.display)
            if print_action:
                print(action.name)
            sleep(wait)
