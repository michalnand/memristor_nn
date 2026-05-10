from utils import *
from model import *


def loss_func(y_target, y_pred):
    loss_func_ = torch.nn.CrossEntropyLoss()
    return loss_func_(y_pred, y_target)

if __name__ == "__main__":

    dataset_train = DatasetMnist(train=True)
    dataset_test  = DatasetMnist(train=False)

    
    # baseline FP32 train    
    hyperparameters = {}
    hyperparameters["num_epochs"]       = 20
    hyperparameters["batch_size"]       = 32
    hyperparameters["learning_rate"]    = 0.001
    hyperparameters["optimizer"]        = torch.optim.Adam
    hyperparameters["loss_func"]        = loss_func
    hyperparameters["results_path"]     = "results/baseline_mlp/"

    pipeline = SupervisedPipeline(dataset_train, dataset_test, BaselineMLP, hyperparameters, device="cpu")

    pipeline.run_training()
    
    
    
    # memristor model, 4bit quantization
    hyperparameters = {}
    hyperparameters["num_epochs"]       = 20
    hyperparameters["batch_size"]       = 32
    hyperparameters["learning_rate"]    = 0.001
    hyperparameters["optimizer"]        = torch.optim.Adam
    hyperparameters["loss_func"]        = loss_func 
    hyperparameters["results_path"]     = "results/memristor_q4_mlp/"
    
    pipeline = SupervisedPipeline(dataset_train, dataset_test, MemristorMLP, hyperparameters, device="cpu")
    
    pipeline.run_training()
    


    # memristor model, 4bit quantization, layer norm
    hyperparameters = {}
    hyperparameters["num_epochs"]       = 20
    hyperparameters["batch_size"]       = 32
    hyperparameters["learning_rate"]    = 0.001
    hyperparameters["optimizer"]        = torch.optim.Adam
    hyperparameters["loss_func"]        = loss_func 
    hyperparameters["results_path"]     = "results/memristor_q4_norm_mlp/"  
    
    pipeline = SupervisedPipeline(dataset_train, dataset_test, MemristorMLPNorm, hyperparameters, device="cpu")
    
    pipeline.run_training()
