import csv
import glob
import math
import os
import pickle
import sys
from functools import reduce


SOURCES_FILE_IGNORE = ["Initial Tests", ".cache", ".sync", ".vscode", "lib", "share", "bin", "etc", "include", ".ipynb_checkpoints"]
POSSIBLE_MASTERS = ["Pixel 2", "Nexus 5", "Ludovic.s iPhone"]

master = ""
slave = ""

# --------------------------------------
# Dataset Parsing

# Finds CSV datasets recursively
def find_sources(folders='./'):
    global SOURCES_FILE_IGNORE

    if type(folders) is not list:
        folders = [folders]

    sources_files = []

    for folder in folders:
        files = glob.glob(folder + '*.csv', recursive=True)
        if len(files) == 0:
            print("WARNING: No csv in {}, or dir none existent".format(folder))
        for file in files:
            ignore = False
            for ignore_pattern in SOURCES_FILE_IGNORE:
                if ignore_pattern in file:
                    ignore = True
            if not ignore:
                sources_files.append(file.replace('./', ''))


    return sorted(sources_files)

# Parses a CSV dataset
all_columns = set()
def extract_columns(dataset_file):
    global all_columns

    with open(dataset_file, "r") as file:
        csv_reader = csv.reader(file, delimiter=',', quotechar='"')
        for i, line in enumerate(csv_reader):
            all_columns.update(line)
            return

def find_common_columns(sources_files):
    global all_columns

    all_columns = set()
    for source in sources_files:
        extract_columns(source)
    all_columns = list(all_columns)
    return all_columns

packet_store = dict() # dataset_file => [packetID => layers]
ID_COLUMN = "Packet #"

# creates a new packet with all columns (from the union of each dataset's columns)
def new_packet():
    global all_columns

    packet = dict()
    for column in all_columns:
        packet[column] = ""

    return packet

def parse_dataset(dataset_file):
    """
    Reads a .csv file and puts its raw contents in packet_store[dataset_file]
    """
    global packet_store, all_columns

    dataset_packet_store = dict() # packetID => packets
    headers = []
    with open(dataset_file, "r") as file:
        reader = csv.reader(file, delimiter=',', quotechar='"')

        for i, line in enumerate(reader):
            if i == 0:
                headers = line
                continue

            packet = new_packet()

            for j, item in enumerate(line):
                key = headers[j]
                val = item

                if key not in packet:
                    print("Fatal: column", key, "not found in packet; all_columns is", all_columns)
                    sys.exit(1)
                packet[key] = val

            packet_id = toInt(packet[ID_COLUMN].replace('\'', ''))
            if packet_id not in dataset_packet_store:
                dataset_packet_store[packet_id] = []

            dataset_packet_store[packet_id].append(packet)

    packet_store[dataset_file] = dataset_packet_store

# Cleanup
def toInt(s, default=0):
    if s.strip() == "":
        return default
    return int(s.replace('\'', ''))

def toFloat(s, default=0):
    if s.strip() == "":
        return default
    return float(s.replace('\'', '').replace(' ', ''))

def extract_payload_length(payload_string, default=0):
    payload_string = payload_string.strip()
    if payload_string == "" or "No data" in payload_string:
        return default
    parts = payload_string.split(' ')
    return toInt(parts[0])

def extract_payload_bytes(payload_string, default=[]): # format: "4 bytes (00 11 22 33)"
    payload_string = payload_string.strip()
    if payload_string == "" or "No data" in payload_string or not "(" in payload_string or not ")" in payload_string:
        return default
    cut1 = payload_string[payload_string.find("(")+1:]
    cut2 = cut1[:cut1.find(")")]
    return cut2

def packet_store_cleanup(dataset_packet_store): #dataset_packet_store is packetID => packets
    for packet_id in dataset_packet_store:
        layers = dataset_packet_store[packet_id]
        for layer in layers:
            layer[ID_COLUMN] = toInt(layer[ID_COLUMN])
            layer["Time"] = toFloat(layer["Time"], default=-1)
            layer["Time delta"] = toFloat(layer["Time delta"], default=-1)
            layer["PayloadLength"] = extract_payload_length(layer["Payload"], default=0)
            layer["PayloadRaw"] = extract_payload_bytes(layer["Payload"])

