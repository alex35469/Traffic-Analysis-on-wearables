#### IMPORTS
import glob
import csv
import pandas as pd
import numpy as np
from build_datasets import *
from feature_extraction import extract_features
import matplotlib.pyplot as plt
from collections import Counter


def new_packet(columns):
    packet = dict()
    for column in columns:
        packet[column] = ""

    return packet



def extract_payload_length(payload_string, default=0):
    payload_string = payload_string.strip()
    if payload_string == "" or "No data" in payload_string:
        return default
    parts = payload_string.split(' ')
    return toInt(parts[0])


def packet_store_cleanup(packets): #dataset_packet_store is packetID => packets
    for packet_id in packets:
        layers = packets[packet_id]
        for layer in layers:
            layer[ID_COLUMN] = toInt(layer[ID_COLUMN])
            layer["Time"] = toFloat(layer["Time"], default=-1)
            layer["Time delta"] = toFloat(layer["Time delta"], default=-1)
            layer["PayloadLength"] = extract_payload_length(layer["Payload"], default=0)
            layer["PayloadRaw"] = extract_payload_bytes(layer["Payload"])
    return packets


def packets_to_timesize_tuples(packets, wprint=True):
    global master
    xy = dict(xs=[], ys=[])
    packets_ids = list(packets.keys())
    packets_ids.sort(reverse=False)

    # Ensure that the direction stays the same even if HUAWEI Watch becomes master


    for packet_id in packets_ids:
        for layer in packets[packet_id]:
            master = extract_master(layer["Communication"])
            if master in POSSIBLE_MASTERS:
                direction = 1
            else:
                if wprint:
                    print("WARNING master not in Possible masters: '" + master + "'")
                    print(layer["Communication"])
                direction = -1

            if not "master" in layer['Transmitter'].lower():
                direction *= -1
            xy['xs'].append(float(layer['Time']))
            xy['ys'].append(direction * int(layer['PayloadLength']))
    return xy
def build_features_labels_dataset(events, adversary_capture_duration=-1, unique_from=46, unique_to=1006, unique_granularity=1):
    data = []
    labels = []
    feature_names = None
    for device in events:
        for app in events[device]:
            for action in events[device][app]:
                label = app + "_" + action
                for event in events[device][app][action]:
                    features_dict = extract_features(event, adversary_capture_duration, unique_from, unique_to, unique_granularity)
                    features = list(features_dict.values())
                    data.append(features)
                    labels.append(label)
                    if feature_names is None:
                        feature_names = list(features_dict.keys())

    return data, labels, feature_names

def read_file(dataset_file, columns):
    """
    Reads a .csv file and puts its raw contents in packet_store[dataset_file]
    """
    ID_COLUMN = "Packet #"
    dataset_packet_store = dict() # packetID => packets
    headers = []
    with open(dataset_file, "r") as file:
        reader = csv.reader(file, delimiter=',', quotechar='"')

        for i, line in enumerate(reader):
            if i == 0:
                headers = line
                continue

            packet = new_packet(columns)

            for j, item in enumerate(line):
                key = headers[j]
                val = item

                if key not in packet:
                    print(packet)
                    print("Fatal: column '{}' not found in packet; all_columns is {}".format(key, columns))
                    sys.exit(1)
                packet[key] = val

            packet_id = toInt(packet[ID_COLUMN].replace('\'', ''))
            if packet_id not in dataset_packet_store:
                dataset_packet_store[packet_id] = []

            dataset_packet_store[packet_id].append(packet)

    return dataset_packet_store


def extract_columns(dataset_file):
    all_columns = set()

    with open(dataset_file, "r") as file:
        csv_reader = csv.reader(file, delimiter=',', quotechar='"')
        for i, line in enumerate(csv_reader):
            all_columns.update(line)
            return all_columns

def filter_out_path(fs, filter_out_device = False):
    f = fs[fs.rfind('/')+ 1:]
    if filter_out_device:
        f = f[f.rfind('_')+ 1:]
    return f


def extract_fname(f):
    "Extract the name of a file (filter out the path and the extention.)"
    return filter_out_path(f[:f.rfind(".")])

def read_longrun_log_file(longrunLogFile, all_action=None, MERGED_FORCE_STOP=None):
    """
    Args:
        longrunLogFile : File log name (including path)
        all_action : actions used to train the model (needed to filter out actions not part of the training set)

    Return
        [[time, action],] : filtered and clean version of the content of a logfile
    """
    out = []
    with open(longrunLogFile, "r") as file:
        csv_reader = csv.reader(file, delimiter=',', skipinitialspace=True)
        next(csv_reader)
        for i, line in enumerate(csv_reader):
            if MERGED_FORCE_STOP and line[1] in MERGED_FORCE_STOP:
                line[1] = "AllApps_force-stop"
            if all_action is None or line[1] in all_action:

                out.append(line)
    return out


