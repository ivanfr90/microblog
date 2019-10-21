from app import create_app, db, cli
from app.core.models import Post, Notification
from app.messages.models import Message
from app.tasks.models import Task
from app.utils import get_user_model

app = create_app()
cli.register(app)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': get_user_model(), 'Post': Post, 'Message': Message, 'Notification': Notification, 'Task': Task}