def packets_to_timesize_tuples(packets):
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
                # print("WARNING master not in Possible masters: '" + master + "'")
                # print(layer["Communication"])
                direction = -1

            if not "master" in layer['Transmitter'].lower():
                direction *= -1
            xy['xs'].append(float(layer['Time']))
            xy['ys'].append(direction * int(layer['PayloadLength']))
    return xy

# --------------------------------------
# Auxiliary functions (print & plot)
def extract_master(comm):
    return comm[comm.find('"') +1 : comm.find('"', comm.find('"')+1)]


def pad(s, length, max_length = -1):
    s = str(s)
    if max_length > -1 and len(s) > max_length:
        s = s[:max_length-3]+"..."
    if len(s) == length:
        return s
    p = " " * (length - len(s))
    return s+p

def print_packet(p):
    isFirstLayer = True

    for layer in p:
        size = "0"
        if layer["PayloadLength"] != -1:
            size = str(layer["PayloadLength"])+"B ("+str(layer["PayloadRaw"])+")"

        details = ""
        if isFirstLayer:
            details = " ("+str(layer["Communication"])+")"
        print(str(layer[ID_COLUMN]) + ": T="+str(layer['Time']) + " P=" + size + ' Tx=' + layer['Originator'] + ' Item='+layer['Item'].strip() + details)

def plot(xs, ys, title="Title not set", bar_width=0.2):
    xs_nonzero = []
    ys_nonzero = []
    xs_zero = []
    ys_zero = []

    for i in range(len(xs)):
        x = xs[i]
        y = ys[i]
        if y > 0:
            xs_nonzero.append(x)
            ys_nonzero.append(abs(y))
        else:
            xs_zero.append(x)
            ys_zero.append(-10) # special value to be visible on the graph

    if len(xs_zero)>0:
        plt.bar(xs_zero, ys_zero, color='r', align='center', linewidth=0, width=bar_width)
    if len(xs_nonzero)>0:
        plt.bar(xs_nonzero, ys_nonzero, color='b', align='center', linewidth=0, width=bar_width * 2)

    plt.xlabel('Time [s]')
    plt.ylabel('Packet size [B]')
    plt.title(title)

    legends = []
    if len(xs_zero)>0:
        legends.append('NULLs')
    if len(xs_nonzero)>0:
        legends.append('Data')

    plt.legend(legends,loc=2)

    plt.show()

# Cache
def cache(object_uri, object_to_cache):
    full_destination = ".cache/" + object_uri.replace('/', '_')
    try:
        os.remove(full_destination)
    except:
        pass
    with open(full_destination, "wb") as f:
        pickle.dump(object_to_cache, f)

def load_cache(object_uri):
    full_destination = ".cache/" + object_uri.replace('/', '_')
    if os.path.isfile(full_destination):
        #print("Loading", object_uri, "from cache (" + str(full_destination)+")")

        with open(full_destination, "rb") as f:
            return pickle.load(f)
    return None

def dataset_file_to_xy_features(source_file):
    """
    Returns [(time,size)] for a given .csv source_file.
    Assumes packet_store has been filled (with parse_dataset) (not necessary if data is cached).
    """
    f = source_file+".xy"

    xy_features = load_cache(f)
    if xy_features == None:
        xy_features = packets_to_timesize_tuples(packet_store[source_file])
        cache(f, xy_features)
    return xy_features

def dataset_file_to_xy_events(source_file, timeout=4.5):
    """
    Returns [[(time,size)],] separated by events for a given .csv source_file.
    Assumes packet_store has been filled (with parse_dataset) (not necessary if data is cached).
    """
    f = source_file+"."+str(timeout)+".events.xy"

    xy_events = load_cache(f)
    if xy_events == None:
        xy_features = dataset_file_to_xy_features(source_file)
        xy_events = cut_in_events(xy_features, timeout=timeout)
        cache(f, xy_events)
    return xy_events


