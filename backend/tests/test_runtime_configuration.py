import pytest

from app.config import Settings, validate_runtime_configuration


def test_sqlite_development_configuration_is_allowed():
    validate_runtime_configuration(Settings(DATABASE_URL="sqlite:///./test.db"))


def test_postgres_rejects_development_placeholders():
    runtime = Settings(
        DATABASE_URL="postgresql://user:password@db/weight_bet",
        ALLOWED_ORIGINS="https://app.example.com",
        PAYMENT_PROVIDER="stripe",
    )
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        validate_runtime_configuration(runtime)


def test_postgres_accepts_complete_secure_configuration():
    runtime = Settings(
        DATABASE_URL="postgresql://user:password@db/weight_bet",
        SECRET_KEY="x" * 48,
        ALLOWED_ORIGINS="https://app.example.com",
        ALLOWED_HOSTS="api.example.com",
        GOOGLE_CLIENT_IDS="web-client.apps.googleusercontent.com",
        PAYMENT_PROVIDER="stripe",
        STRIPE_SECRET_KEY="sk_live_realistic",
        STRIPE_WEBHOOK_SECRET="whsec_live_realistic",
        STRIPE_CONNECT_RETURN_URL="https://app.example.com/payment/connect/complete",
        STRIPE_CONNECT_REFRESH_URL="https://app.example.com/payment/connect/retry",
        REDIS_URL="redis://redis.internal:6379/0",
    )
    validate_runtime_configuration(runtime)


def test_runtime_configuration_rejects_sqlite_in_production():
    runtime = Settings(
        DATABASE_URL="sqlite:///./production.db",
        ENVIRONMENT="production",
        SECRET_KEY="x" * 40,
        ALLOWED_ORIGINS="https://app.example.com",
        ALLOWED_HOSTS="api.example.com",
        GOOGLE_CLIENT_IDS="web-client.apps.googleusercontent.com",
    )
    with pytest.raises(RuntimeError, match="SQLite"):
        validate_runtime_configuration(runtime)


def test_production_rejects_demo_payment_provider():
    runtime = Settings(
        DATABASE_URL="postgresql://user:password@db/weight_bet",
        ENVIRONMENT="production",
        SECRET_KEY="x" * 40,
        ALLOWED_ORIGINS="https://app.example.com",
        ALLOWED_HOSTS="api.example.com",
        GOOGLE_CLIENT_IDS="web-client.apps.googleusercontent.com",
        PAYMENT_PROVIDER="demo",
    )
    with pytest.raises(RuntimeError, match="禁止使用演示支付"):
        validate_runtime_configuration(runtime)


def test_runtime_configuration_rejects_unknown_payment_provider():
    runtime = Settings(
        DATABASE_URL="postgresql://user:password@db/weight_bet",
        SECRET_KEY="x" * 40,
        ALLOWED_ORIGINS="https://app.example.com",
        ALLOWED_HOSTS="api.example.com",
        GOOGLE_CLIENT_IDS="web-client.apps.googleusercontent.com",
        PAYMENT_PROVIDER="unknown",
    )
    with pytest.raises(RuntimeError, match="只能配置为 demo 或 stripe"):
        validate_runtime_configuration(runtime)


def _secure_stripe_runtime(**overrides):
    values = dict(
        DATABASE_URL="postgresql://user:password@db/weight_bet",
        SECRET_KEY="x" * 48,
        ALLOWED_ORIGINS="https://app.example.com",
        ALLOWED_HOSTS="api.example.com",
        GOOGLE_CLIENT_IDS="web-client.apps.googleusercontent.com",
        PAYMENT_PROVIDER="stripe",
        STRIPE_SECRET_KEY="sk_live_realistic",
        STRIPE_WEBHOOK_SECRET="whsec_live_realistic",
        STRIPE_CONNECT_RETURN_URL="https://app.example.com/payment/connect/complete",
        STRIPE_CONNECT_REFRESH_URL="https://app.example.com/payment/connect/retry",
    )
    values.update(overrides)
    return Settings(**values)


def test_stripe_configuration_rejects_zero_decimal_currency():
    runtime = _secure_stripe_runtime(STRIPE_CURRENCY="jpy")
    with pytest.raises(RuntimeError, match="零小数"):
        validate_runtime_configuration(runtime)


def test_stripe_configuration_rejects_invalid_country_code():
    runtime = _secure_stripe_runtime(STRIPE_CONNECT_COUNTRY="cn")
    with pytest.raises(RuntimeError, match="国家代码"):
        validate_runtime_configuration(runtime)


def test_stripe_configuration_accepts_two_decimal_currency_and_country():
    validate_runtime_configuration(_secure_stripe_runtime(STRIPE_CURRENCY="cny", STRIPE_CONNECT_COUNTRY="US"))


def test_production_rejects_legacy_access_token_compatibility():
    runtime = _secure_stripe_runtime(ENVIRONMENT="production", ALLOW_LEGACY_ACCESS_TOKENS=True)
    with pytest.raises(RuntimeError, match="ALLOW_LEGACY_ACCESS_TOKENS"):
        validate_runtime_configuration(runtime)


def test_production_rejects_default_local_redis():
    runtime = _secure_stripe_runtime(REDIS_URL="redis://localhost:6379/0")
    runtime.ENVIRONMENT = "production"
    with pytest.raises(RuntimeError, match="Redis"):
        validate_runtime_configuration(runtime)
