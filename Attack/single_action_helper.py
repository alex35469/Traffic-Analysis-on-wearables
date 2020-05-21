import numpy as np
import random
from build_datasets import *
import csv
from copy import deepcopy
from feature_extraction import extract_features
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support, ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split, ShuffleSplit, cross_val_score
from sklearn.utils.multiclass import unique_labels



#### Imports helper

def merge_actions(events, to_merge, names=None):
    if not names:
        names = [None] * len(to_merge)
    for actions, name in zip(to_merge, names):
        events = merge_action(events, actions, name)
    return events


def merge_action(events, to_merge, name=None, EQUALIZATION=True):
    """
    Merge actions in to_merge from events.
    Args:
        name : Tuple(AppName, ActionName). Name of the merged Application and Action
        events: dict
        to_merge : [app_action,]. Action to merge

    Cannot merge across apps
    """

    # prepare if Equalization is needed
    if EQUALIZATION:
        events, _ = equilibrate_events_across_apps_and_watch(events, SELECTIVE_ACTION=to_merge)

    events_out = deepcopy(events)

    for w in events:
        merged_actions = []
        app_merged = "NoApp"
        action_merged = ""

        for app in events[w]:
            for action in events[w][app]:
                if app+'_'+action in to_merge:
                    action_merged += action[:5].capitalize()
                    merged_actions += events[w][app][action]
                    del events_out[w][app][action]
        if name:
            app_merged = name.split("_")[0]
            action_merged = name.split("_")[1]
        if app_merged not in events_out[w]:
            events_out[w][app_merged] = dict()
        if action_merged not in events_out[w]:
            events_out[w][app_merged][action_merged] = dict()
        events_out[w][app_merged][action_merged] = merged_actions

    return events_out



def discard_actions(source_files, to_discard):
    sf_new = []
    for f in source_files:
        _in = False
        for df in to_discard:
            if df in f:
                _in = True
        if not _in:
            sf_new.append(f)
    return sf_new



def separate_watch(events):
    """Separate events across datat"""

    if len(events.keys()) <= 1:
        print("Only 1 watch. Cannot separate")
        return events
    events_out = dict()

    all_devices = "-".join([device for device in events])
    events_out[all_devices] = dict()

    # dict init
    for device in events:
        for app in events[device]:
            for action in events[device][app]:

                if not app in events_out[all_devices]:
                    events_out[all_devices][device+"_"+app] = dict()
                if not action in events_out[all_devices][device+"_"+app]:
                    events_out[all_devices][device+"_"+app][action] = events[device][app][action]
    return events_out


def delete_different_action_across_watch(events):
        # Create common action set if multiple watches
    intersection_set = set()
    for i, w in enumerate(events):
        all_action = []
        for app in events[w]:
            actions = set(events[w][app].keys())
            all_action += [app + "_" + act for act in actions]
        if i == 0:
            intersection_set = set(all_action)
        else:
            intersection_set = intersection_set.intersection(set(all_action))

    events_copy = deepcopy(events)
    # Delete not common action from dictionnary
    for device in events_copy:
        for app in events_copy[device]:
            for action in events_copy[device][app]:
                if app + "_" + action not in intersection_set:
                    del events[device][app][action]
    return events



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


def filter_by_length(events, minimum_payload=200, ratio_app_not_satisfing_minimum_payload_length=0.25, printInfo = False):
    results = deepcopy(events)
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


def filer_by_data_size(events, N_TO_PICK):

    results = deepcopy(events)
    for watch in events:
        for app in events[watch]:
            for action in events[watch][app]:
                if len(events[watch][app][action]) < N_TO_PICK or N_TO_PICK == -1:
                    if N_TO_PICK != -1:
                        print("N_TO_PICK too large. Took all the dataset for " + app + "_" + action ," instead")
                    continue
                else:
                    chosen_indices = random.sample(range(len(events[watch][app][action])), N_TO_PICK)
                    chosen_events = list(np.array(events[watch][app][action])[chosen_indices])
                results[watch][app][action] = chosen_events
    return results




