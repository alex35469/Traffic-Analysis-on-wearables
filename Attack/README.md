# Attack
Contains the attack on single-action capture and longrun capture, also contains temporal evaluation and transferability.
Please refer to the [Master Thesis Report](https://github.com/alex35469/Traffic-Analysis-on-wearables/blob/master/Thesis/masters_thesis_Traffic_Analysis_of_Smartwatches_final.pdf) for more information


## Setup
Make sure the following files exists:

```
# Single Action Capture and Transferability
"data/huawei/open-3/",
"data/fossil/open-6/",
"data/iwatch/batch-1/",
"data/huawei/open-6/",

# in-App  action
"data/huawei/Endomondo-1/",
"data/huawei/DiabetesM-2/",
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
"data/huawei/NoApp_NoAction/"
```

and run

`python cache_data.py`

note: This might take some time.

Please, also create a folder named `plots` in this directory if it does not exist yet. All plots will go in this folder when launching scripts.


## Reproducibilty

### Single-Action capture evaluation
To reproduce the results on Single-Action capture (Chap):

 `python evalute.py <smartwatch>`
where smartwatch can be `huawei_open`, `huawei_inApp`, `huawei`, `fossil` or `iwatch`.

Print on screen the averaged accuracy with 95% confidence interval using 50 random split cross-validation 25% test 75% train. Finally, the script makes one realisation print the accuracy and plot 3 confusion matrix (with different layout) for that realisation

### Transferability
To reproduce the results on Transferability:

`python transfer_evaluation.py`

Print on screen the averaged accuracy with 95% confidence interval using 50 random split cross-validation 25% test 75% train for the two watches (one in the trained set the other one in the test set and vice versa), when filtering is/isn't used and when fit packages are merged. Finally, for each watch, the script makes one realisation print the accuracy and plot 3 confusion matrix (with different layout) for that realisation.


### Accuracy over Time
To reproduce the results on Accuracy over Time capture:

`python temporal_evaluation.py`

Print on screen the averaged accuracy decrease for each day and averaged over all day. Moreover, it will plot the difference between the fresh and delayed accuracy, and plot also the accuracy gain compared to the delayed accuracy by class for each. All of this doubled by either with or without learning adjustement (3 days learning instead of 1)


### Long-run Attack
To reproduce the results on Long-run Attack:

`python longrun_evaluation.py`

Print on sceen the the best threshold for the Decision Maker according to the F1 score. And the associate Precision, Recall and F1 score. Plot also the Precision, Recall, F1 score against different threshold values.



## Exploration
The jupyter notebook files shows the results in an inter-active fashion.`application_identification.ipynb` for the attack on Single-Action capture and `Longrun identification.ipynb` for attack on long-run captures.
