from app import create_app, celery, db
from celery.schedules import crontab
from app.models import User
from app.trading.main import execute_trade_logic

app = create_app()
app.app_context().push()

@celery.task
def execute_daily_trades():
    print("Executing daily trades...")
    users = User.query.filter_by(subscription_active=True, daily_trades_enabled=True).all()
    for user in users:
        result = execute_trade_logic(user)
        print(f"Trade execution for user {user.id}: {result}")

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=11, minute=10),
        execute_daily_trades.s(),
    )
