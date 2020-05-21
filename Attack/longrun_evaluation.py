# Long-run Captures Attack.
#


from evaluate import *
from longrun_helpers import *






##### CLASSIFIER
print("Building the Classifier")

DATA_PATH = ["data/huawei/Endomondo-1/", "data/huawei/AppInTheAir-1/",
             "data/huawei/DiabetesM-2/", "data/huawei/DiabetesM-3/", "data/huawei/DiabetesM-4/",
             "data/huawei/FoursquareCityGuide-1/", "data/huawei/HealthyRecipes-1/",
             "data/huawei/Lifesum-1/", "data/huawei/Playstore-1/", "data/huawei/open-6/", "data/huawei/elapsed-time/open-9/",
             "data/huawei/elapsed-time/open-13/",
             "data/huawei/elapsed-time/open-15/",
             "data/huawei/elapsed-time/open-16/", "data/huawei/force-stop-2/",
             "data/huawei/NoApp_NoAction/"]



# Discard:  'FitBreathe_open','FitWorkout_open','Fit_open'. Because of update does not send data anymore
DISCARDED_ACTION = [] # [ 'FitBreathe_open', 'FitWorkout_open', 'Fit_open', "Camera_force-stop"]

# Merge all force-stop and background in one class that acts as a filter:
force_stop = ['AppInTheAir_force-stop', 'Bring_force-stop', 'ChinaDaily_force-stop',
              'DCLMRadio_force-stop', 'Endomondo_force-stop', 'FindMyPhone_force-stop',
              'FoursquareCityGuide_force-stop', 'KeepNotes_force-stop', 'Krone_force-stop',
              'Lifesum_force-stop', 'Maps_force-stop', 'Meduza_force-stop', 'Running_force-stop',
              'Spotify_force-stop', 'Strava_force-stop', 'Telegram_force-stop',
              'Translate_force-stop', 'WashPost_force-stop',
              'NoApp_NoAction']


TO_MERGE = [force_stop]

# This is the noise class.
# I named it AllApps_force-stop but should rather be
# NoApp_NoAction but this implies other changes so be careful
NAMES = ["AllApps_force-stop"]
#evaluate(DATA_PATH, TO_MERGE=TO_MERGE, MERGED_NAMES=NAMES, PRINT_COUNT=True, EQUALIZATION=False)


UNIQUE_DELTAS=[0,46, 1005]

to_withdraw = find_feat_to_withdraw(DATA_PATH)
#to_withdraw = []
# Extract features
X, y, feature_name = evaluate(DATA_PATH,
                              TO_MERGE=TO_MERGE, MERGED_NAMES=NAMES,
                              DETAIL_PRINT=True,
                              RETURN_FEATURES_AND_LABELS=True,
                              DISCARDED_ACTION=DISCARDED_ACTION,
                              TO_WITHDRAW=to_withdraw
                             )


# Create and Train the model
clf=RandomForestClassifier(n_estimators=1000, random_state=None)
clf.fit(X, y)

# Get the set of all classes the classifier knows about
all_trained_action = set(np.unique(np.array(y)).tolist())
print("Classifier has : {} classes".format(len(all_trained_action)))


#### Imports
print("Importing longruns")
DATA_PATH = ["./data/huawei/longrun/user-interaction-pattern-1/", "./data/huawei/longrun/user-interaction-pattern-2/", "./data/huawei/longrun/user-interaction-pattern-3/"]
captures, content_ground_truth = import_longrun(DATA_PATH, 
                                                ALL_TRAINED_ACTION=all_trained_action,
                                                MERGED_FORCE_STOP=force_stop) # This should be merged Noise


print("Process and predict the longrun capture")
### Predict the longrun
predicted = predict_all(captures, CLF=clf, TO_WITHDRAW=to_withdraw,
                        INTER_TIMER_EVENT_CUTOFF=10,
                        WINDOW_SIZE=15, DPRINT=False,
                        MINIMUM_SIZE_CRITICAL_STARTING_POINT=0,
                        INTER_SPACING_CRITICAL_POINTS=1)

print("Evaluate and find the best F1 score and its ")
### Evaluate and find the best F1 score and its
ps, rs, f1s = plot_f1_prec_rec(predicted, content_ground_truth, clf)