def plot_confusion_matrix(y_true, y_pred, normalize=True,
                          title=True, figname = None,
                          figsize=(20,20), PLOT_DIR="./plots/",
                          ORDERED_LABELS=None, CM_NO_LABELS=False,
                          CM_ALL_LABEL=False,
                          APP_TO_INDEX=False, SPACING=2):
    cm, fig, ax = None, None, None
    # Compute confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=ORDERED_LABELS)

    # Only use the labels that appear in the data
    classes = unique_labels(y_true, y_pred)
    if ORDERED_LABELS:
        classes = ORDERED_LABELS
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    if CM_ALL_LABEL:
        fig, ax = plt.subplots(figsize=figsize, dpi= 180)
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

        fmt = '.2f' if normalize else 'd'
        thresh = cm.max() / 2.
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(j, i, format(cm[i, j], fmt),
                        ha="center", va="center",
                        color="white" if cm[i, j] > thresh else "black")

        # Rotate the tick labels and set their alignment.
        #plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
        #         rotation_mode="anchor")

        if figname is not None:
            plt.savefig(PLOT_DIR+figname)
            print("Saved image", PLOT_DIR+figname+".png")

    if CM_NO_LABELS:
        fig, ax = plt.subplots(figsize=figsize, dpi= 180)
        ax.imshow(cm, interpolation='none', aspect='auto', cmap=plt.cm.Blues)
        ax.tick_params(axis="both", which='both', bottom=False, top=False, labelbottom=False)
        plt.yticks([])
        if figname is not None:
            plt.savefig(PLOT_DIR+figname+"_nolabels")
            print("Saved image", PLOT_DIR+figname+"_nolabels.png")

    if APP_TO_INDEX:
        fig, ax = plt.subplots(figsize=figsize, dpi= 180)
        index_labels = [APP_TO_INDEX[l] for i, l in enumerate(classes) if i % SPACING == 0]
        im = ax.imshow(cm, interpolation='none', aspect='auto', cmap=plt.cm.Blues)
        #fig.colorbar(im, ax=ax)
        divider = make_axes_locatable(ax)

        ax.set(xticks=np.arange(cm.shape[1]//SPACING) * SPACING,
               yticks=np.arange(cm.shape[0]//SPACING) * SPACING,
               xticklabels=index_labels, yticklabels=index_labels)

        cax = divider.append_axes("right", size="3%", pad=0.05)
        cb = plt.colorbar(im, cax=cax)
        cb.ax.tick_params(labelsize=figsize[0] * 1.2)
        ax.set_xlabel(xlabel='Predicted label index', labelpad=20, fontsize=figsize[0] * 1.5)
        ax.set_ylabel(ylabel='True label index', labelpad=20, fontsize=figsize[0] * 1.5)
        ax.tick_params(labelsize=figsize[0] * 1.2)
        ax.set_title(title, fontsize=figsize[0] * 2)
        if figname is not None:
            plt.savefig(PLOT_DIR+figname+"_index", bbox_inches='tight')
            print("Saved image", PLOT_DIR+figname+"_index.png")
    return cm, fig, ax


def count_print(events):
    nb_categories = 0
    for d in events:
        for app in events[d]:
            nb_categories += len(events[d][app])
            for act in events[d][app]:
                print("{}: {}_{} - {}".format(d, app, act,  len(events[d][app][act])))
    print("Nb class = ", nb_categories)




def plot_acc_and_conf(steps, accuracies, confs, repeat,
                      title=None, xlabel=None, ylabel=None, fname=None, y_lim=None, dpi=500):

    accuracies = np.array(accuracies)
    confs = np.array(confs)

    accuracies_avg = accuracies.reshape((-1,repeat)).mean(axis = 1)
    confs_avg = confs.reshape((-1,repeat)).mean(axis = 1)

    conf_upper = accuracies_avg + confs_avg
    conf_lower = accuracies_avg - confs_avg

    fig, ax = plt.subplots()
    ax.plot(steps, accuracies_avg, '-b', label='averaged accuracy')
    ax.plot(steps, conf_upper, '--r', label='95% confidence interval')
    ax.plot(steps, conf_lower, '--r')
    plt.title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    if y_lim is not None:
        plt.ylim(y_lim[0], y_lim[1])
    leg = ax.legend()

    plt.savefig("./"+fname, dpi=dpi)



def feat_filter(X, f_name, to_withdraw):
    """
    Withdraw features specified in to withdraw
    Args:
        X: [[X1_f1,],] dataset
        f_name : [f1,] feature names
        to_withdraw: [i1,] index of features to withdraw
    Return:
        X_new, f_name_new : Args filtered
    """
    X, f_name, to_withdraw = np.array(X), np.array(f_name), np.array(to_withdraw)
    mask = np.ones(len(f_name), np.bool)
    mask[to_withdraw] = 0
    return X[:,mask].tolist(), f_name[mask].tolist()



#########################

def median_length_order(events):
    n_and_s = []
    l_min = 999999999
    i_min =-1
    for w in events:
        for app in events[w]:
            for action in events[w][app]:
                name = app + "_" + action
                sizes = []
                for i, event in enumerate(events[w][app][action]):
                    ys = np.array(event["ys"])
                    sizes.append(sum(abs(ys)))
                n_and_s.append((name, np.median(sizes)))
    n_and_s = sorted(n_and_s, key = lambda x : x[1])
    n_sorted = [n for n,s in n_and_s]
    s_sorted = [s for n,s in n_and_s]
    return n_sorted, s_sorted


def time_serie_filtering(events, packet_min_length= 0, n_same_consecutive_packet_length=None):
    l_min = 999999999
    i_min =-1
    events_new = deepcopy(events)
    for w in events:
        for app in events[w]:
            for action in events[w][app]:
                new_event_list = []
                for event in events[w][app][action]:
                    xs = np.array(event['xs'])
                    ys = np.array(event['ys'])
                    xs = xs[np.argwhere(abs(ys)  >= packet_min_length)]
                    ys = ys[np.argwhere(abs(ys)  >= packet_min_length)]
                    d = dict()
                    d['xs'] = xs.flatten().tolist()
                    d['ys'] = ys.flatten().tolist()
                    new_event_list.append(d)
                events_new[w][app][action] = new_event_list
    return events_new


def equilibrate_events_across_apps_and_watch(events, SELECTIVE_ACTION=None, equilibrate_events_across_apps_and_watch=None):
    """
    Equilibrate the events by identifing the minimum number of samples per class
    and discarding Randomly the extra samples.
    If there are multiple watchs, only the common application are kept

    Parameters:
        events (dict[watch][app][action] -> event): dataset
        SELECTIVE_ACTION ["app_action",] : only equalized on selective events

    Returns:
        events (dict[watch][app][action] -> event): equilibrate dataset
    """

    events = delete_different_action_across_watch(events)

    # Find minimum samples
    counts = dict()
    for device in events:
        for app in events[device]:
            for action in events[device][app]:
                counts[device + "_" + app +"_" + action] = 0
            for action in events[device][app]:
                counts[device + "_" + app + "_" + action] += len(events[device][app][action])

    if len(counts.values())== 0:
        return events, -1


    nb_samples_per_cat = min(counts.values())
    if SELECTIVE_ACTION:
        nb_samples_per_cat = nb_samples_per_cat // len(SELECTIVE_ACTION) + 1

    events_out = dict()

    # remove everything above the min across devices
    for device in events:
        for app in events[device]:

            for action in events[device][app]:

                if not device in events_out:
                    events_out[device] = dict()
                if not app in events_out[device]:
                    events_out[device][app] = dict()
                if not action in events_out[device][app]:
                    if not SELECTIVE_ACTION or app + "_" + action in SELECTIVE_ACTION:
                        events_out[device][app][action] = random.sample(events[device][app][action], k=nb_samples_per_cat)
                    else:
                        events_out[device][app][action] = events[device][app][action]

    return events_out, nb_samples_per_cat



def build_features_labels_dataset(events, unique_from=46, unique_to=1006,
                                  unique_granularity=1, unique_deltas=[0,46], to_withdraw=[]):
    data = []
    labels = []
    feature_names = None
    for device in events:
        for app in events[device]:
            for action in events[device][app]:
                label = app + "_" + action
                for event in events[device][app][action]:
                    features_dict = extract_features(event,
                                                     unique_from, unique_to,
                                                     unique_granularity, unique_deltas=unique_deltas,
                                                     to_withdraw=to_withdraw
                                                    )
                    features = list(features_dict.values())
                    data.append(features)
                    labels.append(label)
                    if feature_names is None:
                        feature_names = list(features_dict.keys())

    return data, labels, feature_names



def filter_feature_by_importance(X, y, feature_names, RATIO_FILTER_FEATURE,  N_ESTIMATOR, TEST_PERCENTAGE, RANDOM_STATE, DETAIL_PRINT):

    clf = build_train_clf(X, y, N_ESTIMATOR, TEST_PERCENTAGE, RANDOM_STATE, DPRINT=False)
    feature_names = np.array(feature_names)
    # filter ratio
    features_importance = clf.feature_importances_
    to_withdraw = np.where(features_importance<=RATIO_FILTER_FEATURE)[0]
    X, feature_names_new = feat_filter(X, feature_names, to_withdraw)

    if DPRINT:
        print(len(feature_names) - len(feature_names_new), " features removed")

        clf = build_train_clf(X, y, N_ESTIMATOR, TEST_PERCENTAGE, RANDOM_STATE)
        # Accuracy eval.
        shuf_split = ShuffleSplit(n_splits=30, test_size=TEST_PERCENTAGE, random_state=RANDOM_STATE)
        scores_shuffle = cross_val_score(clf, X, y, cv=shuf_split)

        print("Random split cross-validation: Accuracy=%0.3f (+/- %0.2f). " % (scores_shuffle.mean(), scores_shuffle.std() * 2))

    return X, y, feature_names_new, feature_names[to_withdraw]


def build_train_clf(X, y, N_ESTIMATOR, TEST_PERCENTAGE, RANDOM_STATE):
    clf=RandomForestClassifier(n_estimators=N_ESTIMATOR, random_state=RANDOM_STATE)
    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=TEST_PERCENTAGE, random_state=RANDOM_STATE)
    clf.fit(X_train, y_train)
    return clf
