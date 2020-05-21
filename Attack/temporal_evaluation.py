import matplotlib.pyplot as plt
import numpy as np

from single_action_helper import plot_confusion_matrix
from evaluate import evaluate
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from sklearn.model_selection import train_test_split


PLOT_DIR = "./plots/"


def plot_temporal_acc_diff(steps, cumul_acc_avg, self_acc_avg, figname):

    plt.scatter(steps, cumul_acc_avg, color="r", label="Accuracy when trained with day 0")
    plt.scatter(steps, self_acc_avg, label="Accuracy when trained with day n")
    plt.ylim([0.8, 1.005])
    plt.xticks(steps)
    plt.ylabel("accuracy")
    plt.xlabel("elapsed time in days")
    plt.legend(loc="lower left")
    plt.title("Accuracy over time")
    plt.savefig(PLOT_DIR + figname, dpi= 180, bbox_inches='tight')
    plt.close()


def plot_difference(cumul_self_true, cumul_self_pred, cumul_true, cumul_pred, figname, steps, clf, by='all', repeat=50):
    print("Evaluation for day : ", by)
    if by!='all':
        idxs = np.where(np.array(steps)== by)
        start = (idxs[0][0]-1) * repeat
        cumul_self_true = cumul_self_true[start: start + repeat]
        cumul_self_pred = cumul_self_pred[start: start + repeat]
        cumul_true = cumul_true[start: start + repeat]
        cumul_pred = cumul_pred[start: start + repeat]

    cumul_true_self_flat = [t for ts in cumul_self_true for t in ts]
    cumul_pred_self_flat = [t for ts in cumul_self_pred for t in ts]
    cumul_true_flat = [t for ts in cumul_true for t in ts]
    cumul_pred_flat = [t for ts in cumul_pred for t in ts]

    print("nb prediction self acc: ", len(cumul_pred_flat))
    print("nb prediction delayed acc: ", len(cumul_pred_self_flat))
    cm_self, a2, a3 = plot_confusion_matrix(cumul_true_self_flat, cumul_pred_self_flat)
    cm, _, _ = plot_confusion_matrix(cumul_true_flat, cumul_pred_flat)

    acc_diff = np.array([])
    for x in range(len(cm)):
        acc_diff = np.append(acc_diff, cm[x,x] -  cm_self[x,x])

    print("average acc. increase: %.2f" % (acc_diff.mean() * 100))

    clf.classes_[np.where(acc_diff<0)]

    clf.classes_[np.where(acc_diff>0.1)]

    fig, ax = plt.subplots(figsize=(12,8))


    sorted_indice = np.argsort(acc_diff)
    sorted_class = clf.classes_[sorted_indice]
    sorted_class= [c.split("_")[0] for c in sorted_class]
 #   sorted_class_idx = [APP_TO_INDEX[c] for c in sorted_class]
    print("worst classes :", sorted_class[:5])
    acc_diff_sorted = acc_diff[sorted_indice]
    first_0 = np.where(acc_diff_sorted == 0)[0][0]
    barlist = plt.bar(x = np.arange(len(acc_diff)), height = acc_diff_sorted, width=0.8, tick_label = "")
    [barlist[i].set_color('r') for i in range(first_0)]
    plt.xlabel("Classes Index", fontsize=17)
    plt.ylabel("Accuracy gain", fontsize=17)

    title = "Accuracy gain per class"
    if by == 'all':
        title += " averaged over all days"
    else:
        title += " on day " + str(by)
    plt.title(title, fontsize=20)
    ax.set( #xticks=np.arange(sorted_class),
               xticklabels=sorted_class)
    plt.xticks(fontsize=15, rotation=90)
    plt.yticks(fontsize=15)
    plt.ylim([-0.7, 0.3])
    plt.savefig(PLOT_DIR + figname + "_j=" +str(by) , dpi=180, bbox_inches='tight')
    plt.close()
    print()




######### MAIN SCRIPT #########


#### without 2 days learning adjustement
print("Accuracy delay without learning adjustement")
DATA_PATH_REF = ["data/huawei/open-6/"]

# Action that where not part of the long-run experiment
DISCARDED_ACTION = ['Calm_open', 'AppInTheAir_open',
                    'Fit_open', 'FitBreathe_open',
                     "FitWorkout_open", 'Qardio_open']



cumul_acc = []
self_acc = []



cumul_true = []
cumul_pred = []

cumul_self_true = []
cumul_self_pred = []




steps = [1, 2, 4, 8, 12, 16, 20, 24, 28, 32]
repeat = 50