# --------------------------------------
# Events

def cut_in_events(xy_features, timeout=4.5):
    """
    Returns [[(time, size)],] where each list is separated by at least timeout time, from a given [(time,size)]
    """
    events = []
    def trim_and_add_event(start, end):
        start_trim = start
        while ys[start_trim] == 0 :
            start_trim += 1
            if start_trim >= len(ys):
                return None
        end_trim = end
        while ys[end_trim] == 0 :
            end_trim -= 1

        if start_trim > end_trim:
            print("You broke the matrix", start, end, start_trim, end_trim, len(xs), len(ys))
            sys.exit(1)

        xs_copy = xs[start_trim:end_trim]
        ys_copy = ys[start_trim:end_trim]
        events.append(dict(xs=xs_copy, ys=ys_copy))


    xs = xy_features['xs']
    ys = xy_features['ys']

    if timeout == -1:
        return [dict(xs=xs, ys=ys)]

    feature_start = 0
    last_activity_index = -1  # not even one activity seen yet, never create an event in this case
    index = 0

    while index < len(xs):

        if last_activity_index != -1 and xs[index] - xs[last_activity_index] > timeout:
            trim_and_add_event(feature_start, index)

            feature_start = index
            last_activity_index = -1 # not even one activity seen yet

        if ys[index] > 0:
            last_activity_index = index
        index += 1

    # don't forget the last event
    if feature_start < len(xs)-1:
        trim_and_add_event(feature_start, len(xs)-1)

    events = [e for e in events if e is not None]
    return events


def filter_out_path(fs, filter_out_device = False):
    f = fs[fs.rfind('/')+ 1:]
    if filter_out_device:
        f = f[f.rfind('_')+ 1:]
    return f


def cut_all_datasets_in_events(sources_files, timeout=-1):
    """
    Returns a map[device][app][action] => list[[(time, size)],] where list is cut by events
    Second return value is the same structure, but with # of packets instead of events

    also return map[device][app][action] => list[[event_id] used latter to track
    the missclassified events
    """
    events = dict()
    events_id = dict()
    counts = dict()

    # cut each file in events
    for s in sources_files:
        fname = filter_out_path(s)
        parts = fname.split("_")
        device, app, action, event_id = parts[0], parts[1], parts[2], parts[3]

        if not device in events:
            events[device] = dict()
        if not app in events[device]:
            events[device][app] = dict()
        if not action in events[device][app]:
            events[device][app][action] = []

        file_events = dataset_file_to_xy_events(s, timeout=timeout) # cut each trace into subtraces after 4.5 idle time

        event_index = 0
        for event in file_events:
            n_packets = len(event['xs'])
            if n_packets == 0:
                #print("Skipping", s, " (",device,app,action,") event",event_index, "as it has 0 packets")
                pass
            else:
                events[device][app][action].append(event)

            event_index += 1

    return events, counts


def cut_all_datasets_in_event(sources_files, timeout=-1):
    """
    Returns a map[device][app][action][event] => (time, size) where list is cut by events
    Second return value is the same structure, but with # of packets instead of events
    """
    events = dict()
    counts = dict()

    # cut each file in events
    for s in sources_files:
        fname = s.replace(DATA_PATH, '')
        parts = fname.split("_")
        device, app, action = parts[0], parts[1], parts[2]
        event_nb = parts[5][: parts[5].find(".")]

        if not device in events:
            events[device] = dict()
        if not app in events[device]:
            events[device][app] = dict()
        if not action in events[device][app]:
            events[device][app][action] = dict()

        file_events = dataset_file_to_xy_events(s, timeout=timeout) # cut each trace into subtraces after 4.5 idle time

        event_index = 0
        for event in file_events:
            n_packets = len(event['xs'])
            if n_packets == 0:
                #print("Skipping", s, " (",device,app,action,") event",event_index, "as it has 0 packets")
                pass
            else:
                events[device][app][action][event_nb] = event

            event_index += 1

    return events, counts


