import torch
import numpy

class ClassificationMetric:
    def __init__(self, num_classes):
        self.num_classes = num_classes
        self.clear()

    def step(self, y_gt, y_pred):
        # y_gt contains ground truth integer
        # y_pred contains confidence vector
        
        if isinstance(y_gt, torch.Tensor):
            y_gt = y_gt.detach().cpu().numpy()

        if isinstance(y_pred, torch.Tensor):
            y_pred = y_pred.detach().cpu().numpy()

        y_gt    = numpy.asarray(y_gt).reshape(-1)
        y_pred  = numpy.asarray(y_pred)

        self.y_gt.extend(y_gt.tolist())
        self.y_pred.extend(y_pred.tolist())


        

    def clear(self):
        self.y_gt    = []
        self.y_pred  = []


    def get(self):
        result = {}

        dp = 5

        # convert to numpy arrays
        y_gt = numpy.asarray(self.y_gt, dtype=numpy.int64)

        # predicted class index, max value
        y_pred_logits = numpy.asarray(self.y_pred)
        y_pred        = numpy.argmax(y_pred_logits, axis=1)

        n = self.num_classes

        # confusion matrix
        # rows    = ground truth
        # columns = prediction
        cm = numpy.zeros((n, n), dtype=numpy.int64)
        for gt, pred in zip(y_gt, y_pred):
            cm[gt, pred]+= 1


        # per class metric
        tp = numpy.diag(cm)
        fp = cm.sum(axis=0) - tp
        fn = cm.sum(axis=1) - tp
        tn = cm.sum() - (tp + fp + fn)

        eps = 1e-12

        precision = tp / (tp + fp + eps)
        recall = tp / (tp + fn + eps)
        f1 = 2.0 * precision * recall / (precision + recall + eps)

        per_class_accuracy = tp / (cm.sum(axis=1) + eps)


        # global metric, summary
        accuracy = numpy.sum(tp) / (cm.sum() + eps)

        macro_precision = numpy.mean(precision)
        macro_recall = numpy.mean(recall)
        macro_f1 = numpy.mean(f1)

        # weighted metrics
        support = cm.sum(axis=1)
        weights = support / (support.sum() + eps)

        weighted_precision = numpy.sum(precision * weights)
        weighted_recall = numpy.sum(recall * weights)
        weighted_f1 = numpy.sum(f1 * weights)


        # micro metrics
        micro_tp = numpy.sum(tp)
        micro_fp = numpy.sum(fp)
        micro_fn = numpy.sum(fn)

        micro_precision = micro_tp / (micro_tp + micro_fp + eps)
        micro_recall = micro_tp / (micro_tp + micro_fn + eps)
        micro_f1 = (2.0 * micro_precision * micro_recall/ (micro_precision + micro_recall + eps))


        # arrange output into json like structure

        result["num_samples"] = int(numpy.sum(tp) + numpy.sum(fp) + numpy.sum(fn) + numpy.sum(tn))
        result["accuracy"] = round(float(accuracy), dp)

        result["macro_precision"] = round(float(macro_precision), dp)
        result["macro_recall"] = round(float(macro_recall), dp)
        result["macro_f1"] = round(float(macro_f1), dp)

        result["weighted_precision"] = round(float(weighted_precision), dp)
        result["weighted_recall"] = round(float(weighted_recall), dp)
        result["weighted_f1"] = round(float(weighted_f1), dp)

        result["micro_precision"] = round(float(micro_precision), dp)
        result["micro_recall"] = round(float(micro_recall), dp)
        result["micro_f1"] = round(float(micro_f1), dp)

        result["confusion_matrix"] = cm.tolist()

        result["per_class"] = {}


        for c in range(n):
            result["per_class"][c] = {
                "tp": int(tp[c]),
                "tn": int(tn[c]),
                "fp": int(fp[c]),
                "fn": int(fn[c]),   
                "support": int(support[c]),
                "accuracy": round(float(per_class_accuracy[c]), dp),
                "precision": round(float(precision[c]), dp),
                "recall": round(float(recall[c]), dp),
                "f1": round(float(f1[c]), dp),
            }

        return result