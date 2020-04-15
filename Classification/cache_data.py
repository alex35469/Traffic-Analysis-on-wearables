
from build_datasets import *


############################## GLOBAL VARIABLES ##########################


DATA_PATH = ["./data/huawei/elapsed_time/open-12/"] #, "./data/huawei/Shazam_openNotFound/"]


sources_files = find_sources(DATA_PATH)

rebuild_all_datasets(sources_files, True)
