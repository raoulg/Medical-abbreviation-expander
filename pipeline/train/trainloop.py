from pathlib import Path
from typing import Callable, Dict, Iterator, List, Protocol, Tuple, Type

# import mlflow
import torch
from layers import AbbrvtExpander
from loguru import logger
from metrics import Metric
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm


class GenericModel(Protocol):
    train: Callable
    eval: Callable
    parameters: Callable

    def __call__(self, *args, **kwargs) -> torch.Tensor:
        pass


def trainbatches(
    model: Type[AbbrvtExpander],
    traindatastreamer: Iterator,
    loss_fn: Callable,
    optimizer: torch.optim.Optimizer,
    train_steps: int,
) -> float:
    model.train()  # type: ignore
    train_loss: float = 0.0
    for _ in tqdm(range(train_steps), colour="#1e4706"):
        x, cand, y = next(iter(traindatastreamer))
        optimizer.zero_grad()
        yhat = model(x, cand)  # type: ignore
        loss = loss_fn(yhat, y)
        loss.backward()
        optimizer.step()
        train_loss += loss.detach().numpy()
    train_loss /= train_steps
    return train_loss


def evalbatches(
    model: Type[AbbrvtExpander],
    valdatastreamer: Iterator,
    loss_fn: Callable,
    metrics: List[Metric],
    eval_steps: int,
) -> Tuple[Dict[str, float], float]:
    model.eval()  # type: ignore
    test_loss: float = 0.0
    metric_dict: Dict[str, float] = {}
    for _ in range(eval_steps):
        x, cand, y = next(iter(valdatastreamer))
        yhat = model(x, cand)  # type: ignore
        test_loss += loss_fn(yhat, y).detach().numpy()
        for m in metrics:
            metric_dict[str(m)] = (
                metric_dict.get(str(m), 0.0)
                + m(y, yhat).detach().numpy()  # type:ignore
            )

    test_loss /= eval_steps
    for key in metric_dict:
        metric_dict[str(key)] = metric_dict[str(key)] / eval_steps
    return metric_dict, test_loss


def trainloop(
    epochs: int,
    model: Type[AbbrvtExpander],
    optimizer: torch.optim.Optimizer,
    learning_rate: float,
    loss_fn: Callable,
    metrics: List[Metric],
    train_dataloader: Iterator,
    val_dataloader: Iterator,
    log_dir: Path,
    train_steps: int,
    eval_steps: int,
    patience: int = 10,
    factor: float = 0.9,
    tunewriter: List[str] = ["tensorboard", "gin", "mlflow", "ray"],
    weight_decay: float = 1e-5,
) -> Tuple[Type[AbbrvtExpander], float]:
    """

    Args:
        epochs (int) : Amount of runs through the dataset
        model: A generic model with a .train() and .eval() method
        optimizer : an uninitialized optimizer class. Eg optimizer=torch.optim.Adam
        learning_rate (float) : floating point start value for the optimizer
        loss_fn : A loss function
        metrics (List[Metric]) : A list of callable metrics.
            Assumed to have a __repr__ method implemented, see src.models.metrics
            for Metric details
        train_dataloader, val_dataloader (Iterator): data iterators
        log_dir (Path) : where to log stuff when not using the tunewriter
        train_steps, eval_steps (int) : amount of times the Iterators are called for a
            new batch of data.
        patience (int): used for the ReduceLROnPlatues scheduler. How many epochs to
            wait before dropping the learning rate.
        factor (float) : fraction to drop the learning rate with, after patience epochs
            without improvement in the loss.
        tunewriter (List[str]) :
            A list of all the options.
                "tensorboard" creates a subdir with a timestamp, and a SummaryWriter
                is invoked to write in that subdir for Tensorboard use.
                "gin" simply writes the gin config to a file.
                hyperparameters to pick.
                "mlflow" uses the MLflow framework for logging.

    Returns:
        _type_: _description_
    """

    optimizer_: torch.optim.Optimizer = optimizer(
        model.parameters(), lr=learning_rate, weight_decay=weight_decay  # type: ignore
    )

    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer_,
        factor=factor,
        patience=patience,
    )

    if "tensorboard" in tunewriter:
        # log_dir = data_tools.dir_add_timestamp(log_dir)
        writer = SummaryWriter(log_dir=log_dir)

    for epoch in tqdm(range(epochs), colour="#1e4706"):
        train_loss = trainbatches(
            model, train_dataloader, loss_fn, optimizer_, train_steps
        )

        metric_dict, test_loss = evalbatches(
            model, val_dataloader, loss_fn, metrics, eval_steps
        )

        scheduler.step(test_loss)

        # if "mlflow" in tunewriter:
        #     mlflow.log_metric("train loss", train_loss, step=epoch)
        #     mlflow.log_metric("test loss", test_loss, step=epoch)
        #     for m in metric_dict:
        #         mlflow.log_metric(f"metric/{m}", metric_dict[m], step=epoch)
        #     lr = [group["lr"] for group in optimizer_.param_groups][0]
        #     mlflow.log_metric("learning_rate", lr, step=epoch)

        if "tensorboard" in tunewriter:
            writer.add_scalar("Loss/train", train_loss, epoch)
            writer.add_scalar("Loss/test", test_loss, epoch)
            for m in metric_dict:
                writer.add_scalar(f"metric/{m}", metric_dict[m], epoch)
            lr = [group["lr"] for group in optimizer_.param_groups][0]
            writer.add_scalar("learning_rate", lr, epoch)

        metric_scores = [f"{v:.4f}" for v in metric_dict.values()]
        logger.info(
            f"Epoch {epoch} train {train_loss:.4f} test {test_loss:.4f} metric {metric_scores}"  # noqa E501
        )

    return model, test_loss