# --------------------------------------
# General Dataset Operations

def split_test_train(sources_files):
    """
    Sorts input csv into map[device][app][action], then foreach action, split into test train
    (1 entry for test, remaining for train; typically that's 20% test 80% train)
    """
    sources_hierarchy = dict()

    for s in sources_files:
        fname = s.replace(DATA_PATH, '')
        parts = fname.split("_")
        device, app, action = parts[0], parts[1], parts[2]

        if not device in sources_hierarchy:
            sources_hierarchy[device] = dict()
        if not app in sources_hierarchy[device]:
            sources_hierarchy[device][app] = dict()
        if not action in sources_hierarchy[device][app]:
            sources_hierarchy[device][app][action] = []

        sources_hierarchy[device][app][action].append(s)

    sources_test = []
    sources_train = []

    for device in sources_hierarchy:
        for app in sources_hierarchy[device]:
            for action in sources_hierarchy[device][app]:
                test = True
                for s in sorted(sources_hierarchy[device][app][action]):
                    if test:
                        sources_test.append(s)
                        test = False
                    else:
                        sources_train.append(s)

    return sources_test, sources_train


def split_test_train_non_mixed(sources_files, CLASSIC_DEVICES=[], test_percentage=0.05):
    """
    Sorts input csv into map[device][app][action], then foreach action, split into test train
    (1 entry for test, remaining for train; typically that's 20% test 80% train)
    """
    sources_hierarchy = dict()

    for s in sources_files:
        fname = s.replace(DATA_PATH, '')
        parts = fname.split("_")
        device, app, action = parts[0], parts[1], parts[2]

        if not device in sources_hierarchy:
            sources_hierarchy[device] = dict()
        if not app in sources_hierarchy[device]:
            sources_hierarchy[device][app] = dict()
        if not action in sources_hierarchy[device][app]:
            sources_hierarchy[device][app][action] = []

        sources_hierarchy[device][app][action].append(s)

    sources_test_classic = []
    sources_train_classic = []

    for device in sources_hierarchy:
        for app in sources_hierarchy[device]:
            for action in sources_hierarchy[device][app]:

                total = len(sources_hierarchy[device][app][action])
                n_test = round(total * test_percentage)
                print("Test %% is", test_percentage, "=",n_test, "out of", total)
                current_n_test = 0
                for s in sorted(sources_hierarchy[device][app][action]):
                    if current_n_test<n_test:
                        sources_test_classic.append(s)
                        current_n_test += 1
                    else:
                        sources_train_classic.append(s)


    return sources_test_classic, sources_train_classic

def count_all_packets(events_all_devices):
    n_packets = dict()
    for device in events_all_devices:
        events = events_all_devices[device]
        if not device in n_packets:
            n_packets[device] = 0
        n = reduce(lambda a,b: a+b, [len(e['xs']) for e in events], 0) # just a deep sum
        n_packets[device] += n

    return n_packets

def equilibrate_events_across_app_or_action(events):
    counts = dict()
    for device in events:
        for app in events[device]:

            if not app in counts:
                counts[app] = 0

            for action in events[device][app]:
                counts[app] += len(events[device][app][action])

    min_number_events = min(counts.values())

    events_out = dict()

    # remove everything above the min # across devices
    for device in events:

        current_leaf_index = 0
        current_count = 0
        while current_count < min_number_events:
            for app in events[device]:
                for action in events[device][app]:
                    if len(events[device][app][action]) > current_leaf_index:
                        if not device in events_out:
                            events_out[device] = dict()
                        if not app in events_out[device]:
                            events_out[device][app] = dict()
                        if not action in events_out[device][app]:
                            events_out[device][app][action] = []
                        events_out[device][app][action].append(events[device][app][action][current_leaf_index])
                        current_count += 1
            current_leaf_index += 1
    return events_out


