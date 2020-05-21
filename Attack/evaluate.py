import sys

from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, ShuffleSplit, cross_val_score
import time
from single_action_helper import *


############################## HELPERS FUNCTION ##########################

def build_app_to_index_dict(apple_only=False):
    """
    Create dict[app_action] -> index for confusion matrix (related to )
    """

    c = 0
    if apple_only:
        c=72
    app_to_index = dict()
    def fill_dict(events, c):
        for device in events:
            for app in events[device]:
                for action in events[device][app]:
                    c+=1
                    label = app+"_"+action
                    if label in app_to_index:
                        label += "_"+device
                    app_to_index[label] = c
        return c

    if not apple_only:
        DATA_PATH = "data/huawei/open-3/"
        DISCARDED_ACTION = ["NoApp_NoAction"]
        events = evaluate(DATA_PATH, DISCARDED_ACTION=DISCARDED_ACTION, RETURN_EVENTS=True)
        c = fill_dict(events, c)

        DATA_PATH = ["data/huawei/Endomondo-1/", "data/huawei/DiabetesM-2/",
                     "data/huawei/FoursquareCityGuide-1/", "data/huawei/HealthyRecipes-1/",
                     "data/huawei/Lifesum-1/", "data/huawei/Playstore-1/"]
        events = evaluate(DATA_PATH, RETURN_EVENTS=True)
        c = fill_dict(events, c)

    DATA_PATH = ["data/iwatch/batch-1/"]
    events = evaluate(DATA_PATH, RETURN_EVENTS=True)
    c = fill_dict(events, c)


    return app_to_index

def find_feat_to_withdraw(DATA_PATH, UNIQUE_DELTAS = [0,46,1005],
                          N_ESTIMATOR = 200, STOP_REMOVING_FROM = 0, N_ATTEMPS_AFTER_EXIT=30,
                          TEST_PERCENTAGE = 0.25, RANDOM_STATE = None, DPRINT=False, MAX_ITERATION=1):
    """
    Adaptive Filtering. Removing features with no-importances.

    """

    print("Adaptive feature filtering. (might take up to 1min)")
    to_withdraw = np.array([])
    X, y, feature_names = evaluate(DATA_PATH, DETAIL_PRINT=DPRINT, RETURN_FEATURES_AND_LABELS=True, UNIQUE_DELTAS = [0,46,1005])
    feature_names = np.array(feature_names)
    f_total = len(feature_names)
    zeros_counter = 0
    MAX_ITERATION = MAX_ITERATION if MAX_ITERATION else 999
    for _ in range(MAX_ITERATION):
        clf = build_train_clf(X, y, N_ESTIMATOR, TEST_PERCENTAGE, RANDOM_STATE)

        # filter ratio
        features_importance = clf.feature_importances_
        to_withdraw_tmp = np.where(features_importance<=0)
        to_withdraw = np.append(to_withdraw, feature_names[to_withdraw_tmp])
        X, feature_names = feat_filter(X, feature_names, to_withdraw_tmp)
        print("{} features removed out of {}.".format(len(to_withdraw_tmp[0]),f_total))

        if len(to_withdraw_tmp[0]) <= STOP_REMOVING_FROM:
            zeros_counter += 1
            if zeros_counter >= N_ATTEMPS_AFTER_EXIT:
                return to_withdraw
    return to_withdraw

############################## MAIN FUNCTION ##########################