X_past, y_past, _ = evaluate(DATA_PATH_REF, DISCARDED_ACTION=DISCARDED_ACTION,
                             RETURN_FEATURES_AND_LABELS=True, PRINT_COUNT=False,
                             EQUALIZATION=True)




clf_past=RandomForestClassifier(n_estimators=200, random_state=None)
clf_past.fit(X_past, y_past)


accuracy, _ = evaluate(DATA_PATH_REF, DISCARDED_ACTION=DISCARDED_ACTION,
                       RATIO=0.3, DATA_SIZE_FILTER=10,
                       RETURN_ACC_AND_CONF=True, N_SPLITS=repeat,
                       EQUALIZATION=False)

cumul_acc += [accuracy] * repeat # already averaged over `repeat` runs by 10-Splits
self_acc += [accuracy] * repeat


for i, step in zip(range(7, 17), steps):
    DATA_PATH_NEW = ["data/huawei/elapsed-time/open-"+str(i)+"/"] # all
    X_new_all, y_new_all, _ = evaluate(DATA_PATH_NEW, DISCARDED_ACTION=DISCARDED_ACTION, EQUALIZATION=False, RETURN_FEATURES_AND_LABELS=True)
    print("day elapsed: ", step)
    for _ in range(repeat):

        # train old model with 7 random stratified samples
        X_past_train, _, y_past_train, _ = train_test_split(X_past,  y_past,
                 stratify=y_past,
                 train_size=30*7)


        clf_past=RandomForestClassifier(n_estimators=200, random_state=None)
        clf_past.fit(X_past_train, y_past_train)

        # test old model with 7 new random stratified samples
        X_new_train, X_new_true, y_new_train, y_new_true = train_test_split(X_new_all,  y_new_all,
                 stratify=y_new_all,
                 test_size=30*3)

        y_new_pred = clf_past.predict(X_new_true)
        accuracy = metrics.accuracy_score(y_new_true, y_new_pred)

        cumul_acc.append(accuracy)
        cumul_true.append(y_new_true)
        cumul_pred.append(y_new_pred)


        # Self accuracy
        clf_new=RandomForestClassifier(n_estimators=200, random_state=None)
        clf_new.fit(X_new_train[:7*30], y_new_train[:7*30])
        y_new_pred = clf_new.predict(X_new_true)
        accuracy = metrics.accuracy_score(y_new_true, y_new_pred)

        cumul_self_true.append(y_new_true)
        cumul_self_pred.append(y_new_pred)
        self_acc.append(accuracy)


cumul_acc_avg = np.array(cumul_acc).reshape((-1,repeat)).mean(axis = 1)
self_acc_avg = np.array(self_acc).reshape((-1,repeat)).mean(axis = 1)


steps = [0, 1, 2, 4, 8, 12, 16, 20, 24, 28, 32]

plot_temporal_acc_diff(steps, cumul_acc_avg, self_acc_avg, "acc_vs_temporal_distance")

bys = steps[1:] + ["all"]
for by in bys:
    plot_difference(cumul_self_true, cumul_self_pred, cumul_true, cumul_pred, figname="acc_vs_temporal_distance_by_class", steps=steps, clf=clf_past, by=by, repeat=repeat)






#### without 2 days learning adjustement
print("Accuracy delay with learning adjustement (might take up to 20min)")

DATA_PATH_REF_1 = ["data/huawei/open-6/"] #, "./data/huawei/Shazam_openFound/",  "data/huawei/DCLM_openError/"]
DATA_PATH_REF_2 = ["data/huawei/elapsed-time/open-7/"]
DATA_PATH_REF_3 = ["data/huawei/elapsed-time/open-8/"]
DATA_PATH_REF = DATA_PATH_REF_1 + DATA_PATH_REF_3 + DATA_PATH_REF_3

DISCARDED_ACTION = ['Calm_open', 'AppInTheAir_open', 'Fit_open', 'FitBreathe_open', "FitWorkout_open", 'Qardio_open']

cumul_acc_mix = []
self_acc_mix = []



cumul_true_mix = []
cumul_pred_mix = []

cumul_self_true_mix = []
cumul_self_pred_mix = []




steps = [4 , 8, 12, 16, 20, 24, 28, 32]
repeat = 50


