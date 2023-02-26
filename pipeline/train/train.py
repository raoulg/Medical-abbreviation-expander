import polars as pl
import torch
import torch.optim as optim
from datatools import Datastreamer, FileHandler, TxtDataset
from layers import AbbrvtExpander
from metrics import Accuracy
from settings import datasettings, filesettings, modelsettings
from settings import DataSettings
from trainloop import trainloop
from loguru import logger
from datetime import datetime


def train():
    # create datastreamers
    filehandler = FileHandler(filesettings)
    maps, train = filehandler._get_latest()

    mapping = filehandler.load_mapping(maps)
    data = filehandler.load_data(train)
    data = data.with_columns(pl.Series(name="idx", values=[*range(len(data))]))
    logger.info(f"using datasettings {datasettings}")
    logger.info(f"The loaded data has size {len(data)}")
    
    traindata = data.sample(frac=datasettings.trainfrac)
    valdata = data.join(traindata, on="idx", how="anti")

    traindataset = TxtDataset(traindata, settings=datasettings)
    valdataset = TxtDataset(valdata, settings=datasettings)

    trainstreamer = Datastreamer(
        traindataset, batchsize=datasettings.batchsize, mapping=mapping
    )

    valstreamer = Datastreamer(
        valdataset, batchsize=datasettings.batchsize, mapping=mapping
    )

    # trainloop
    logger.info(f"using modelsettings {modelsettings}")
    model = AbbrvtExpander(modelsettings)
    loss = torch.nn.CrossEntropyLoss()
    accuracy = Accuracy()
    model, testloss = trainloop(
        epochs=modelsettings.epochs,
        model=model,
        optimizer=optim.Adam,
        learning_rate=modelsettings.learning_rate,
        loss_fn=loss,
        metrics=[accuracy],
        train_dataloader=trainstreamer.stream(),
        val_dataloader=valstreamer.stream(),
        log_dir="logs",
        train_steps=10,
        eval_steps=10,
        tunewriter=["tensorboard"],
    )

    logger.info("Finished train and validation loop. Starting test.")
    # test accuracy
    testfile  = filesettings.datadir / "raw/test_set.csv"
    testdata = filehandler.load_data(testfile)
    logger.info(f"testset has size {len(testdata)}")
    testsettings = DataSettings(targetcol="expansion", txtcol="sample", trainfrac=1.0, batchsize=len(testdata))
    test = TxtDataset(testdata, testsettings)
    teststream = Datastreamer(test, batchsize=testsettings.batchsize, mapping=mapping).stream()
    X, y_, y = next(teststream)
    yhat = model(X, y_)
    acc = accuracy(y, yhat)
    logger.info(f"testaccuracy: {acc}")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    modelpath = modelsettings.modeldir / (timestamp + "trainedmodel.pt")
    logger.success(f"saving model to {modelpath}")
    torch.save(model, modelpath)

if __name__ == "__main__":
    train()