def read_longrun_log_files(longrunLogFiles, all_action=None, MERGED_FORCE_STOP=None):
    """
    Args:
        longrunLogFiles : a list of files log names (including path)
        all_action : actions used to train the model (needed to filter out actions not part of the training set)

    Return
        dict[filename] = [[time, action],] : filtered and clean version of the content of multiple logfile
    """
    out = dict()
    for longrunLogFile in longrunLogFiles:
        out[extract_fname(longrunLogFile)] = read_longrun_log_file(longrunLogFile, all_action, MERGED_FORCE_STOP)
    return out

def record_diff_checked_gt(checkeds, gts, all_actions):
    """
    Aggregate and filter the recordings timing difference between checked and ground-truth for one file
    Args:
        checkeds: [[t, action],]. The manullay checked ground truth content
        gts: [[t,action],]. The generated ground truth content
        all_actions: [action,]. List of actions that are part of the training set. (Use as a filter).
    Return:
        recording: [diff,]. List of int representing the delay between ground truth and checked ground truth.
    """
    recordings = []
    for checked, gt in zip(checkeds, gts):
        action = gt[1]
        if action is None:
            print("ERROR: Parsing failure")
            break
        if eval(checked[0]) is None or action not in all_actions:
            continue

        recordings.append(float(checked[0]) - float(gt[0]))  # add the difference between
    return recordings


def record_diff_checked_gts(content_ground_truth_for_boundaries, content_checked_for_boundaries, all_actions):
    """
    Aggregate and filter the recordings timing difference between checked and ground-truth accross all files.
    Args:
        content_ground_truth_for_boundaries: fileName -> [[t, action],]. Dict of the generated ground truth content.
        content_checked_for_boundaries: fileName -> [[action, t],]. Dict of the manullay checked ground truth content
        all_actions: [action,]. List of actions that are part of the training set. (Use as a filter).

    Return:
        recording: [diff,]. List of int representing the delay between ground truth and checked ground truth.
    """
    recordings = []

    for capt in content_checked_for_boundaries:
        checkeds = content_checked_for_boundaries[capt]
        gts = content_ground_truth_for_boundaries[capt]
        recordings += record_diff_checked_gt(checkeds, gts, all_actions)
    return recordings


def make_bound_for_timing_in_action(content_ground_truth, lower, upper):
    """
    Make time boundaries for each action.
    Args:
        content_ground_truth: fileName -> [[t, action],]. Dict of the generated ground truth content.
        lower: lower bound of the first seen traffic emanetaed from a perormed aciton
        upper: upper bound of the first seen traffic emanetaed from a perormed aciton
    Return:
        content_ground_truth_with_bound: fileName -> [[(t_lower, t_upper), action],]. Ground truth with time bounded actions
    """
    content_ground_truth_with_bound = dict()
    for gt in content_ground_truth:
        new_gt = []
        for i, action in content_ground_truth[gt]:
            lower_bound = float(i) + lower
            upper_bound = float(i) + upper
            # Because Appstore apps takes longer time to open, we shift its bound
            if action == "PlayStore_deterministicBrowse":
                lower_bound += 12
                upper_bound += 12

            new_gt.append((lower_bound, upper_bound, action))
        content_ground_truth_with_bound[gt] = new_gt
    return content_ground_truth_with_bound

# Build bounds for groundtruth


def intersection_fname(files1, files2, print_missing=True):
    "Return the list of files names (without extension) that files1 containes and files2 contains"
    if len(files1) == 0 or len(files2) == 0:
        print("WARNING: one or both dir. are empty")
        return []

    extension1 = files1[0][files1[0].rfind("."):]
    extension2 = files2[0][files2[0].rfind("."):]

    files1_filtered = set()
    files2_filtered = set()

    for f1 in files1:
        files1_filtered.add(extract_fname(f1))
    for f2 in files2:
        files2_filtered.add(extract_fname(f2))

    complete_files = files1_filtered.intersection(files2_filtered)
    missing_files = sorted(list(files1_filtered.union(files2_filtered) - complete_files))

    # print Missing files
    if print_missing:
        for mf in missing_files:
            if mf in files1_filtered:
                print("WARNING: {} - {} companion missing".format(mf, extension2))
            if mf in files2_filtered:
                print("WARNING: {} - {} companion missing".format(mf, extension1))
    return sorted(list(complete_files))


