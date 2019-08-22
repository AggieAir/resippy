from sklearn.metrics import roc_curve, auc
from numpy import ndarray


def roc_from_truth_and_detection_image(truth_map,           # type: ndarray
                                       detection_map,       # type: ndarray
                                       ):
    fpr, tpr, thresholds = roc_curve(truth_map.ravel(), detection_map.ravel())
    return fpr, tpr, thresholds