def evaluate(DATA_PATH, DISCARDED_ACTION=None, TO_MERGE=None, MERGED_NAMES=None,
             EQUALIZATION=True, TEST_PERCENTAGE=0.25, MINIMUM_PAYLOAD=200, RANDOM_STATE=None,
             UNIQUE_DELTAS=[0,46, 1005], UNIQUE_LENGTH_FROM=46, SPLIT_CRITERION='gini',
             MAX_FEATURES='auto', RATIO_FILTER_FEATURE=None, TO_WITHDRAW=[],
             APP_TO_INDEX=False, CM_ALL_LABEL = False,
             FILTER_FEATURE=None, ORDER_CM_BY_SIZE=None, TIME_SERIE_FILTERING = None,
             KEEP_RATIO_ACROSS_DIRECTORIES=False, DATA_SIZE_FILTER=None, SHUFFLE=False,
             RATIO=0.25, N_SPLITS=5, N_ESTIMATOR=200, SEPARATE_WATCH=False, PRINT_COUNT=False,
             figsize=(20,20), figname=None, TITLE=None, PLOT_DIR="./plots/", CM_NO_LABELS=False,
             RETURN_MERGED_EVENTS=False, RETURN_EVENTS=None, RETURN_PRED=False,
             RETURN_FILTIRED=False, RETURN_ACC_AND_CONF=False, RETURN_CLF=False, RETURN_CM=False,
             RETURN_EQUILIBRATE_EVENTS=False, RETURN_FEATURES_AND_LABELS=False, DETAIL_PRINT=False,
             SPACING=2

            ):
    """
    Represents the Attack on single-action captures.

    Given a bunch of path leading to dirctories with .csv captures extracted from ellysis software (.btt), load

    Args:
        checkeds: [[t, action],]. The manullay checked ground truth content
        gts: [[t,action],]. The generated ground truth content
        all_actions: [action,]. List of actions that are part of the training set. (Use as a filter).
    Return:
        recording: [diff,]. List of int representing the delay between ground truth and checked ground truth.
    """

    # print helper
    def dprint(c):
        if DETAIL_PRINT or PRINT_COUNT:
            print(c)

    #### IMPORTS
    dprint("\nimporting data...")
    sources_files = find_sources(DATA_PATH)


    if DISCARDED_ACTION:
        dprint("withdraw action to be discarded")
        sources_files = discard_actions(sources_files, DISCARDED_ACTION)

    events, counts = cut_all_datasets_in_events(sources_files)

    if RETURN_EVENTS:
        return events

    dprint("filtering app that does not send traffic by their length")
    filtered_events = filter_by_length(events, minimum_payload=MINIMUM_PAYLOAD, ratio_app_not_satisfing_minimum_payload_length=RATIO)

    ### GLOBAL FILTERING AND PROCESSING
    if DATA_SIZE_FILTER:
        filtered_events = filer_by_data_size(filtered_events, DATA_SIZE_FILTER)

    if RETURN_FILTIRED:
        return filtered_events

    if TO_MERGE:
        dprint("merging events")
        filtered_events = merge_actions(filtered_events, TO_MERGE, MERGED_NAMES)

    if RETURN_MERGED_EVENTS:
        return events

    if PRINT_COUNT:
        dprint("\nclass event count")
        count_print(filtered_events)
        dprint("")

    nb_samples_per_cat = "not uniform"
    if EQUALIZATION:
        dprint("dataset equalization per class")
        filtered_events, nb_samples_per_cat = equilibrate_events_across_apps_and_watch(filtered_events)

        dprint("samples per classes: {}".format(nb_samples_per_cat))

        if PRINT_COUNT:
            dprint("\nclass event count after equalization")
            count_print(filtered_events)
            dprint("")
        if RETURN_EQUILIBRATE_EVENTS:
            return filtered_events

    if SEPARATE_WATCH:
        dprint("separate watch action")
        filtered_events = separate_watch(filtered_events)
        if PRINT_COUNT:
            count_print(filtered_events)

    dprint("building features and labels")
    if TIME_SERIE_FILTERING:
        filtered_events = time_serie_filtering(filtered_events, packet_min_length=TIME_SERIE_FILTERING, n_same_consecutive_packet_length=None)


    #### FEATURES FILTERING
    X, y, feature_names = build_features_labels_dataset(filtered_events, unique_from=UNIQUE_LENGTH_FROM, unique_deltas=UNIQUE_DELTAS, to_withdraw=TO_WITHDRAW)


    dprint("features count : " + str(len(feature_names)))
    if RATIO_FILTER_FEATURE or RATIO_FILTER_FEATURE == 0:
        dprint("filtering non important features")
        X, y, feature_names, to_withdraw = filter_feature_by_importance(X, y, feature_names, RATIO_FILTER_FEATURE,  N_ESTIMATOR, TEST_PERCENTAGE, RANDOM_STATE, DETAIL_PRINT)
        return X, y, feature_names, to_withdraw


    if RETURN_FEATURES_AND_LABELS:
        return X, y, feature_names

    # Accuracy with cross validation
    dprint("building and training the model for cross validation ")
    clf=RandomForestClassifier(n_estimators=N_ESTIMATOR, criterion=SPLIT_CRITERION, max_features=MAX_FEATURES, random_state=RANDOM_STATE)
    shuf_split = ShuffleSplit(n_splits=N_SPLITS, test_size=RATIO, random_state=RANDOM_STATE)
    scores_shuffle = cross_val_score(clf, X, y, cv=shuf_split)
    dprint("Random split cross-validation: Accuracy=%0.3f (+/- %0.3f). " % (scores_shuffle.mean(), scores_shuffle.std() * 2))
    eval_metric = "cross-val radomSplit={} accRs={:.1f} +-{:.1f}% 95% conf interval".format(N_SPLITS, scores_shuffle.mean() *100, scores_shuffle.std() * 2 * 100)
    if RETURN_ACC_AND_CONF:
        return scores_shuffle.mean(), scores_shuffle.std() * 2

    dprint("building and training a model for confusion matrix")
    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=RATIO, random_state=RANDOM_STATE)

    clf=RandomForestClassifier(n_estimators=N_ESTIMATOR, criterion=SPLIT_CRITERION, max_features=MAX_FEATURES, random_state=RANDOM_STATE)
    t1 = time.time()
    clf.fit(X_train, y_train)
    t2 = time.time()
    dprint("fitting duration = {:.3f}".format(t2-t1))


    if RETURN_CLF:
        return clf

    t1 = time.time()
    y_pred = clf.predict(X_test)
    t2 = time.time()
    dprint("prediction duration = {:.3f}".format(t2-t1))

    if RETURN_PRED:
        return y_test, y_pred

    accuracy = metrics.accuracy_score(y_test, y_pred)
    dprint("accuracy = {}".format(accuracy))

    title = "Confusion matrix for {}acc={:0.2f} ".format(" ".join([f.replace("data/", "").replace("/", "_") for f in DATA_PATH]), accuracy * 100)
    title += eval_metric
    title += "test={}% minimum_payload={}B nb_samples={}".format(int(TEST_PERCENTAGE * 100), MINIMUM_PAYLOAD, nb_samples_per_cat)
    saved_title = title.replace(".", "_").replace(" ", "_")
    if len(saved_title) > 320:
        saved_title = "all_action_confusion_martix"
    if figname:
        saved_title = figname
    if TITLE or TITLE =="":
        title=TITLE

    if ORDER_CM_BY_SIZE:
        ORDER_CM_BY_SIZE, s_sorted = median_length_order(filtered_events)
        dprint(s_sorted)

    cm, _, _ = plot_confusion_matrix(y_test, y_pred, title= title,
                                     figname = saved_title, figsize=figsize,
                                     PLOT_DIR=PLOT_DIR,
                                     ORDERED_LABELS=ORDER_CM_BY_SIZE,
                                     CM_NO_LABELS=CM_NO_LABELS,
                                     APP_TO_INDEX=APP_TO_INDEX,
                                     SPACING=SPACING,
                                     CM_ALL_LABEL=CM_ALL_LABEL
                                    )
    if ORDER_CM_BY_SIZE:
        return cm, ORDER_CM_BY_SIZE, s_sorted

    if RETURN_CM:
        return cm
    dprint("done")


