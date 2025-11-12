import pytest
from pathlib import Path
import json
from datetime import datetime, timedelta
from src.system.billing import BillingSystem, SubscriptionTier, PaymentStatus

@pytest.fixture
def test_data_dir(tmp_path):
    return tmp_path / "test_data"

@pytest.fixture
def billing_system(test_data_dir):
    return BillingSystem(test_data_dir)

def test_create_user(billing_system):
    """Тест создания пользователя в системе биллинга."""
    user = billing_system.create_user(
        user_id="test_user",
        email="test@example.com"
    )
    
    assert user["user_id"] == "test_user"
    assert user["email"] == "test@example.com"
    assert user["subscription"]["tier"] == SubscriptionTier.FREE.value
    assert user["usage"]["requests_today"] == 0
    
def test_update_subscription(billing_system):
    """Тест обновления подписки."""
    billing_system.create_user(
        user_id="sub_test",
        email="sub@example.com"
    )
    
    success = billing_system.update_subscription(
        user_id="sub_test",
        tier=SubscriptionTier.PRO,
        months=3
    )
    
    assert success is True
    
    user = billing_system.get_user("sub_test")
    assert user["subscription"]["tier"] == SubscriptionTier.PRO.value
    assert user["subscription"]["status"] == "active"
    
def test_record_usage(billing_system):
    """Тест записи использования ресурсов."""
    billing_system.create_user(
        user_id="usage_test",
        email="usage@example.com",
        tier=SubscriptionTier.BASIC
    )
    
    # Проверяем успешную запись в пределах лимита
    assert billing_system.record_usage(
        user_id="usage_test",
        requests=50,
        storage=100
    ) is True
    
    # Проверяем превышение лимита
    assert billing_system.record_usage(
        user_id="usage_test",
        requests=2000,  # Превышает лимит BASIC плана
        storage=0
    ) is False
    
def test_process_payment(billing_system):
    """Тест обработки платежа."""
    payment = billing_system.process_payment(
        user_id="payment_test",
        amount=29.99,
        payment_method={
            "type": "card",
            "number": "4242424242424242",
            "exp_month": 12,
            "exp_year": 2025
        }
    )
    
    assert payment["status"] == PaymentStatus.PENDING.value
    assert payment["amount"] == 29.99
    assert payment["user_id"] == "payment_test"
    
def test_list_transactions(billing_system):
    """Тест получения списка транзакций."""
    # Создаем несколько транзакций
    for i in range(3):
        billing_system.process_payment(
            user_id="trans_test",
            amount=9.99 * (i + 1),
            payment_method={"type": "card"}
        )
    
    # Получаем все транзакции
    transactions = billing_system.list_transactions("trans_test")
    assert len(transactions) == 3
    
    # Получаем транзакции за определенный период
    start_date = datetime.now() - timedelta(days=1)
    end_date = datetime.now() + timedelta(days=1)
    
    filtered_transactions = billing_system.list_transactions(
        "trans_test",
        start_date=start_date,
        end_date=end_date
    )
    assert len(filtered_transactions) == 3
    
def test_get_transaction(billing_system):
    """Тест получения данных транзакции."""
    # Создаем транзакцию
    payment = billing_system.process_payment(
        user_id="get_trans_test",
        amount=19.99,
        payment_method={"type": "paypal"}
    )
    
    # Получаем данные транзакции
    transaction = billing_system.get_transaction(payment["transaction_id"])
    
    assert transaction is not None
    assert transaction["amount"] == 19.99
    assert transaction["user_id"] == "get_trans_test"
    assert transaction["payment_method"]["type"] == "paypal"