X_past_1, y_past_1, _ = evaluate(DATA_PATH_REF, DISCARDED_ACTION=DISCARDED_ACTION, RETURN_FEATURES_AND_LABELS=True, PRINT_COUNT=False, EQUALIZATION=False)
X_past_2, y_past_2, _ = evaluate(DATA_PATH_REF, DISCARDED_ACTION=DISCARDED_ACTION, RETURN_FEATURES_AND_LABELS=True, PRINT_COUNT=False, EQUALIZATION=False)
X_past_3, y_past_3, _ = evaluate(DATA_PATH_REF, DISCARDED_ACTION=DISCARDED_ACTION, RETURN_FEATURES_AND_LABELS=True, PRINT_COUNT=False, EQUALIZATION=False)


X_past_train_1, _, y_past_train_1, _ = train_test_split(X_past_1,  y_past_1,  stratify=y_past_3, train_size=30*3)
X_past_train_2, _, y_past_train_2, _ = train_test_split(X_past_2,  y_past_2,  stratify=y_past_3, train_size=30*2)
X_past_train_3, _, y_past_train_3, _ = train_test_split(X_past_3,  y_past_3,  stratify=y_past_3, train_size=30*2)

X_past_train = X_past_1 + X_past_2 + X_past_3
y_past_train = y_past_1 + y_past_2 + y_past_3



accuracy, _ = evaluate(DATA_PATH_REF, DISCARDED_ACTION=DISCARDED_ACTION, RATIO=0.3, DATA_SIZE_FILTER=10, RETURN_ACC_AND_CONF=True, N_SPLITS=repeat, PRINT_COUNT=False, EQUALIZATION=False)
cumul_acc_mix += [accuracy] * repeat # already averaged over 10 runs by 10-Splits
self_acc_mix += [accuracy] *  repeat


for i, step in zip(range(9, 17), steps):
    DATA_PATH_NEW = ["data/huawei/elapsed-time/open-"+str(i)+"/"] # all
    X_new_all, y_new_all, _ = evaluate(DATA_PATH_NEW, DISCARDED_ACTION=DISCARDED_ACTION, EQUALIZATION=False, RETURN_FEATURES_AND_LABELS=True)
    print("day elapsed: ", step)
    for _ in range(repeat):

        # train old model with 7 random stratified samples
        X_past_train_1, _, y_past_train_1, _ = train_test_split(X_past_1,  y_past_1,  stratify=y_past_1, train_size=30*3)
        X_past_train_2, _, y_past_train_2, _ = train_test_split(X_past_2,  y_past_2,  stratify=y_past_2, train_size=30*2)
        X_past_train_3, _, y_past_train_3, _ = train_test_split(X_past_3,  y_past_3,  stratify=y_past_3, train_size=30*2)

        X_past_train = X_past_1 + X_past_2 + X_past_3
        y_past_train = y_past_1 + y_past_2 + y_past_3

        clf_past=RandomForestClassifier(n_estimators=200, random_state=None)
        clf_past.fit(X_past_train, y_past_train)

        # test the old model with 3 new random stratified samples
        X_new_train, X_new_true, y_new_train, y_new_true = train_test_split(X_new_all,  y_new_all, stratify=y_new_all, test_size=30*3)

        y_new_pred = clf_past.predict(X_new_true)
        accuracy = metrics.accuracy_score(y_new_true, y_new_pred)

        cumul_acc_mix.append(accuracy)
        cumul_true_mix.append(y_new_true)
        cumul_pred_mix.append(y_new_pred)


        # Self accuracy
        clf_new=RandomForestClassifier(n_estimators=200, random_state=None)
        clf_new.fit(X_new_train[:7*30], y_new_train[:7*30])
        y_new_pred = clf_new.predict(X_new_true)
        accuracy = metrics.accuracy_score(y_new_true, y_new_pred)

        cumul_self_true_mix.append(y_new_true)
        cumul_self_pred_mix.append(y_new_pred)
        self_acc_mix.append(accuracy)

steps = [0, 4, 8, 12, 16, 20, 24, 28, 32]

cumul_acc_avg_mix = np.array(cumul_acc_mix).reshape((-1,repeat)).mean(axis = 1)
self_acc_avg_mix = np.array(self_acc_mix).reshape((-1,repeat)).mean(axis = 1)

plot_temporal_acc_diff(steps, cumul_acc_avg_mix, self_acc_avg_mix, "acc_vs_temporal_distance_adjusted")

bys = steps[1:] + ["all"]
for by in bys:
    plot_difference(cumul_self_true_mix, cumul_self_pred_mix, cumul_true_mix, cumul_pred_mix, figname="acc_vs_temporal_distance_by_class_adjusted", steps=steps, clf=clf_past, by=by, repeat=repeat)
