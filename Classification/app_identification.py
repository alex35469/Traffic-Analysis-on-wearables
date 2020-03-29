import sys
import build_datasets
import machine_learning
import feature_extraction
import numpy as np
import pandas as pd
import sklearn
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier
import operator
from sklearn import metrics
from sklearn.utils.multiclass import unique_labels
import matplotlib.pyplot as plt
from collections import Counter

REBUILD = True
CACHE_FILE = 'app_id_event_all_devices_non_mixed_eq_open_2'
DEVICES_TO_INCLUDE = ['LEO-BX9']#['SamsungGalaxyWatch', 'FossilExploristHR', 'AppleWatch']
PLOT_DIR = 'plots/'
TEST_PERCENTAGE = 0.25
MINIMUM_PAYLOAD = 500  # in B
RATIO_APP_NOT_SATIFING_MINIMUM_PAYLOAD_CUT_OFF = 0.25
pad = build_datasets.pad
DATA_PATH = "data/huawei/open-3/"

# ===============================
# Load or rebuild datasets

events = build_datasets.load_cache(CACHE_FILE)
if REBUILD or events is None:
    sources = build_datasets.find_sources(DATA_PATH)

    def exclude(d):
        device = d.replace(DATA_PATH, '')
        device = device[:device.find('_')]
        return device in DEVICES_TO_INCLUDE

    all_sources_files = list(filter(exclude, sources))
    print(sources)

    build_datasets.rebuild_all_datasets(sources_files=all_sources_files, force_rebuild=REBUILD)

    # split BLE/Classic and Test/Train (1 file = around 20% test)
    sources_test_classic, sources_train_classic = build_datasets.split_test_train_non_mixed(all_sources_files, DEVICES_TO_INCLUDE, test_percentage=TEST_PERCENTAGE)

    print("---------")
    print(sources_test_classic)
    print("---------")
    # Cross-Over safety checks
    for s in []: #all_sources_files:
        if s in sources_test_ble or s in sources_train_ble:
            if s in sources_test_ble:
                print("[BLE]", s, "is in TEST")
                if s in sources_train_ble:
                    print("Panic !", s, "is both in TEST and TRAIN datasets")
                    sys.exit(1)
            if s in sources_train_ble:
                print("[BLE]", s, "is in TRAIN")
                if s in sources_test_ble:
                    print("Panic !", s, "is both in TEST and TRAIN datasets")
                    sys.exit(1)
        if s in sources_test_classic or s in sources_train_classic:
            if s in sources_test_classic:
                print("[CLA]", s, "is in TEST")
                if s in sources_train_classic:
                    print("Panic !", s, "is both in TEST and TRAIN datasets")
                    sys.exit(1)
            if s in sources_train_classic:
                print("[CLA]", s, "is in TRAIN")
                if s in sources_test_classic:
                    print("Panic !", s, "is both in TEST and TRAIN datasets")
                    sys.exit(1)

    # actually parse the files
    events_train_classic, counts_train_classic = build_datasets.cut_all_datasets_in_events(sources_train_classic)
    events_test_classic, counts_test_classic = build_datasets.cut_all_datasets_in_events(sources_test_classic)

    # equilibrate so each device has (1) an equal number of events across its apps/actions and (2) globally, around the same number of events as other devices

    events_train_classic_eq = build_datasets.equilibrate_events_across_apps(events_train_classic)

    events = [events_train_classic, events_train_classic_eq, events_test_classic]
    build_datasets.cache(CACHE_FILE, events)

[events_train_classic, events_train_classic_eq, events_test_classic] = events


# ===============================
# Functions

def remove_events_from_dataset(events, xs, ys):
    for event in events:
        xs = np.array(xs)
        ys = np.array(ys)
        indices_to_remove = np.where(ys == event)

        xs = np.delete(xs, indices_to_remove, 0)
        ys = np.delete(ys, indices_to_remove, 0)

    return xs, ys

