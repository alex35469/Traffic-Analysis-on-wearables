from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
import time
import sys
sys.path.append(r"./yaml")
import longrun_config
import yaml
from helper_controller import *
from helper import *
from random import choice, random, uniform
from helper_controller import read_app



################################ VARIABLES ##################################

# Categories
# better if application.yaml but lack of time
messengers = ['Telegram', 'Glide']
emails = ['Outlook']
maps = ['Maps', 'Citymapper', 'FoursquareCityGuide']
fitness = ['FitWorkout', 'Fit', 'FITIVPlus', 'Endomondo', 'Strava', 'Running']
note_taking = ['Bring', 'KeepNotes']
health = ['Lifesum', 'SmokingLog', 'HealthyRecipes','DiabetesM']
banking = ['Mobilis']
media = ['ChinaDaily', 'Krone', 'WashPost', 'Meduza']
religious = ['DCLMRadio', 'SalatTime']
other = ['Translate', 'Weather', 'PlayStore', 'Shazam', 'FitBreathe', 'SleepTracking', 'FindMyPhone', 'Spotify', 'Calm']

popular = messengers + emails + fitness + note_taking
f = 1.5  # multiplication factor. f more time to occur if in popular


NORM_USER_INTERACT_SLOT_10 = [0.3, 0.19, 0.17, 0.1, 0.05, 0.03, 0.05, 0.18, 0.35, 0.5, 0.6, 0.68, 0.7, 0.835, 0.84, 0.9, 0.85, 1, 0.96, 0.85, 0.8, 0.6, 0.61, 0.38]
NORM_USER_INTERACT_SLOT_30 = [0.3, 0.19, 0.2, 0.19, 0.09, 0.05, 0.09, 0.18, 0.35, 0.6, 0.7, 0.69, 0.71, 0.89, 0.85, 0.9, 0.82, 0.96, 1, 0.9, 0.8, 0.58, 0.58, 0.38]


NORM_USER_INTERACT = NORM_USER_INTERACT_SLOT_30
EXPECTED_ACTION_DURATION = 30  # seconds


########################### APPS CHOICE #####################################

apps_all = read_app(longrun_config.APPLICATIONS_FNAME)

all_action = []
# filter popular with the apps that will remain
for app in apps_all:
    if len(longrun_config.KEEP_ONLY) == 0 and not app in longrun_config.SKIPPING:
        all_action += [app+"_"+action for action in apps_all[app]["keepOnly"]]
    elif app in longrun_config.KEEP_ONLY and not app in longrun_config.SKIPPING:
            all_action += [app+"_"+action for action in apps_all[app]["keepOnly"]]

# First, equilibrate actions. If an app counts 3 actions: a1, a2, a3 and another app countains only 1 action b1
# we should have P(a1 or a2 or a3) = P(b1) = 0.5
apps_prob_vect = dict()
action_per_apps = dict()
kept_actions = []
for action in all_action:
    app, act = action.split("_")
    # skip force stop because anyway open trigers stop
    if act == "force-stop":
        continue
    apps_prob_vect[app] = 0
    v = action_per_apps.get(app, [])
    action_per_apps[app] = v + [act]

L = len(popular)
N = len(apps_prob_vect)

p_popular = f/(N + L * (f - 1))
p_normal = 1/(N + L * (f - 1))

# recompute probability vector
for app in apps_prob_vect:
    if app in popular:
        apps_prob_vect[app] = p_popular
    else:
        apps_prob_vect[app] = p_normal

if round(sum(apps_prob_vect.values()), 10) != 1.0:
    print("Error! Not a distribution probability: sum = ", sum(apps_prob_vect.values()) ," Please check the popular set")
    sys.exit(1)

cumul = 0
for app in apps_prob_vect:
    cumul += apps_prob_vect[app]
    apps_prob_vect[app] = cumul

def pick_app_from_prob_vect():
    r = random()
    for app in apps_prob_vect:
        if r < apps_prob_vect[app]:
            #print("r={}, app = {}".format(r, app))
            return app
    return app


################################## TIME WAITING ########################

# skeeze 24 hours
slot_duration = float(longrun_config.CAPTURE_DURATION)


expected = slot_duration / (longrun_config.WAITING_TIME + EXPECTED_ACTION_DURATION)
expected_after_norm = [norm * expected for norm in NORM_USER_INTERACT]
waiting_in_slot = [slot_duration / exp - EXPECTED_ACTION_DURATION for exp in expected_after_norm ]


# Check
if max(waiting_in_slot) > slot_duration:
    print("Waiting time exceed slot duration.")
    print("min CAPTURE_DURATION should be with these settings >=",round(max(waiting_in_slot),1), " seconds")
    print("Please change longrun_config, or some slot will not have any capture.")


################################ FINAL PUBLIC FUNC #####################
print(waiting_in_slot)

def user_interact_choice():
    app = pick_app_from_prob_vect()
    action = choice(action_per_apps[app])
    return app, action



def user_interact_wait(slot):
    # Recompute for the next slot the time needed to wait
    return waiting_in_slot[slot]
