import time


def write_logs(log_fname, log, how='a'):
    "Write to log"
    path = "./logs/" + log_fname + ".log"
    f = open(path, how)
    f.write(log)
    f.close()
    if how == "w":
        print("log file: " + path +" init")


def tprint(txt, log_fname=None, t_ref = None):
    "Print with time and log to file"

    currentTime = time.strftime("%d/%m/%y %H:%M:%S", time.localtime())
    txt = ' [' + currentTime + '] ' + txt
    if t_ref is not None:
        t_diff = str(round( time.time() - t_ref,1))
        txt += ' (' + t_diff + ' after capture started)'
    print(txt)
    if log_fname != None:
        write_logs(log_fname, txt + '\n')

def sprint(txt, log_fname, t_ref):
    "synthesis log to file"
    t_diff = str(round( time.time() - t_ref,1))
    txt = t_diff  + ', ' + txt
    write_logs(log_fname, txt + '\n')