def check_same_action_set(all_trained_action, content_ground_truth):

    def get_all_gt_action(content_ground_truth):
        all_gt_action = set()
        for c in content_ground_truth:
            for t1, t2, l in content_ground_truth[c]:
                all_gt_action.add(l)
        return all_gt_action

    all_gt_action = get_all_gt_action(content_ground_truth)
    in_train_not_in_gt = all_trained_action.difference(all_gt_action)
    if len(in_train_not_in_gt) != 0:
        print("WARNINGS: {} are in train set but does not appears in longruns.".format(list(in_train_not_in_gt)))

    in_gt_not_in_train = all_gt_action.difference(all_trained_action)
    if len(in_gt_not_in_train) != 0:
        print("WARNINGS: {} are in longruns set but does not appears in train.".format(list(in_gt_not_in_train)))


def import_longrun(DATA_PATH, ALL_TRAINED_ACTION,
                   MERGED_FORCE_STOP=None, GROUND_TRUTH_PATH_EXTENTION="ground-truth/",
                   LOWER = 0, UPPER = 18.5,
                   DPRINT=False):
    """
    Imports all
    Args:
        DATA_PATH : [path_to_csv_data,]. List of path to the .csv representing captures
        GROUND_TRUTH_PATH_EXTENTION : str. Where the ground truth are compared to the base path DATA_PATH.
                                           If in the same folder, use the empty string : ""
        LOWER : int. Lower time difference between automate and manually checked gournd-truth for action launch
        UPPER : int. Upper difference between automate and manually checked gournd-truth for action launch
    Return:
        captures : dict[filename] -> dict(xs:[t,] ys[l,]). Mapping from file name to associated time series
        content_ground_truth : dict[filename] -> [(t_lower,t_upper, action),] Mapping from file name to associated ground_truth
    """
    def dprint(s):
        if DPRINT:
            print(s)

    if type(DATA_PATH) != list:
        DATA_PATH = [DATA_PATH]

    captures = dict()
    content_ground_truth = dict()


    for data_path in DATA_PATH:
        print("Importing data in :" + data_path)
        data_path_content = sorted(glob.glob(data_path + '*.csv', recursive=True))
        gt_path_content = sorted(glob.glob(data_path + GROUND_TRUTH_PATH_EXTENTION + '*.log', recursive=True))


        # All data that can be used must have their .log companion (in ground-truth)
        ready_dataset = intersection_fname(data_path_content, gt_path_content)

        path_files_data = [data_path + f + ".csv" for f in ready_dataset]
        path_files_ground_truth = [data_path + GROUND_TRUTH_PATH_EXTENTION + f + ".log" for f in ready_dataset]

        # Read ground_truth and make boundaries
        content_ground_truth_tmp = read_longrun_log_files(path_files_ground_truth, ALL_TRAINED_ACTION, MERGED_FORCE_STOP)
        content_ground_truth_tmp = make_bound_for_timing_in_action(content_ground_truth_tmp, LOWER, UPPER)
        content_ground_truth.update(content_ground_truth_tmp)


        # From files to time series

        for longrunCaptFile in data_path_content:
            dprint(longrunCaptFile)
            columns = extract_columns(longrunCaptFile)
            packets = read_file(longrunCaptFile, columns)
            packets = packet_store_cleanup(packets)
            time_serie = packets_to_timesize_tuples(packets, wprint=False)
            captures[extract_fname(longrunCaptFile)] = time_serie
        dprint("export in "+ data_path+ " finished\n")

    check_same_action_set(ALL_TRAINED_ACTION, content_ground_truth)

    return captures, content_ground_truth

#### SEQUENCE SPLITTER


