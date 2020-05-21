from evaluate import *
from single_action_helper import plot_confusion_matrix

def merge_predicted_fit_label(y_true, y_pred):
    y_true = [y if not "Fit" in y else "Fit_open" for y in y_true]
    y_pred = [y if not "Fit" in y else "Fit_open" for y in y_pred]
    return y_true, y_pred



### SETUP
# build class index dict
APP_TO_INDEX = build_app_to_index_dict()

DATA_PATH_FOSSIL = ["data/fossil/open-6/"]
DATA_PATH_HUAWEI = ["data/huawei/open-6/"]


DATA_PATH = DATA_PATH_FOSSIL + DATA_PATH_HUAWEI # ["data/fossil/open-6/","data/huawei/open-6/"]#, "data/huawei/elapsed-time/open-7/","data/huawei/elapsed-time/open-8/", "data/huawei/elapsed-time/open-9/", "data/huawei/elapsed-time/open-10/","data/huawei/elapsed-time/open-11/",  "data/huawei/elapsed-time/open-12/", "data/huawei/elapsed-time/open-13/"]
DISCARD = [] # ["FindMyPhone_open", "Running_open", "Strava_open"]
TO_MERGED = [] # [["FitWorkout_open", "Fit_open", "FitBreathe_open"]]
Names =  []# ["FitPackages_open"]
UNIQUE_DELTAS = [1005, 46, 0] #, 195, 106, 279, 194, 254, 861]
equilibrate_events = evaluate(DATA_PATH, DISCARDED_ACTION=DISCARD, TO_MERGE=TO_MERGED, MERGED_NAMES=Names, EQUALIZATION=True, RETURN_EQUILIBRATE_EVENTS=True, PRINT_COUNT=False)


equilibrate_events_huawei = dict()
equilibrate_events_fossil = dict()

# Separation of the two datasets
equilibrate_events_huawei["LEO-BX9"] = equilibrate_events["LEO-BX9"]
equilibrate_events_fossil["Q-Explorist-HR"] = equilibrate_events["Q-Explorist-HR"]

print("building features and labels (no adaptive filtering)")
X_huawei, y_huawei, f_name = build_features_labels_dataset(equilibrate_events_huawei, unique_deltas=UNIQUE_DELTAS)
X_fossil, y_fossil, _ = build_features_labels_dataset(equilibrate_events_fossil, unique_deltas=UNIQUE_DELTAS)

print("useless features extraction")
to_withdraw_h = find_feat_to_withdraw(DATA_PATH_HUAWEI, N_ATTEMPS_AFTER_EXIT=1, N_ESTIMATOR=1000, MAX_ITERATION=1, DPRINT=False)
to_withdraw_f = find_feat_to_withdraw(DATA_PATH_FOSSIL, N_ATTEMPS_AFTER_EXIT=1, N_ESTIMATOR=1000, MAX_ITERATION=1, DPRINT=False)

#to_withdraw_h = []
#to_withdraw_f = []

print("building filtered features label (adaptive filtering)")
# For train with Huawei
X_huawei_h_filtered, _, _ = build_features_labels_dataset(equilibrate_events_huawei,
                                                    unique_deltas=UNIQUE_DELTAS,
                                                    to_withdraw=to_withdraw_h
                                                   )

X_fossil_h_filtered, _, _ = build_features_labels_dataset(equilibrate_events_fossil,
                                                    unique_deltas=UNIQUE_DELTAS,
                                                    to_withdraw=to_withdraw_h
                                                   )


# For train with Fossil
X_huawei_f_filtered, _, _ = build_features_labels_dataset(equilibrate_events_huawei,
                                                    unique_deltas=UNIQUE_DELTAS,
                                                    to_withdraw=to_withdraw_f
                                                   )

X_fossil_f_filtered, _ , _ = build_features_labels_dataset(equilibrate_events_fossil,
                                                    unique_deltas=UNIQUE_DELTAS,
                                                    to_withdraw=to_withdraw_f
                                                   )


repeat = 10

### Train with huawei, test with Fossil
accs = []
accs_no_fit = []
accs_filtered = []

