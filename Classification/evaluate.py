import pandas as pd
import numpy as np
import sys
import random
from build_datasets import *
import csv
import os
import pickle
import copy

import matplotlib.pyplot as plt
from scipy.stats import kurtosis
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split, ShuffleSplit, cross_val_score
from sklearn.utils.multiclass import unique_labels

############################## GLOBAL VARIABLES ##########################


TEST_PERCENTAGE = 0.25
DATA_PATH = ["./data/huawei/elapsed_time/open-7/", "./data/huawei/elapsed_time/open-8/",
             "./data/huawei/elapsed_time/open-9/", "./data/huawei/elapsed_time/open-10/"]
PLOT_DIR = "./plots/"
WATCH_NAME = 'LEO-BX9'
REBUILD = True
EQUALIZATION = False
DISCARDED_ACTION = ["DiabetesM_addCarbsaddInsulin", "WashPost_openConnectionError", "AppInTheAir_openNotLogin"] #["DiabetesM_addCarbsaddInsulin"] # ["DiabetesM_addFat", "DiabetesM_addProt", "DiabetesM_addCal"] # ["DiabetesM_addCarbsaddInsulin"] #  #["WashPost_open_", "AppInTheAir"]
TO_MERGE = [] #[["DiabetesM_addFat", "DiabetesM_addProt", "DiabetesM_addCal", "DiabetesM_addCarbs"]] #, "DiabetesM_addInsulin"]] #["DiabetesM_addFat", "DiabetesM_addProt", "DiabetesM_addCal", "DiabetesM_addCarbs","DiabetesM_addInsulin" ]
MINIMUM_PAYLOAD = 200
RATIO = 0.25
N_SPLITS = 50


############################### FUNCTIONS #############################


def merge_actions_in_app(events, to_merge):
    for actions in to_merge:
        events = merge_action_in_app(events, actions)
    return events


def merge_action_in_app(events, to_merge):
    """to_merge is of the form [app_feature_x1, app_feature_x2...]
    Cannot merge across apps
    """
    app = to_merge[0].split("_")[0]
    events_out = copy.deepcopy(events)
    to_merge_action_set = set([f.split("_")[1] for f in to_merge])
    print("to_merge_action_set = ", to_merge_action_set)
    for w in events:
        for appli in events[w]:
            if appli != app:
                continue
            merged_actions = []
            labeled_actions = ""
            for action in events[w][app]:
                if action in to_merge_action_set:
                    labeled_actions += action
                    merged_actions += events[w][app][action]
                    del events_out[w][app][action]
            events_out[w][app][labeled_actions] = merged_actions
    return events_out


def discard_actions(source_files, to_discard):
    sf_new = []
    for f in sources_files:
        _in = False
        for df in to_discard:
            if df in f:
                _in = True
        if not _in:
            sf_new.append(f)
    return sf_new


def build_features_labels_dataset(events, adversary_capture_duration=-1):
    data = []
    labels = []
    for device in events:
        for app in events[device]:
            for action in events[device][app]:
                label = app + "_" + action
                for event in events[device][app][action]:
                    features_dict = extract_features(event, adversary_capture_duration)
                    features = list(features_dict.values())
                    data.append(features)
                    labels.append(label)

    return data, labels


def equilibrate_events_across_apps(events):
    counts = dict()
    for device in events:
        for app in events[device]:
            for action in events[device][app]:
                counts[app +"_" + action] = 0
            for action in events[device][app]:
                counts[app +"_" + action] += len(events[device][app][action])

    if len(counts.values())== 0:
        return events

    nb_samples_per_cat = min(counts.values())

    events_out = dict()

    # remove everything above the min # across devices
    for device in events:
        for app in events[device]:

            for action in events[device][app]:

                if not device in events_out:
                    events_out[device] = dict()
                if not app in events_out[device]:
                    events_out[device][app] = dict()
                if not action in events_out[device][app]:
                    events_out[device][app][action] = random.sample(events[device][app][action], k=nb_samples_per_cat)

    counts = dict()
    for device in events_out:
        for app in events_out[device]:
            if not app in counts:
                counts[app] = 0
            for action in events_out[device][app]:
                counts[app] += len(events_out[device][app][action])

    return events_out, nb_samples_per_cat


