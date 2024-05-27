import stripe
from config.environ import settings




stripe.api_key = settings.stripe_secret_key