def build_features_labels_dataset(events, adversary_capture_duration=-1):
    data = []
    labels = []
    counter_bellow_threshold = Counter()
    counter_total = Counter()
    # shape: data is a [[Features], [Features], ...]
    for device in events:
        for app in events[device]:
            for action in events[device][app]:
                label = app + "_" + action
                for event in events[device][app][action]:
                    features_dict = feature_extraction.extract_features(event, adversary_capture_duration)
                    features = list(features_dict.values())

                    # Filtering by total payload
                    if features_dict["total_payload"] < MINIMUM_PAYLOAD:
                        counter_bellow_threshold.update([label])

                    counter_total.update([label])

                    data.append(features)
                    labels.append(label)
    return [data, labels], counter_bellow_threshold, counter_total


# Fit Random Forest
def random_forest(events_train_eq, X_train, y_train, X_test, y_test, seed=0, n_trees=100):
    clf=RandomForestClassifier(n_estimators=n_trees, random_state=seed)
    clf.fit(X_train,y_train)
    y_pred=clf.predict(X_test)

    accuracy = metrics.accuracy_score(y_test, y_pred)
    feature_importance = pd.Series(clf.feature_importances_,index=feature_extraction.get_list_of_feature_names(events_train_eq))
    feature_importance = feature_importance.sort_values(ascending=False)

    return accuracy, feature_importance[0:10], y_pred

# Plot Confusion Matrix
def confusion_matrix(events_train_eq, events_test, seed=0, n_trees=100, show=True, output="confusion-matrix.png", adversary_capture_duration=-1):

    (X_train, y_train), counter_bellow_threshold, counter_total = build_features_labels_dataset(events_train_eq, adversary_capture_duration)
    (X_test, y_test), _ , _= build_features_labels_dataset(events_test, adversary_capture_duration)

    no_traffic_label = []
    for label in counter_total:
        ratio = counter_bellow_threshold[label]/counter_total[label]
        if ratio > RATIO_APP_NOT_SATIFING_MINIMUM_PAYLOAD_CUT_OFF:
            no_traffic_label.append(label)



    X_train, y_train = remove_events_from_dataset(no_traffic_label, X_train, y_train)
    X_test, y_test = remove_events_from_dataset(no_traffic_label, X_test, y_test)


    # compute all

    print("Sizes:", len(X_train), len(X_train[0]), len(X_test), len(X_test[0]))

    acc, features, y_pred  = random_forest(events_train_eq, X_train, y_train, X_test, y_test, seed, n_trees)

    print(features)

    print("RF accuracy:", acc)

    #acc, _  = machine_learning.naive_bayes(X_train, X_test, y_train, y_test) # careful argument order
    #print("Bayes", acc)

    #acc, _  = machine_learning.k_nearest_neighbors(X_train, X_test, y_train, y_test) # careful argument order
    #print("k_nearest_neighbors", acc)

    #acc, _  = machine_learning.svm(X_train, X_test, y_train, y_test) # careful argument order
    #print("svm", acc)

    cm, fig, ax = machine_learning.plot_confusion_matrix(y_test, y_pred, normalize=True, title=output)
    plt.savefig(PLOT_DIR+output)
    if show:
        plt.show()
    print("Saved image", PLOT_DIR+output)

# ===============================
# Entrypoint

events_train = dict()
events_test = dict()
print(events_train_classic)
events_train['LEO-BX9'] = events_train_classic['LEO-BX9']
events_test['LEO-BX9'] = events_test_classic['LEO-BX9']



confusion_matrix(events_train, events_test_classic, show=False, output="confusion-matrix-app-LEO-BX9_open_3_"+  str(MINIMUM_PAYLOAD//1000) +"KB_" + str(int(RATIO_APP_NOT_SATIFING_MINIMUM_PAYLOAD_CUT_OFF * 100)) + "percent", adversary_capture_duration=-1)