def create_sub_dataset(datasets, N_TO_PICK = -1, AppToKeepOnly="all"):
    datasets_to_analysis = []
    labels_to_analysis = []

    for watch in datasets:
        for app in datasets[watch]:
            if AppToKeepOnly != "all" and app not in AppToKeepOnly:
                continue
            for action in datasets[watch][app]:
                label= WATCH_NAME +"_"+app+"_"+action


                events = datasets[watch][app][action]
                chosen_events = []
                if type(datasets[watch][app][action]) is dict:
                    events = list(events.keys())

                if N_TO_PICK == -1 or len(events) < N_TO_PICK:
                    chosen_events = random.sample(events, len(events_nb))
                    if N_TO_PICK != -1:
                        print("N_TO_PICK too large. Took all the dataset for " + app + "_" + action ," instead")
                    chosen_events = random.sample(events, N_TO_PICK)

                if type(datasets[watch][app][action]) is dict:
                    labels_to_analysis += [label + "_" + nb for nb in chosen_events]
                    datasets_to_analysis += [datasets[watch][app][action][event_nb] for event_nb in chosen_events]
                else:
                    labels_to_analysis += [label for nb in chosen_events]
                    datasets_to_analysis += events

    return datasets_to_analysis, labels_to_analysis


def extract_features(xy, capture_duration_does_nothing=0): # dataset is {'xs': [packet1, packet2,...], 'ys': [packet1, packet2,...]} where x is time and y is size
    xs = xy['xs']
    ys = xy['ys']
    f = dict()

    def take(arr, n=30):
        if len(arr) > n:
            return arr[:30]
        return arr

    def stats(key, data):
        if len(data) == 0:
            data=[-1]
        f['min_'+key] = np.min(data)
        f['mean_'+key] = np.mean(data)
        f['max_'+key] = np.max(data)
        f['count_'+key] = len(data)
        f['std_'+key] = np.std(data)
        f['kurtosis_'+key] = kurtosis(data)



    # general statistics
    stats("non_null", [abs(y) for y in ys if y != 0])
    stats("outgoing", [abs(y) for y in ys if y > 0])
    stats("incoming", [abs(y) for y in ys if y < 0])
    stats("outgoing_30", [abs(y) for y in take(ys) if y > 0])
    stats("incoming_30", [abs(y) for y in take(ys) if y < 0])

    f["total_payload"] = sum([abs(y) for y in ys])

    # statistics about timings
    x_deltas = []
    i = 1
    while i<len(xs):
        x_deltas.append(xs[i]-xs[i-1])
        i += 1

    stats("x_deltas", x_deltas)
    stats("x_deltas_30", take(x_deltas))

    # bursts

    # unique packet lengths [Liberatore and Levine; Herrmann et al.]
    lengths = dict()
    for i in range(1,1005):
        lengths[str(i)] = 0
    for y in ys:
        if str(abs(y)) in lengths:
            lengths[str(abs(y))] += 1

    lengths_array = list(lengths.values())
    stats("unique_lengths", lengths_array)
    for l in lengths:
        f['unique_lengths_'+str(l)] = lengths[l]
    return f


def filter_by_length(events, minimum_payload=500, ratio_app_not_satisfing_minimum_payload_length=0.25, printInfo = False):
    results = copy.deepcopy(events)
    for watch in events:
        for app in events[watch]:
            for action in events[watch][app]:
                total_event = len(events[watch][app][action])
                bellow_minimum_payload = 0
                for sample in events[watch][app][action]:

                    payload_length = sum([abs(s) for s in sample["ys"]])
                    if payload_length < minimum_payload:
                        bellow_minimum_payload += 1

                ratio_bellow = bellow_minimum_payload / total_event
                if ratio_bellow > ratio_app_not_satisfing_minimum_payload_length:
                    if printInfo:
                        print("total_event: ", total_event, " - bellow threshold: ", bellow_minimum_payload)
                        print(app + "_" + action + " removed")
                        print(" ratio_below = ", ratio_bellow)
                    del results[watch][app][action]

            if len(results[watch][app]) == 0:
                del results[watch][app]
    return results


