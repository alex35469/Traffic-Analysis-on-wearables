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

REBUILD = True
CACHE_FILE = 'device_id_event_all_devices_non_mixed_eq'
DEVICES_CLASSIC = ['SamsungGalaxyWatch', 'FossilExploristHR', 'AppleWatch'] # other devices are BLE
DEVICES_TO_EXCLUDE = ['']#'BeurerAS80', 'Huawei3', 'MiBand2', 'MiBand3', 'MiBand4', 'SW170', 'PanoBike']
PLOT_DIR = 'plots/'

pad = build_datasets.pad

# ===============================
# Load or rebuild datasets

events = build_datasets.load_cache(CACHE_FILE)
if REBUILD or events is None: 
    sources = build_datasets.find_sources()

    def exclude(d):
        device = d.replace('data/', '')
        device = device[:device.find('_')]
        return device not in DEVICES_TO_EXCLUDE

    all_sources_files = list(filter(exclude, sources))

    build_datasets.rebuild_all_datasets(sources_files=all_sources_files, force_rebuild=REBUILD)

    # split BLE/Classic and Test/Train (1 file = around 20% test)
    sources_test_classic, sources_test_ble, sources_train_classic, sources_train_ble = build_datasets.split_test_train_non_mixed(all_sources_files, DEVICES_CLASSIC)

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
    events_train_ble, counts_train_ble = build_datasets.cut_all_datasets_in_events(sources_train_ble)
    events_test_classic, counts_test_classic = build_datasets.cut_all_datasets_in_events(sources_test_classic)
    events_test_ble, counts_test_ble = build_datasets.cut_all_datasets_in_events(sources_test_ble)

    # equilibrate so each device has (1) an equal number of events across its apps/actions and (2) globally, around the same number of events as other devices

    print("-------- Classic --------")
    events_train_classic_eq = build_datasets.equilibrate_events_across_devices(events_train_classic)

    print("-------- BLE --------")
    events_train_ble_eq = build_datasets.equilibrate_events_across_devices(events_train_ble)

    events = [events_train_classic, events_train_ble, events_train_classic_eq, events_train_ble_eq, events_test_classic, events_test_ble]
    build_datasets.cache(CACHE_FILE, events)

[events_train_classic, events_train_ble, events_train_classic_eq, events_train_ble_eq, events_test_classic, events_test_ble] = events

# ===============================
# Functions

def build_features_labels_dataset(events, adversary_capture_duration=-1):
    data = []
    labels = []
    # shape: data is a [[Features], [Features], ...]
    for device in events:
        for app in events[device]:
            for action in events[device][app]:
                for event in events[device][app][action]:
                    features_dict = feature_extraction.extract_features_short(event, adversary_capture_duration)
                    features = list(features_dict.values())
                    data.append(features)
                    labels.append(device)
    return [data, labels]

# Fit Random Forest
def random_forest(events_train_eq, X_train, y_train, X_test, y_test, seed=0, n_trees=100):
    clf=RandomForestClassifier(n_estimators=n_trees, random_state=seed)
    clf.fit(X_train,y_train)
    y_pred=clf.predict(X_test)

    accuracy = metrics.accuracy_score(y_test, y_pred)
    feature_importance = pd.Series(clf.feature_importances_,index=feature_extraction.get_list_of_feature_names_short(events_train_eq))
    feature_importance = feature_importance.sort_values(ascending=False)
    
    return accuracy, feature_importance[0:10], y_pred

# Plot Confusion Matrix
def confusion_matrix(events_train_eq, events_test, seed=0, n_trees=100, show=True, output="confusion-matrix.png", adversary_capture_duration=-1):

    X_train, y_train = build_features_labels_dataset(events_train_eq, adversary_capture_duration)
    X_test, y_test = build_features_labels_dataset(events_test, adversary_capture_duration)

    print("Sizes:", len(X_train), len(y_train), len(X_test), len(y_test))

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

for duration in [1,5,10,15,20,25,30,60,-1]:
    print("Duration", duration)
    print("-------- Classic --------")
    #print_packet_summary(events_train_classic_eq)
    confusion_matrix(events_train_classic_eq, events_test_classic, show=False, output="confusion-matrix-classic-"+str(duration)+".png", adversary_capture_duration=duration)

    print("-------- BLE --------")
    #print_packet_summary(events_train_ble_eq)
    confusion_matrix(events_train_ble_eq, events_test_ble, show=False, output="confusion-matrix-ble-"+str(duration)+".png", adversary_capture_duration=duration)