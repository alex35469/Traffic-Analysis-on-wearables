
from build_datasets import *
import os

print("creating .cache folder")

# Create the .cache if none exisstant
if not os.path.isdir("./.cache"):
    os.mkdir("./.cache")


print("Importing data")
DATA_PATH = [ # Single Action and Transfer
             "data/huawei/open-3/",

             "data/fossil/open-6/",
             "data/iwatch/batch-1/",
             "data/huawei/open-6/",

             # in-App  action
             "data/huawei/Endomondo-1/",
             "data/huawei/DiabetesM-3/",
             "data/huawei/DiabetesM-4/",
             "data/huawei/FoursquareCityGuide-1/",
             "data/huawei/HealthyRecipes-1/",
             "data/huawei/Lifesum-1/",
             "data/huawei/Playstore-1/",

             # Elapsed time
             "data/huawei/elapsed-time/open-7/",
             "data/huawei/elapsed-time/open-8/",
             "data/huawei/elapsed-time/open-9/",
             "data/huawei/elapsed-time/open-10/",
             "data/huawei/elapsed-time/open-11/",
             "data/huawei/elapsed-time/open-12/",
             "data/huawei/elapsed-time/open-13/",
             "data/huawei/elapsed-time/open-14/",
             "data/huawei/elapsed-time/open-15/",
             "data/huawei/elapsed-time/open-16/",

             # Long-run
             "data/huawei/force-stop-2/",
             "data/huawei/NoApp_NoAction/"]

sources_files = find_sources(DATA_PATH)

rebuild_all_datasets(sources_files, True)
