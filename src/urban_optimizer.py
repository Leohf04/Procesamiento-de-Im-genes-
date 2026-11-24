"""Protocol-aligned optimizer and scheduler construction."""
import torch


def build_optimizer_and_scheduler(model, task, config):
    """Build optimizer/scheduler for one urban-v1 task without stepping it."""
    if task not in {"semantic", "instances"}:
        raise ValueError("task must be semantic or instances")
    lr = float(config["learning_rate"])
    if lr <= 0:
        raise ValueError("learning_rate must be positive")
    if task == "semantic":
        optimizer = torch.optim.AdamW(
            model.parameters(), lr=lr,
            weight_decay=float(config.get("weight_decay", 1e-4)),
        )
    else:
        optimizer = torch.optim.SGD(
            model.parameters(), lr=lr,
            momentum=float(config.get("momentum", 0.9)),
            weight_decay=float(config.get("weight_decay", 5e-4)),
        )
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="max", patience=2
    )
    return optimizer, scheduler
