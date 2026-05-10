import numpy
import json
import os

import matplotlib.pyplot as plt


class EvaluateExperiment:


    def __init__(self, path):
        
        self.path = path

        self.model_info           = self._load_model_info(path + "model.txt")
        self.metric_train_quality = self._load_metric_quality(path + "metric_train_quality.txt")
        self.metric_test_quality  = self._load_metric_quality(path + "metric_test_quality.txt")
        self.weights_stats        = self._load_weights_stats(path + "model_weights.txt")

        self.num_epoch = len(self.metric_train_quality["accuracy"])

    def process(self):

        self._create_plots()

        return self._create_md()
    


    def _create_md(self):
        result_txt_md = ""
        result_txt_md+= "# Experiment path : " + str(self.path)
        result_txt_md+= "\n\n\n\n"

        result_txt_md+= "## Model info \n"

        result_txt_md+= self._json_to_markdown(self.model_info)

        result_txt_md+= "\n\n\n\n"  

        result_txt_md+= "## Training Results\n\n"
        result_txt_md+= self._build_results_markdown(self.metric_train_quality)
        result_txt_md+= "\n\n\n"

        result_txt_md+= "## Testing Results\n\n"
        result_txt_md+= self._build_results_markdown(self.metric_test_quality)
        result_txt_md+= "\n\n\n"

        result_txt_md+= "## Quantization scheme\n\n"
        img_path = "./diagrams/diagrams_quantization_"+ self.model_info["model_name"]
        result_txt_md+= "![plot](" + img_path + ")" + "\n\n"

        result_txt_md+= "## Result plots\n\n"
        img_path = "../../src/"+ self.path + "/plots/accuracy.png"
        result_txt_md+= "![plot](" + img_path + ")" + "\n\n"

        img_path = "../../src/"+ self.path + "/plots/f1.png"
        result_txt_md+= "![plot](" + img_path + ")" + "\n\n"

        result_txt_md+= "## Weights distribution\n\n"
        img_path = "../../src/"+ self.path + "/plots/weights.png"
        result_txt_md+= "![plot](" + img_path + ")" + "\n\n"
        
        result_txt_md+= "\n\n\n"

        result_txt_md+= "# Model comparison\n\n"
        result_txt_md+= "![plot](" + "summary_accuracy.png" + ")" + "\n\n"


        
        return result_txt_md

    def _create_plots(self):
        if not os.path.exists(self.path + "./plots/"):
            os.makedirs(self.path + "./plots/")

        # accuracy
        plt.cla()
        plt.clf()
        plt.title("Accuracy")
        plt.plot(self.metric_train_quality["accuracy"], label = "training", color = "blue", lw=2.0)
        plt.plot(self.metric_test_quality["accuracy"], label = "testing", color = "red", lw=3.0)
        plt.xlabel("epoch")
        plt.xticks(list(range(self.num_epoch)))
        plt.ylabel("accuracy")
        plt.legend()
        
        plt.savefig(self.path + "./plots/" + "accuracy.png", dpi=300)


        plt.cla()
        plt.clf()
        plt.title("F1")
        plt.plot(self.metric_train_quality["f1"], label = "training", color = "blue", lw=2.0)
        plt.plot(self.metric_test_quality["f1"], label = "testing", color = "red", lw=3.0)
        plt.xlabel("epoch")
        plt.xticks(list(range(self.num_epoch)))
        plt.ylabel("f1")
        plt.legend()
        
        plt.savefig(self.path + "./plots/" + "f1.png", dpi=300)



   
        last = self.weights_stats[-1]

        x = numpy.array(last["values"])
        y = numpy.array(last["count"])

        plt.cla()
        plt.clf()
        
        plt.figure(figsize=(15, 10))

        width = numpy.mean(numpy.diff(x))

        plt.bar(
            x,
            y,
            width=width,
            align="center",
        )

        plt.xlabel("Weight Value")
        plt.ylabel("Density")
        plt.title("Weight Distribution")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        plt.savefig(self.path + "./plots/" + "weights.png", dpi=300)


    

    def _build_results_markdown(self, results):
        result_txt_md = ""        

        # =========================================================
        # Summary table
        # =========================================================
        result_txt_md += "### Summary\n\n"

        result_txt_md += "| Metric | Value |\n"
        result_txt_md += "|---|---|\n"
        result_txt_md += f"| Accuracy | {results['accuracy'][-1]:.5f} |\n"
        result_txt_md += f"| Precision | {results['precission'][-1]:.5f} |\n"
        result_txt_md += f"| Recall | {results['recall'][-1]:.5f} |\n"
        result_txt_md += f"| F1 | {results['f1'][-1]:.5f} |\n\n"

        # =========================================================
        # Per-class metrics table
        # =========================================================
        result_txt_md += "### Per Class Metrics\n\n"

        result_txt_md += (
            "| Class | TP | TN | FP | FN | Support | "
            "Accuracy | Precision | Recall | F1 |\n"
        )

        result_txt_md += "|---|---|---|---|---|---|---|---|---|---|\n"

        per_class = results["per_class"]

        for cls, metrics in per_class.items():

            result_txt_md += (
                f"| {cls} "
                f"| {metrics['tp']} "
                f"| {metrics['tn']} "
                f"| {metrics['fp']} "
                f"| {metrics['fn']} "
                f"| {metrics['support']} "
                f"| {metrics['accuracy']:.5f} "
                f"| {metrics['precision']:.5f} "
                f"| {metrics['recall']:.5f} "
                f"| {metrics['f1']:.5f} |\n"
            )

        result_txt_md += "\n"

        # =========================================================
        # Confusion matrix table
        # =========================================================
        result_txt_md += "### Confusion Matrix\n\n"

        cm = results["confusion_matrix"]

        num_classes = len(cm)

        # Header
        result_txt_md += "| Actual \\ Pred | "
        result_txt_md += " | ".join(str(i) for i in range(num_classes))
        result_txt_md += " |\n"

        result_txt_md += "|" + "---|" * (num_classes + 1) + "\n"

        # Rows
        for i, row in enumerate(cm):

            result_txt_md += f"| {i} | "
            result_txt_md += " | ".join(str(v) for v in row)
            result_txt_md += " |\n"

        result_txt_md += "\n"

        return result_txt_md

    def _load_model_info(self, file_name):
        
        lines = ""
        with open(file_name) as file:
            for line in file:
                lines+= line.rstrip()


        model_info = json.loads(lines)

        return model_info
        

    def _load_jsonl(self, file_name):
        rows = []

        with open(file_name, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))

        return rows
    



    def _load_metric_quality(self, file_name):

        result = {}

        data = self._load_jsonl(file_name)

        result["accuracy"]      = self._extract_column(data, "accuracy")
        result["precission"]    = self._extract_column(data, "macro_precision")
        result["recall"]        = self._extract_column(data, "macro_recall")
        result["f1"]            = self._extract_column(data, "macro_f1")

        result["per_class"]     = data[-1]["per_class"]


        cm = data[-1]["confusion_matrix"]
        result["confusion_matrix"] = cm

        return result
    

    def _load_weights_stats(self, file_name):
        data = self._load_jsonl(file_name)

        return data


    def _extract_column(self, data, key):
        result = []

        for row in data:
            result.append(row[key])

        return numpy.array(result)


    def _json_to_markdown(self, data, indent=0):
        md = ""

        if isinstance(data, dict):
            for key, value in data.items():
                md += "  " * indent + f"- **{key}**:\n"
                md += self._json_to_markdown(value, indent + 1)

        elif isinstance(data, list):
            for item in data:
                md += "  " * indent + "- \n"
                md += self._json_to_markdown(item, indent + 1)

        else:
            md += "  " * indent + f"{data}\n"

        return md


