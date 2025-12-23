import click


@click.group()
@click.option("-l", "--loglevel", default="info", help="Logging level (default: info)")
def queue(loglevel: str, scheduler_name: str | None = None) -> None:
    pass


@queue.command(name="list")
@click.option("-l", "--loglevel", default="info", help="Logging level (default: info)")
def list_(loglevel: str, scheduler_name: str | None = None) -> None:
    from bitcaster.runner.manager import BackgroundManager

    manager = BackgroundManager()
    click.secho("Runners", fg="green")
    for runner_name, info in manager.get_runners().items():
        click.secho(f"  - {runner_name} - {info['last_seen']}", fg="yellow")
        for task in info["tasks"]:
            click.secho(f"     - {task['name']} - {task}")

    click.secho("Queued tasks", fg="green")
    for queue, size in manager.get_queue_sizes().items():
        click.secho(f" - {queue:<20} : {size: 5}", fg="yellow")


@queue.command(name="reset")
@click.option("-l", "--loglevel", default="info", help="Logging level (default: info)")
def reset(loglevel: str, scheduler_name: str | None = None) -> None:
    from bitcaster.runner.manager import BackgroundManager

    manager = BackgroundManager()

    manager.reset()