def plot_confusion_matrix(y_true, y_pred,
                          normalize=True,
                          title=True,
                          save = None):

    # Compute confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    # Only use the labels that appear in the data
    classes = unique_labels(y_true, y_pred)
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    fig, ax = plt.subplots(figsize=(20, 20), dpi= 180)
    ax.imshow(cm, interpolation='none', aspect='auto', cmap=plt.cm.Blues)


    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
            rotation_mode="anchor")

    ax.set(xticks=np.arange(cm.shape[1]),
            yticks=np.arange(cm.shape[0]),
            # ... and label them with the respective list entries
            xticklabels=classes, yticklabels=classes,
            title=title,
            ylabel='True label',
            xlabel='Predicted label')

    # Rotate the tick labels and set their alignment.
    #plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
    #         rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], fmt),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black")


    plt.savefig(PLOT_DIR+save)
    print("Saved image", PLOT_DIR+save+".png")

    return cm, fig, ax


def count_print(events):
    for d in events:
        for app in events[d]:
            for act in events[d][app]:
                print("{}: {}_{} - {}".format(d, app, act,  len(events[d][app][act])))


#### MAIN ####

# ## Import all the dataset
print("\nimporting data...")
sources_files = find_sources(DATA_PATH)


if len(DISCARDED_ACTION) != 0:
    print("withdraw action to be discarded")
    sources_files = discard_actions(sources_files, DISCARDED_ACTION)


if REBUILD:
    print("rebuilding dataset")
    rebuild_all_datasets(sources_files, REBUILD)

events, counts = cut_all_datasets_in_events(sources_files)

if len(TO_MERGE) != 0:
    print("merging events")
    events = merge_actions_in_app(events, TO_MERGE)


print("filtering app that does not send traffic by their length")
filtered_events = filter_by_length(events, minimum_payload=MINIMUM_PAYLOAD, ratio_app_not_satisfing_minimum_payload_length=RATIO)

print("\nclass event count")
count_print(filtered_events)

nb_samples_per_cat = "not uniform"
if EQUALIZATION:
    print("dataset equalization per class")
    filtered_events, nb_samples_per_cat = equilibrate_events_across_apps(filtered_events)
    print("\nclass event count after equalization")
    count_print(filtered_events)


print("building features and labels")
X, y = build_features_labels_dataset(filtered_events)


# ## Accuracy with cross validation

print("\nbuilding and training the model for cross validation ")
clf=RandomForestClassifier(n_estimators=100, random_state=None)
shuf_split = ShuffleSplit(n_splits=N_SPLITS, test_size=0.25, random_state=None)
scores_shuffle = cross_val_score(clf, X, y, cv=shuf_split)
print("Random split cross-validation. Accuracy: %0.2f (+/- %0.2f). " % (scores_shuffle.mean(), scores_shuffle.std() * 2))
eval_metric = "cross-val radomSplit={} accRs={:.1f} +-{:.1f}% 95% conf interval".format(N_SPLITS, scores_shuffle.mean() *100, scores_shuffle.std() * 2 * 100)

# ### Plotting the confusion matrix

print("\nbuilding and training a model for confusion matrix")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=None)


clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
accuracy = metrics.accuracy_score(y_test, y_pred)
print("accuracy = ", accuracy)


title = "Confusion matrix for {} acc={:2f} ".format("and ".join([f.replace("/", "_") for f in DATA_PATH]), accuracy * 100)
title += eval_metric
title += "test={}% minimum_payload={}B nb_samples={}".format(int(TEST_PERCENTAGE * 100), MINIMUM_PAYLOAD, nb_samples_per_cat)


saved_title = title.replace(".", "_").replace(" ", "_")
plot_confusion_matrix(y_test, y_pred, title= title, save = saved_title)
print("done")
