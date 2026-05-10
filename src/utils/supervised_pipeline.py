from .performance_metric import *
from .classification_metric import *

import os
import json



class SupervisedPipeline:


    def __init__(self, dataset_train, dataset_test, ModelClass, hyperparameters, device = "cpu"):

        self.dataset_train = dataset_train
        self.dataset_test  = dataset_test
        
        input_shape  = dataset_train.input_shape
        output_shape = dataset_train.output_shape

        
        self.device = device

        self.num_epochs    = hyperparameters["num_epochs"]
        self.learning_rate = hyperparameters["learning_rate"]
        self.batch_size    = hyperparameters["batch_size"]
        self.results_path  = hyperparameters["results_path"]

        if not os.path.exists(self.results_path):
            os.makedirs(self.results_path)
        

        self.model = ModelClass(input_shape, output_shape)
        self.model.to(device)

        self.optimizer = hyperparameters["optimizer"](self.model.parameters(), lr=self.learning_rate)
        self.loss_func = hyperparameters["loss_func"]

        self.classification_metric_train    = ClassificationMetric(num_classes=output_shape[0])
        self.classification_metric_test     = ClassificationMetric(num_classes=output_shape[0])

        self.performance_metric_train       = PerformanceMetric()
        self.performance_metric_test        = PerformanceMetric()


        self._save_model_into()

    def run_training(self):

        # files for logs
        self._create_log("metric_train_quality")
        self._create_log("metric_test_quality")
        self._create_log("metric_train_performance")
        self._create_log("metric_test_performance")
        self._create_log("model_weights")


        for epoch in range(self.num_epochs):
            print("starting epoch ", epoch, "\n")

            self.classification_metric_train.clear()
            self.classification_metric_test.clear()
            self.performance_metric_train.clear()
            self.performance_metric_test.clear()
            
            print("training")
            self._epoch_train()
            print("testing")
            self._epoch_test()
            print("stats")
            
            result = self._weight_stats()
            self._append_log("model_weights", str(json.dumps(result)))


            result = self.classification_metric_train.get()
            self._append_log("metric_train_quality", str(json.dumps(result)))

            print("training_accuracy", round(result["accuracy"], 4))
            print("training_f1", round(result["macro_f1"], 4))


            result = self.classification_metric_test.get()
            self._append_log("metric_test_quality", str(json.dumps(result)))

            print("testing_accuracy", round(result["accuracy"], 4))
            print("testing_f1", round(result["macro_f1"], 4))


            result = self.performance_metric_train.get()
            self._append_log("metric_train_performance", str(json.dumps(result)))
            print("batch_time", round(result["batch_time_mean"], 4))


            result = self.performance_metric_test.get()
            self._append_log("metric_test_performance", str(json.dumps(result)))
            print("batch_time", round(result["batch_time_mean"], 4))

            print("\n\n")
            print(50*"=")
            print("\n\n")



    def _epoch_train(self):
        
        num_batches = len(self.dataset_train)//self.batch_size

        for n in range(num_batches):
            x, y = self.dataset_train.get_batch(self.batch_size)

            x = x.to(self.device)
            y = y.to(self.device)

            y_pred = self.model(x)


            self.optimizer.zero_grad()
            loss = self.loss_func(y, y_pred)
            loss.backward()
            self.optimizer.step()



            self.classification_metric_train.step(y, y_pred)
            self.performance_metric_train.step(self.batch_size)
    
    def _epoch_test(self):
        num_batches = len(self.dataset_test)//self.batch_size

        for n in range(num_batches):    
            x, y = self.dataset_test.get_batch(self.batch_size)

            x = x.to(self.device)
            y = y.to(self.device)

            y_pred = self.model(x)

            self.classification_metric_test.step(y, y_pred)
            self.performance_metric_test.step(self.batch_size)

        '''
        for n in range(len(self.dataset_test)):
            x, y = self.dataset_test[n]

            x = x.to(self.device).unsqueeze(0)
            y = y.to(self.device).unsqueeze(0)

            y_pred = self.model(x)

            self.classification_metric_test.step(y, y_pred)
            self.performance_metric_test.step(1)
        '''

    def _weight_stats(self):
        print("_weight_stats")
        weights = self.model.get_weights()

        # flatten all tensors and concatenate into one vector
        all_weights = numpy.concatenate([numpy.asarray(w.detach().cpu().numpy()).ravel() for w in weights])

        result = {}

        # Global statistics
        result["mean"] = float(numpy.mean(all_weights))
        result["std"] = float(numpy.std(all_weights))
        result["min"] = float(numpy.min(all_weights))
        result["max"] = float(numpy.max(all_weights))

        # Histogram
        num_bins = 50
        counts, bin_edges = numpy.histogram(all_weights, bins=num_bins, density=True)

        # Use bin centers as histogram values
        bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

        result["values"] = bin_centers.tolist()
        result["count"] = counts.tolist()

        return result
        



    def _create_log(self, log_name):
        log_file = open(self.results_path + log_name + ".txt", "w")
        log_file.close()

    def _append_log(self, log_name, data):
        log_file = open(self.results_path + log_name + ".txt", "a+")
        log_file.write(data+"\n")
        log_file.close()


    def _save_model_into(self):
        result = {}
        result["model_name"]    = self.model.__class__.__name__
        result["model_summary"] = str(self.model)

        result["model_modules"] = []
        for name, module in self.model.named_modules():
            
            if len(str(name)) > 0:
                tmp = {}
                tmp["name"] = str(name)
                tmp["module"] = str(module)

                result["model_modules"].append(tmp)
        
        result["model_parameters"] = []
        for name, param in self.model.named_parameters():

            tmp = {}
            tmp["name"] = str(name)
            tmp["parameters_count"] = int(numpy.prod(param.shape))
            tmp["parameters_shape"] = list((param.shape))

            result["model_parameters"].append(tmp)


        
        

        result = str(json.dumps(result, indent=4))
        log_file = open(self.results_path + "model" + ".txt", "w")
        log_file.write(result+"\n")
        log_file.close()