def find_critical_point(time_serie, WINDOW_SIZE=20, INTER_SPACING_CRITICAL_POINTS=5,
                        WINDOW_MINIMAL_PAYLOAD=200, MINIMUM_SIZE_CRITICAL_STARTING_POINT=-1):
    """
    Find Critcal points: where we have more than WINDOW_MINIMAL_PAYLOAD Bytes
    data sum over a period of WINDOW_SIZE seconds with INTER_SPACING_CRITICAL_POINTS seconds inter space
    """
    ts = pd.Series(data = time_serie['ys'], index = pd.to_timedelta(time_serie["xs"], 'sec'))

    # filter out packets with no payload length and (or not) the ones that contains < 26 bits
    ts = ts.map(abs)[ts != 0][ts > MINIMUM_SIZE_CRITICAL_STARTING_POINT]

    def extract_indexes_in_groups(x):
        return x.index.tolist()

    def time_delta_to_float(td):
        if len(td) == 0:
            return None
        return float(str(td[0].seconds) +"." + str(td[0].microseconds))

    # Compute the moving sum of WINDOW_SIZE seconds head in data PayloadLengt
    def rolling_forward(ts, WINDOW_SIZE):
        def forward_window(x, ts, WINDOW_SIZE):
            return ts[x['index'] : x['index'] + pd.Timedelta(seconds=WINDOW_SIZE)].sum()
        roll_forward = ts.reset_index().apply(lambda x: forward_window(x, ts, WINDOW_SIZE), axis=1).values
        return pd.Series(roll_forward, ts.index)

    stw = rolling_forward(ts, WINDOW_SIZE)
    stw = stw[stw > WINDOW_MINIMAL_PAYLOAD]  # filter out minimum WINDOW_MINIMAL_PAYLOAD Bytes payload (banned app)
    stw = stw.resample(str(INTER_SPACING_CRITICAL_POINTS)+'s').apply(extract_indexes_in_groups) # 5 seconds jump
    critical_points = stw.map(time_delta_to_float).dropna().values

    return critical_points



def find_action_end(xs_capt, ys_capt, FILTER_LENGTH_LIMIT=46 ,INTER_TIMER_EVENT_CUTOFF=5):
    """
    return the potential end of the action that begins at indicce j
    xs_capt : time elements
    ys_capt : length elements
    FILTER_LENGTH_LIMIT : do not take length <= n
    INTER_TIMER_EVENT_CUTOFF ; Do not take into accout

    return indices of the en
    """
    xs_no_zeros = [x  for y, x in zip(ys_capt, xs_capt) if abs(y) > FILTER_LENGTH_LIMIT]
    for i, x0 in enumerate(xs_no_zeros):
        if i + 1 == len(xs_no_zeros):
            return xs_capt[-1]  # reached the end
        x1 = xs_no_zeros[i + 1]
        inter_time = x1-x0
        if inter_time > INTER_TIMER_EVENT_CUTOFF:
            return x0
    return xs_capt[-1]

def find_x_indices(xs_capt, j, xs_end):
    for i, x in enumerate(xs_capt[j:]):
        if xs_end <= x:
            return i + j
    return len(xs_capt) - 1



#### CLASSIFIER

def compute_acc_per_capture(acc, DPRINT=False):
        total_correct = []
        total = []
        for capture in acc:

            correct = [y1 for y1, y2 in acc[capture] if y1==y2]
            total_correct += correct
            total += acc[capture]
            if DPRINT:
                print(capture, " Accuracy = ",len(correct)/len(acc[capture]))

        print("\nOverval accuracy: ", len(total_correct)/len(total))
        print(len(total))


def predict(time_serie, CLF, WINDOW_SIZE=20, INTER_SPACING_CRITICAL_POINTS=5,
            WINDOW_MINIMAL_PAYLOAD=200, MINIMUM_SIZE_CRITICAL_STARTING_POINT=-1,
            FILTER_LENGTH_LIMIT=46, INTER_TIMER_EVENT_CUTOFF=5, TO_WITHDRAW=[]):

    """
    Make Prediction on a longrun capture
    Args:
        time_series : dict['xs', 'ys'] -> [x,],[y,]. Dictonary having 2 entries: xs for the time and ys of packet length
        WINDOW_SIZE : int. Size in seconds of the Sliding Window.
        INTER_SPACING_CRITICAL_POINTS : int. Minimum spacing between two critical points.

    """

    critical_points = find_critical_point(time_serie,  WINDOW_SIZE, INTER_SPACING_CRITICAL_POINTS,
                        WINDOW_MINIMAL_PAYLOAD, MINIMUM_SIZE_CRITICAL_STARTING_POINT)

    cap_predict = []  # tuple list of
    critical_points_i = 0
    xs_end = -1
    xs_capt = time_serie["xs"]
    ys_capt = time_serie["ys"]



    for i, _ in enumerate(xs_capt):


        current_xs = xs_capt[i]
        critical_point = critical_points[critical_points_i]
        if current_xs > critical_point and current_xs > xs_end:

            j = i-1   # take previous one since we are one step further

            xs_start = xs_capt[i]
            xs_end = find_action_end(xs_capt[i:], ys_capt[i:], FILTER_LENGTH_LIMIT, INTER_TIMER_EVENT_CUTOFF)
            end_indice = find_x_indices(xs_capt, j, xs_end)
            xy = dict()
            xy["xs"] = xs_capt[j:end_indice+1]
            xy["ys"] = ys_capt[j:end_indice+1]
            features_dict = extract_features(xy, to_withdraw=TO_WITHDRAW)
            features = list(features_dict.values())
            y = CLF.predict_proba(np.array(features).reshape(1,-1))

            cap_predict.append((xs_start, xs_end, y[0]))

            while critical_points[critical_points_i] < xs_end:
                critical_points_i +=1
                if critical_points_i == len(critical_points):
                    break




        if critical_points_i == len(critical_points) or xs_end == xs_capt[-1]:
            break
    return cap_predict

