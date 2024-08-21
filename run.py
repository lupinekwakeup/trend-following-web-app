from app import create_app, db
from app.models import User, Trade
import click

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Trade': Trade}

@app.cli.command("update-subscription")
@click.argument("username")
@click.argument("status", type=bool)
def update_subscription(username, status):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user:
            user.subscription_active = status
            db.session.commit()
            click.echo(f"Subscription for {username} set to {status}")
        else:
            click.echo(f"User {username} not found")

@app.cli.command("list-users")
def list_users():
    with app.app_context():
        users = User.query.all()
        for user in users:
            api_credentials_set = user.encrypted_api_key is not None and user.encrypted_api_secret is not None
            click.echo(f"Username: {user.username}")
            click.echo(f"Email: {user.email}")
            click.echo(f"Subscription Active: {user.subscription_active}")
            click.echo(f"Daily Trades Enabled: {user.daily_trades_enabled}")
            click.echo(f"API Credentials Set: {api_credentials_set}")
            click.echo("---")

if __name__ == '__main__':
    app.run(host='128.199.183.216', port=5000, debug=True)