def equilibrate_events_across_devices(events):
    counts = dict()
    for device in events:
        if not device in counts:
            counts[device] = 0

        for app in events[device]:
            for action in events[device][app]:
                counts[device] += len(events[device][app][action])

    print("Devices event count pre-equalization:")
    for k in counts:
        print(k, counts[k])

    min_number_events = min(counts.values())

    events_out = dict()

    # remove everything above the min # across devices
    for device in events:

        current_leaf_index = 0
        current_count = 0
        while current_count < min_number_events:
            for app in events[device]:
                for action in events[device][app]:
                    if len(events[device][app][action]) > current_leaf_index:
                        if not device in events_out:
                            events_out[device] = dict()
                        if not app in events_out[device]:
                            events_out[device][app] = dict()
                        if not action in events_out[device][app]:
                            events_out[device][app][action] = []
                        events_out[device][app][action].append(events[device][app][action][current_leaf_index])
                        current_count += 1
            current_leaf_index += 1

    counts = dict()
    for device in events_out:
        if not device in counts:
            counts[device] = 0

        for app in events_out[device]:
            for action in events_out[device][app]:
                counts[device] += len(events_out[device][app][action])

    print("Devices event count post-equalization:")
    for k in counts:
        print(k, counts[k])

    return events_out

def equilibrate_events_across_apps(events):
    counts = dict()
    for device in events:
        for app in events[device]:
            if not app in counts:
                counts[app] = 0
            for action in events[device][app]:
                counts[app] += len(events[device][app][action])

    print("Devices app count pre-equalization:")
    for k in counts:
        print(k, counts[k])

    if len(counts.values())== 0:
        return events

    min_number_events = min(counts.values())

    events_out = dict()

    # remove everything above the min # across devices
    for device in events:
        for app in events[device]:
            current_leaf_index = 0
            current_count = 0
            while current_count < min_number_events:
                for action in events[device][app]:
                    if len(events[device][app][action]) > current_leaf_index:
                        if not device in events_out:
                            events_out[device] = dict()
                        if not app in events_out[device]:
                            events_out[device][app] = dict()
                        if not action in events_out[device][app]:
                            events_out[device][app][action] = []
                        events_out[device][app][action].append(events[device][app][action][current_leaf_index])
                        current_count += 1
            current_leaf_index += 1

    counts = dict()
    for device in events_out:
        for app in events_out[device]:
            if not app in counts:
                counts[app] = 0
            for action in events_out[device][app]:
                counts[app] += len(events_out[device][app][action])

    print("Devices event count post-equalization:")
    for k in counts:
        print(k, counts[k])

    return events_out

def extract_comm_direction():
    """
    Use a referenciel of the direction (i.e. the master's name.)
    If it changes, the direction should change as well
    """
    global all_columns, packet_store, master

    if not "Communication" in all_columns:
        print("Communication is missing in all_columns")
        sys.exit(1)

    first_comm = list(packet_store.keys())[0]
    first_packet = list(packet_store[first_comm].keys())[0]
    comm = packet_store[first_comm][first_packet][0]["Communication"]
    master = comm[comm.find('"', 8) +1 : comm.find('"', comm.find('"', 8)+1)]
    print("mast: " + master)
    print()

# --------------------------------------
# Main logic of this script:

def rebuild_all_datasets(sources_files=None, force_rebuild=True):
    global all_columns, packet_store, master

    if sources_files is None:
        sources_files = find_sources(folder=DATA_PATH)
    find_common_columns(sources_files)

    print("Common columns:", all_columns)

    sources_files = sorted(sources_files)

    for i, source_file in enumerate(sources_files):
        packet_store[source_file] = load_cache(source_file)

        if force_rebuild or packet_store[source_file] == None:
            print("Loading and cleaning dataset", source_file)

            parse_dataset(source_file)
            packet_store_cleanup(packet_store[source_file])
            cache(source_file, packet_store[source_file])
            if i == 0:
                extract_comm_direction()
        dataset_file_to_xy_features(source_file) # map but more importantly cache the results

    for source_file in sources_files:
        print("Dataset", source_file, "contains", len(packet_store[source_file]), "packets")

if __name__ == "__main__":
    print("Parsing all files in current directory")
    rebuild_all_datasets()