def predict_all(captures, CLF, WINDOW_SIZE=20, INTER_SPACING_CRITICAL_POINTS=5,
                WINDOW_MINIMAL_PAYLOAD=200, MINIMUM_SIZE_CRITICAL_STARTING_POINT=-1,
                FILTER_LENGTH_LIMIT=46, INTER_TIMER_EVENT_CUTOFF=5, DPRINT=False,
                TO_WITHDRAW=[]
               ):

    predicted = dict()
    for capture in captures:
        if DPRINT:
            print(capture)
        predicted[capture] = predict(captures[capture], CLF, WINDOW_SIZE, INTER_SPACING_CRITICAL_POINTS,
                                     WINDOW_MINIMAL_PAYLOAD, MINIMUM_SIZE_CRITICAL_STARTING_POINT,
                                     FILTER_LENGTH_LIMIT, INTER_TIMER_EVENT_CUTOFF, TO_WITHDRAW=TO_WITHDRAW)
    return predicted


def predict_with_ground_truth(captures, content_ground_truth, DPRINT=False, ACTION_DURATION=45, TO_WITHDRAW=[]):
    predicted = dict()
    acc = dict()

    def dprint(c):
        if DPRINT:
            print(c)

    for capture in captures:
        predicted[capture] = []
        acc[capture] = []
        ts = captures[capture]
        xs = ts["xs"]
        ys = ts["ys"]
        i_start = 0
        for j , (start_min, start_max, y_true) in enumerate(content_ground_truth[capture]):

            stop = start_min + ACTION_DURATION
            i_start = find_x_indices(xs, i_start, start_min)
            if j < len(content_ground_truth[capture]) - 1:
                # Take the minimum between  the maximum duration and the start of the next action
                stop = min(start_min + ACTION_DURATION, content_ground_truth[capture][j+1][0])


            i_stop = find_x_indices(xs, i_start, stop)
            # extract the cut
            xy = dict()
            xy["xs"] = xs[i_start:i_stop+1]
            xy["ys"] = ys[i_start:i_stop+1]

            # extract features
            features_dict = extract_features(xy, to_withdraw=TO_WITHDRAW)
            features = list(features_dict.values())

            # predict
            y_prob_pred = clf.predict_proba(np.array(features).reshape(1,-1))[0]
            y_pred = clf.predict(np.array(features).reshape(1,-1))[0]
            predicted[capture] += [(xs[i_start], xs[i_stop], y_prob_pred)]
            acc[capture].append((y_pred, y_true))
            acc[capture]
            i_start = i_stop

        dprint("#############")
        dprint("")

        if len(acc[capture]) == 0:
            print(capture, " does not have any performed action")
            continue
        print(capture)
        correct = [y1 for y1, y2 in acc[capture] if y1==y2]
        dprint(capture + " Accuracy = " + str(len(correct)/len(acc[capture])))
        dprint("")
        dprint("#############")
    return predicted, acc



#### DECISION MAKER AND Evaluation



def overlaps(a, b):
    return not (b[0] > a[1] or a[0] > b[1])


def overlap_length(a,b):
    if not overlaps(a, b):
        return 0
    return  min(a[1], b[1]) - max(a[0], b[0])

def majority_votings(predicted):
    mv_pred = dict()
    for c in predicted:
        mv_pred[c] = list()
        for tstart, t_stop, prob_vect in predicted[c]:
            mv_pred[c].append( (tstart,  clf.classes_[np.argmax(prob_vect)]))

    return mv_pred


def top_n_majority_votings(predicted):
    top_args = np.argsort(-pred_vec)[:TOP_N].tolist()
    return [clf.classes_[top_arg] for top_arg in top_args]