wrong_args = """Possible args:
    `fossil` : produces results with fossil watch
    `iwatch` : produces results with Apple Watch
    `huawei_inApp` : produces results with huawei watch for in-app actions only
    `huawei_open` : produces results with huawei watch for open actions only
    `huawei` : produces results with huawei watch for all actions"""
if __name__ == '__main__':
    if len(sys.argv) >= 2:

        watch = sys.argv[1]
        if watch not in ["huawei", "huawei_inApp", "huawei_open",  "fossil", "iwatch"] :
            print("Wrong arguments.")
            print(wrong_args)
            sys.exit()
    else:
        print("Wrong number of arguments (got {}, expected 1)".format(len(sys.argv)))
        print(wrong_args)
        sys.exit()




    # build class index dict
    APP_TO_INDEX = build_app_to_index_dict(apple_only=(watch == "iwatch"))
    DATA_PATH_DICT = {  "huawei_open" : ["data/huawei/open-3/"],
                        "huawei_inApp" : ["data/huawei/Endomondo-1/", "data/huawei/DiabetesM-2/",
                                          "data/huawei/DiabetesM-3/", "data/huawei/DiabetesM-4/",
                                          "data/huawei/FoursquareCityGuide-1/", "data/huawei/HealthyRecipes-1/",
                                          "data/huawei/Lifesum-1/", "data/huawei/Playstore-1/"],
                        "huawei" : ["data/huawei/Endomondo-1/", "data/huawei/DiabetesM-2/",
                                    "data/huawei/DiabetesM-3/", "data/huawei/DiabetesM-4/",
                                    "data/huawei/FoursquareCityGuide-1/", "data/huawei/HealthyRecipes-1/",
                                    "data/huawei/Lifesum-1/", "data/huawei/Playstore-1/", "data/huawei/open-3/"],
                        "iwatch" : ["data/iwatch/batch-1/"],
                        "fossil" : ["data/fossil/open-6/"]}
    DATA_PATH = DATA_PATH_DICT[watch]
    title = "Confusion Matrix with {}".format(watch.replace("_", " "))

    to_withdraw = find_feat_to_withdraw(DATA_PATH,  MAX_ITERATION=1)
    evaluate(DATA_PATH, DETAIL_PRINT=True, TO_WITHDRAW=to_withdraw, N_SPLITS=50,
             TITLE=title, figname=title.replace(" ", "_"),
             APP_TO_INDEX=APP_TO_INDEX, CM_NO_LABELS=True,
             CM_ALL_LABEL=True, N_ESTIMATOR=200)