def plot_final_weight_distribution(rows, figsize=(10, 5)):
    """
    Plot histogram/density from final epoch.

    Expects:
    - values = bin centers
    - count = densities/frequencies
    """

    last = rows[-1]

    x = numpy.array(last["values"])
    y = numpy.array(last["count"])

    print(y)

    plt.figure(figsize=figsize)

    width = numpy.mean(numpy.diff(x))

    plt.bar(
        x,
        y,
        width=width,
        align="center",
    )

    plt.xlabel("Weight Value")
    plt.ylabel("Density")
    plt.title("Final Weight Distribution")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.show()

if __name__ == "__main__":
    f = open("../doc/results/results.md", "w")

    baseline = EvaluateExperiment("results/baseline_mlp/")
    md_desc = baseline.process()
    f.write(md_desc)

    memristor_q4 = EvaluateExperiment("results/memristor_q4_mlp/")
    md_desc = memristor_q4.process()
    f.write(md_desc)

    memristor_q4_norm = EvaluateExperiment("results/memristor_q4_norm_mlp/")
    md_desc = memristor_q4_norm.process()
    f.write(md_desc)

    f.close()


    num_epoch = len(baseline.metric_test_quality["accuracy"])
    plt.cla()
    plt.clf()
    plt.title("Accuracy")
    
    plt.plot(baseline.metric_test_quality["accuracy"], label = "baseline", color = "blue", lw=3.0)
    plt.plot(memristor_q4.metric_test_quality["accuracy"], label = "memristor_q4", color = "red", lw=3.0)
    plt.plot(memristor_q4_norm.metric_test_quality["accuracy"], label = "memristor_q4_norm", color = "green", lw=3.0)
    
    plt.xlabel("epoch")
    plt.xticks(list(range(num_epoch)))
    plt.ylabel("accuracy")
    plt.legend()

    plt.savefig("../doc/results/summary_accuracy.png", dpi=300)