def compute_eval_metric(prediciton, ground_truth, clf, METHOD="majority_voting",
                        TOP_N=3, MATCH_METHOD="first",
                        print_details=True, SKIPPING_FORCE_STOP=False,
                        RETURN_PROB=False, TARGET_APPS_ONLY=False,
                        THRESHOLD=None
                       ):
    """
    calculate accuarcy, precision and recall
    Args:
        prediction : [(start, stop, action),]. List of predicition with time boundaries
        ground_truth : [(start, stop, action),]. List of ground_turh associated with the prediction
        METHOD : str. The method to use to classify the probability output.
                      The list of possible methods are the folowing:
                      'majority_voting': return the label with the most vote in the RF
                      'top_n_majority_voting': return the TOP_N
                      'threshold_majority_voting': same as majority_voting with threshold cutoff
        MATCH_METHOD : str. The matching method to be use if 2 or more prediction overlaps a correct ground truth.
                            The list of possible methods are the folowing:
                            'first' : The closest to the begining of the action
                            'overlap' : The one that overlap the most the ground-truth
        RETURN_PROB : bool. Return Probabilities vector instead of
        SKIPPING_FORCE_STOP : bool. Remove all force stop from predicted and gt.
    Return (tp, fp, fn) True Positive, False Positive and False Negative
    """

    MATCH_METHOD = "best_match_" + MATCH_METHOD

    if SKIPPING_FORCE_STOP and METHOD=="top_n_majority_voting":
        print("WARNING: {} cannot be combined with SKIPPING_FORCE_STOP=True".format(METHOD))
        sys.exit(1)

    if METHOD == "threshold_majority_voting" and THRESHOLD is None:
        print("WARNING: {} cannot be combined with THRESHOLD=None".format(METHOD))
        sys.exit(1)

    tp, fp, fn = 0, 0, 0
    i_pred, i_gt = 0, 0
    correct_pred, wrong_pred, missed_gt, correct_gt = [], [], [], []
    last_run = False


    def add_wrong_pred(pred, fp):
        fp += 1
        wrong_pred.append(pred)
        if print_details:
            print(pred[2] + " wrong prediction (fp + 1= ", fp, ")")
        return fp

    def add_missed_gt(gt, fn):
        fn += 1
        missed_gt.append(gt)
        if print_details:
            print(gt[2], " missed prediction (fn + 1= ", fn,")")
        return fn

    def add_correct_pred(pred, tp):
        tp += 1
        correct_pred.append(pred)
        if print_details:
            print(pred[2] + " correct pref (tp + 1 = ", tp,")")
        return tp


    def majority_voting(pred_vec):
        return [clf.classes_[np.argmax(pred_vec)]]

    def threshold_majority_voting(pred_vec):
        if max(pred_vec) < THRESHOLD:
            return None
        return majority_voting(pred_vec)


    def top_n_majority_voting(pred_vec):
        top_args = np.argsort(-pred_vec)[:TOP_N].tolist()
        return [clf.classes_[top_arg] for top_arg in top_args]

    def remove_force_stop(prediction):
        prediciton_out = list()
        for pred in prediction:
            pred_cop = pred[2] if type(pred[2]) == list else [pred[2]]
            if any([True for x in pred_cop if "force-stop" in x]):
                continue
            prediciton_out.append(pred)
        return prediciton_out

    def best_match_first(match):
        "Return a list sorted by best match according to the criteria on the function name"
        return match

    def best_match_overlap(match):
        "Return a list sorted by best match according to the criteria on the function name"
        return sorted(match,key=lambda item:-item[1])



    matched_pred = []
    for gt in ground_truth:
        start_gt, stop_gt, action_gt = gt
        if TARGET_APPS_ONLY:
            action_gt = action_gt.split("_")[0]

        match = []
        for pred in prediciton:
            start_pred, stop_pred, pred_vec = pred
            action_pred = eval(METHOD)(pred_vec)
            if action_pred is None:
                continue

            if overlaps((start_pred, stop_pred), (start_gt, stop_gt)) and any([True for x in action_pred if action_gt in x]):

                chosen_pred = (start_pred, stop_pred, action_pred)
                match.append((chosen_pred, overlap_length((start_pred, stop_pred), (start_gt, stop_gt))))

        if len(match) == 0:
            fn = add_missed_gt(gt, fn)
            continue

        best_matchs = eval(MATCH_METHOD)(match)

        for bm in best_matchs:
            pred = bm[0]
            if not pred in correct_pred:
                tp = add_correct_pred(pred, tp)
                break

    # compute wrong pred:
    for pred in prediciton:
        start_pred, stop_pred, pred_vec = pred
        action_pred = eval(METHOD)(pred_vec)

        # prediction skipped by the Decision Maker
        if action_pred is None:
            continue
        chosen_pred = (start_pred, stop_pred, action_pred)
        if chosen_pred not in correct_pred:
            fp = add_wrong_pred(chosen_pred, fp)

    if SKIPPING_FORCE_STOP:
        correct_pred = remove_force_stop(correct_pred)
        wrong_pred = remove_force_stop(wrong_pred)
        missed_gt = remove_force_stop(missed_gt)

    return correct_pred, wrong_pred, missed_gt