print("\nTraining with huawei testing with fossil")
for _ in range(repeat):


    # building and training the model for cross validation
    clf_huawei=RandomForestClassifier(n_estimators=1000, random_state=None)
    clf_huawei.fit(X_huawei, y_huawei)
    y_fossil_pred = clf_huawei.predict(X_fossil)
    accuracy = metrics.accuracy_score(y_fossil, y_fossil_pred)
    accs.append(accuracy)



    # With adaptive filtering
    clf_huawei=RandomForestClassifier(n_estimators=1000, random_state=None)
    clf_huawei.fit(X_huawei_h_filtered, y_huawei)
    y_fossil_pred = clf_huawei.predict(X_fossil_h_filtered)

    accuracy = metrics.accuracy_score(y_fossil, y_fossil_pred)
    accs_filtered.append(accuracy)



    # When fit packets are merged
    y_t, y_p = merge_predicted_fit_label(y_fossil, y_fossil_pred)
    accuracy = metrics.accuracy_score(y_t, y_p)
    accs_no_fit.append(accuracy)


accs = np.array(accs)
accs_no_fit = np.array(accs_no_fit)
accs_filtered = np.array(accs_filtered)

print("Results: ")
print("accuracy:\n mean: {:.3f}\n conf: {:.3f}\n".format(np.mean(accs), 2 * np.std(accs)))
print("accuracy no filtered:\n mean: {:.3f}\n conf: {:.3f}\n".format(np.mean(accs_filtered),2 * np.std(accs_filtered)))
print("accuracy no fit:\n mean: {:.3f}\n conf: {:.3f}\n".format(np.mean(accs_no_fit),2 * np.std(accs_no_fit)))


title = "Confusion_Matrix_train_with_Huawei_test_with_Fossil"
saved_title = title.replace(".", "_").replace(" ", "_")
plot_confusion_matrix(y_fossil, y_fossil_pred, title=title.replace("_", " "), figname=title, APP_TO_INDEX=APP_TO_INDEX, CM_ALL_LABEL=True, CM_NO_LABELS=True)




### Train with Fossil, test with Huawei

accs = []
accs_no_fit = []
accs_filtered = []

print("\nTraining with Fossil testing with Huawei")
for _ in range(repeat):


    # building and training the model for cross validation
    clf_fossil=RandomForestClassifier(n_estimators=1000, random_state=None)
    clf_fossil.fit(X_fossil, y_fossil)
    y_huawei_pred = clf_fossil.predict(X_huawei)
    accuracy = metrics.accuracy_score(y_huawei, y_huawei_pred)
    accs.append(accuracy)



    # With adaptive filtering
    clf_fossil=RandomForestClassifier(n_estimators=1000, random_state=None)
    clf_fossil.fit(X_fossil_f_filtered, y_fossil)
    y_huawei_pred = clf_fossil.predict(X_huawei_f_filtered)
    accuracy = metrics.accuracy_score(y_huawei, y_huawei_pred)
    accs_filtered.append(accuracy)

    # When fit packets are merged
    y_t, y_p = merge_predicted_fit_label(y_huawei, y_huawei_pred)
    accuracy = metrics.accuracy_score(y_t, y_p)
    accs_no_fit.append(accuracy)

accs = np.array(accs)
accs_no_fit = np.array(accs_no_fit)
accs_filtered = np.array(accs_filtered)

print("Results: ")
print("\naccuracy:\n mean: {:.3f}\n conf: {:.3f}\n".format(np.mean(accs), 2 * np.std(accs)))
print("accuracy with adaptive filtering:\n mean: {:.3f}\n conf: {:.3f}\n".format(np.mean(accs_filtered),2 * np.std(accs_filtered)))
print("accuracy no fit:\n mean: {:.3f}\n conf: {:.3f}\n".format(np.mean(accs_no_fit),2 * np.std(accs_no_fit)))

title = "Confusion_Matrix_train_with_Fossil_test_with_Huawei"
saved_title = title.replace(".", "_").replace(" ", "_")
plot_confusion_matrix(y_huawei, y_huawei_pred, title=title.replace("_", " "), figname=title, APP_TO_INDEX=APP_TO_INDEX, CM_ALL_LABEL=True, CM_NO_LABELS=True)
