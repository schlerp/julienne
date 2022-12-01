from celery import Celery

# app = Celery("julienne.tasks", broker="pyamqp://admin:mypass@rabbit//")
app = Celery("julienne.tasks", broker="redis://redis:6379/0")

app.config_from_object("julienne.celeryconfig")
app.setup_security()

from . import tasks