#### EVALUATION

def eval_all(predicted, content_ground_truth, clf, METHOD='majority_voting', TOP_N=3,
             MATCH_METHOD='first', OUTPUT_DICT=False, DPRINT=False, TARGET_APPS_ONLY=False,
             THRESHOLD=None, SKIPPING_FORCE_STOP=False):

    all_correct_pred = []
    all_wrong_pred = []
    all_missed_gt = []

    all_correct_pred_dict = dict()
    all_wrong_pred_dict = dict()
    all_missed_gt_dict = dict()

    def dprint(s):
        if DPRINT:
            print(s)

    for capture in predicted:
        if capture == "longrun_uniform_20-04-20_11-28-32":
            continue
        (correct_pred, wrong_pred, missed_gt) = compute_eval_metric(predicted[capture],
                                                                    content_ground_truth[capture],
                                                                    clf,
                                                                    METHOD=METHOD,
                                                                    THRESHOLD=THRESHOLD,
                                                                    MATCH_METHOD=MATCH_METHOD,
                                                                    TOP_N=TOP_N,
                                                                    TARGET_APPS_ONLY=TARGET_APPS_ONLY,
                                                                    print_details=False, SKIPPING_FORCE_STOP=SKIPPING_FORCE_STOP)

        all_correct_pred_dict[capture] = correct_pred
        all_wrong_pred_dict[capture] = wrong_pred
        all_missed_gt_dict[capture] = missed_gt

        all_wrong_pred += wrong_pred
        all_correct_pred += correct_pred
        all_missed_gt += missed_gt

        dprint(capture)
        tp, fp, fn = len(correct_pred), len(wrong_pred), len(missed_gt)
        #if tp + fp != 0 or tp + fn !=0:
        precision = 1 if tp + fp == 0 else tp / (tp + fp)
        recall = 1 if tp + fn == 0 else tp / (tp + fn)

        dprint("precision = {}, recall = {}".format(precision, recall))
        dprint(" ")
    if OUTPUT_DICT:
        return all_correct_pred_dict, all_wrong_pred_dict, all_missed_gt_dict
    return all_correct_pred, all_wrong_pred, all_missed_gt




def fbeta_score(x, precision="precision", recall="recall", beta=1.):
    p = float(x[precision])
    r = float(x[recall])
    if p == 0 or r == 0:
        return 0
    return (1 + beta**2) * (p * r)/((beta**2 * p) + r)



#### PLOTS


def plot_prec_recall_by_slot(all_correct_pred_dict, all_wrong_pred_dict, all_missed_gt_dict,
                             by='slots', remove_force_stop=True, savefig=None, beta=1):

    tp, fp, fn = Counter(), Counter(), Counter()

    def apps_count(preds):
        app_counter = Counter()
        for c in preds:
            for pred in preds[c]:
                pred_cop = pred[2] if type(pred[2]) == list else [pred[2]]
                app_counter[pred_cop[0]] += 1
        return app_counter


    if by == 'slots':
        for c in all_correct_pred_dict:
            slot = int(c.split("_")[-1].split("-")[1])
            tp[slot] += len(all_correct_pred_dict[c])
            fp[slot] += len(all_wrong_pred_dict[c])
            fn[slot] += len(all_missed_gt_dict[c])

    if by == "date":
        for c in all_correct_pred_dict:
            date = c.split("_")[2]
            tp[date] += len(all_correct_pred_dict[c])
            fp[date] += len(all_wrong_pred_dict[c])
            fn[date] += len(all_missed_gt_dict[c])

    if by == "category":
        cats = ["open", "stop", 'inApp']
        for cat in cats:
            for c in all_correct_pred_dict:
                if cat == 'inApp':
                    corr_count = [1  for pred in all_correct_pred_dict[c] if 'open' not in pred[2][0] and 'force-stop' not in pred[2][0]]
                    wrong_count = [1  for pred in all_wrong_pred_dict[c] if 'open' not in pred[2][0] and 'force-stop' not in pred[2][0]]
                    missed_count = [1  for pred in all_missed_gt_dict[c] if 'open' not in pred[2] and 'force-stop' not in pred[2]]
                else:
                    corr_count = [1  for pred in all_correct_pred_dict[c] if cat in pred[2][0]]
                    wrong_count = [1  for pred in all_wrong_pred_dict[c] if cat in pred[2][0]]
                    missed_count = [1  for pred in all_missed_gt_dict[c] if cat in pred[2]]
                tp[cat] += len(corr_count)
                fp[cat] += len(wrong_count)
                fn[cat] += len(missed_count)

    if by == 'apps':
        tp = apps_count(all_correct_pred_dict)
        fp = apps_count(all_wrong_pred_dict)
        fn = apps_count(all_missed_gt_dict)


    if by == 'all':
        # Return precision. recall and f1 score
        for c in all_correct_pred_dict:
            tp['tp'] += len(all_correct_pred_dict[c])
            fp['fp'] += len(all_wrong_pred_dict[c])
            fn['fn'] += len(all_missed_gt_dict[c])
        p = tp['tp'] / (tp['tp'] + fp['fp'])
        r = tp['tp'] / (tp['tp'] + fn['fn'])
        f1 = (1 + beta**2) * (p * r)/((beta**2 * p) + r)
        return p, r, f1

    tp = pd.Series(tp)
    fp = pd.Series(fp)
    fn = pd.Series(fn)

    if remove_force_stop and by=="category":
        del tp["stop"]
        del fp["stop"]
        del fn["stop"]


    tpfpfn = pd.DataFrame({'tp': tp, 'fp': fp, 'fn':fn}).fillna(0)

    precision = tpfpfn["tp"] / (tpfpfn["tp"] + tpfpfn["fp"])
    recall = tpfpfn["tp"] / (tpfpfn["tp"] + tpfpfn["fn"])


    prec_recall = pd.DataFrame({'recall': recall, 'precision': precision})

    if savefig:
        if by == 'category':
            by = "action types"

        ax = tpfpfn.plot(kind='bar', fontsize=15, figsize=(7,5))
        plt.ylabel("score", fontsize=16)
        plt.xlabel(by, fontsize=16)
        plt.title("tp fp fn for by " + by, fontsize = 16)
        plt.legend(fontsize=13)
        #plt.xticks(rotation=0)
        plt.savefig(savefig+'_1tpfpfn', dpi= 80)


        title="Recall and Precision Score by " + by
        ax = prec_recall.plot(kind='bar', fontsize=15, ylim=[0,1.02], figsize=(7,5))
        plt.ylabel("score", fontsize=16)
        plt.xlabel(by, fontsize=16)
        plt.title(title, fontsize=16)
        plt.legend(fontsize=13, loc=(0.4,0.82)) #loc='upper center')
        #plt.xticks(rotation=0)
        plt.savefig(savefig+"_"+by+"_pr", dpi= 80)


    return prec_recall, tpfpfn


def plot_f1_prec_rec(predicted, content_ground_truth, clf):
    linspace = np.arange(0, 1, 0.025)
    ps, rs, f1s = [], [], []
    for sensitivity in linspace:
        #all_correct_pred, all_wrong_pred, all_missed_gt = eval_all(predicted, content_ground_truth, METHOD="majority_voting", MATCH_METHOD='first', TOP_N=100)
        all_correct_pred_dict, all_wrong_pred_dict, all_missed_gt_dict = eval_all(predicted,
                                                                                  content_ground_truth,
                                                                                  clf,
                                                                                  METHOD='threshold_majority_voting', # "majority_voting",
                                                                                  THRESHOLD=sensitivity,
                                                                                  MATCH_METHOD='first',
                                                                                  TARGET_APPS_ONLY=False,
                                                                                  TOP_N=1, OUTPUT_DICT=True,
                                                                                  SKIPPING_FORCE_STOP=True)
        p, r, f1 = plot_prec_recall_by_slot(all_correct_pred_dict,
                                            all_wrong_pred_dict,
                                            all_missed_gt_dict,
                                            by="all", savefig=None)
        ps.append(p)
        rs.append(r)
        f1s.append(f1)
    plt.plot(linspace, rs, label="recall")
    plt.plot(linspace, ps, label="precision")
    plt.plot(linspace, f1s, label= "F1")
    plt.xlabel("Decision Maker threshold", fontsize=14)
    plt.ylabel("score", fontsize=14)
    plt.title("Precision, Recall, F1 at different Threshold", fontsize = 16)
    plt.xticks(fontsize=13)
    plt.yticks(fontsize=13)
    plt.legend(fontsize=14)
    plt.savefig("./plots/longrun_p_r_f1_threshold", dpi=180)

    max_ = np.argmax(f1s)
    print("maximum f1 score reached at ", linspace[max_], " threshold")
    print(" precision: ", ps[max_])
    print(" recall: ", rs[max_])
    print(" f1: ", f1s[max_])
    print("saved image ./plots/longrun_p_r_f1_threshold.png")
    return ps, rs, f1s
