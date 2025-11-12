# Billing and Subscription API

**Version**: 2.0  
**Last Updated**: 2025-11-12  
**Status**: Production Ready

---

## Overview

The Billing and Subscription API provides comprehensive functionality for managing user subscriptions, processing payments, tracking usage, and handling billing operations. This API integrates with payment processors like Stripe and provides a complete billing solution for SaaS applications.

The Billing API is designed with **security**, **reliability**, and **compliance** as top priorities, ensuring that all financial transactions are handled safely and in accordance with industry standards.

---

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [Subscription Management](#subscription-management)
3. [Payment Processing](#payment-processing)
4. [Usage Tracking](#usage-tracking)
5. [Invoice Management](#invoice-management)
6. [Billing History](#billing-history)
7. [Webhooks](#webhooks)
8. [Error Handling](#error-handling)
9. [Security](#security)
10. [Examples](#examples)

---

## Core Concepts

### Subscription Tiers

Daur AI supports multiple subscription tiers with different features and pricing. Each tier provides specific capabilities and resource limits.

| Tier | Monthly Price | Features | Limits |
|------|---------------|----------|--------|
| **Free** | $0 | Basic automation, 100 operations/month | Limited support |
| **Basic** | $29 | Standard automation, 1,000 operations/month | Email support |
| **Pro** | $99 | Advanced automation, 10,000 operations/month | Priority support |
| **Enterprise** | Custom | Unlimited operations, custom features | Dedicated support |

### Billing Cycle

Subscriptions operate on a **monthly billing cycle** by default, with charges occurring on the same day each month. Annual billing is also available with discounted rates. The system automatically handles prorated charges for mid-cycle upgrades or downgrades.

### Payment Methods

The system supports multiple payment methods through Stripe integration, including credit cards, debit cards, and ACH transfers. Payment information is securely stored and tokenized to ensure PCI compliance.

---

## Subscription Management

### Class: BillingSystem

```python
from src.system.billing import BillingSystem, SubscriptionTier

class BillingSystem:
    """
    Manages subscriptions and billing operations.
    
    This class provides comprehensive billing functionality including
    subscription management, payment processing, and usage tracking.
    """
    
    def __init__(self, data_dir: Path):
        """
        Initialize billing system.
        
        Args:
            data_dir: Directory for storing billing data
        """
        pass
    
    def create_subscription(self, 
                          user_id: str, 
                          tier: SubscriptionTier,
                          payment_method: str = None) -> Dict[str, Any]:
        """
        Create a new subscription for a user.
        
        Args:
            user_id: User identifier
            tier: Subscription tier (FREE, BASIC, PRO, ENTERPRISE)
            payment_method: Payment method token (required for paid tiers)
            
        Returns:
            Dictionary containing subscription details
            
        Raises:
            ValueError: If payment method missing for paid tier
            BillingError: If subscription creation fails
        """
        pass
    
    def update_subscription(self,
                          user_id: str,
                          new_tier: SubscriptionTier) -> Dict[str, Any]:
        """
        Update user's subscription tier.
        
        Handles prorated charges/credits for mid-cycle changes.
        
        Args:
            user_id: User identifier
            new_tier: New subscription tier
            
        Returns:
            Updated subscription details
        """
        pass
    
    def cancel_subscription(self, 
                          user_id: str,
                          immediate: bool = False) -> bool:
        """
        Cancel a user's subscription.
        
        Args:
            user_id: User identifier
            immediate: If True, cancel immediately; otherwise at period end
            
        Returns:
            True if cancellation successful
        """
        pass
    
    def get_subscription(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's current subscription details.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary containing subscription information
        """
        pass
```

### Creating a Subscription

```python
from src.system.billing import BillingSystem, SubscriptionTier
from pathlib import Path

# Initialize billing system
billing = BillingSystem(Path("./data/billing"))

# Create free subscription
free_sub = billing.create_subscription(
    user_id="user_123",
    tier=SubscriptionTier.FREE
)
print(f"Free subscription created: {free_sub}")

# Create paid subscription
pro_sub = billing.create_subscription(
    user_id="user_456",
    tier=SubscriptionTier.PRO,
    payment_method="pm_1234567890"  # Stripe payment method token
)
print(f"Pro subscription created: {pro_sub}")
```

### Updating Subscriptions

```python
# Upgrade subscription
updated = billing.update_subscription(
    user_id="user_123",
    new_tier=SubscriptionTier.BASIC
)

print(f"Subscription upgraded to: {updated['tier']}")
print(f"Next billing date: {updated['next_billing_date']}")
print(f"Prorated charge: ${updated['prorated_charge']}")

# Downgrade subscription
downgraded = billing.update_subscription(
    user_id="user_456",
    new_tier=SubscriptionTier.BASIC
)

print(f"Subscription downgraded, credit applied: ${downgraded['credit_amount']}")
```

### Canceling Subscriptions

```python
# Cancel at period end (default)
billing.cancel_subscription(user_id="user_123")
print("Subscription will cancel at end of billing period")

# Immediate cancellation with refund
billing.cancel_subscription(user_id="user_456", immediate=True)
print("Subscription canceled immediately, prorated refund issued")
```

---

## Payment Processing

### Processing Payments

```python
from src.system.billing import PaymentStatus

# Process a payment
payment_result = billing.process_payment(
    user_id="user_123",
    amount=29.00,
    currency="USD",
    description="Monthly subscription - Basic tier"
)

if payment_result['status'] == PaymentStatus.COMPLETED:
    print(f"Payment successful: {payment_result['transaction_id']}")
else:
    print(f"Payment failed: {payment_result['error']}")
```

### Payment Methods

```python
# Add payment method
billing.add_payment_method(
    user_id="user_123",
    payment_method_token="pm_9876543210",
    is_default=True
)

# List payment methods
methods = billing.list_payment_methods(user_id="user_123")
for method in methods:
    print(f"Card ending in {method['last4']}, expires {method['exp_month']}/{method['exp_year']}")

# Remove payment method
billing.remove_payment_method(
    user_id="user_123",
    payment_method_id="pm_9876543210"
)
```

### Refunds

```python
# Process refund
refund = billing.process_refund(
    transaction_id="txn_abc123",
    amount=29.00,  # Full refund
    reason="Customer request"
)

if refund['status'] == PaymentStatus.REFUNDED:
    print(f"Refund processed: ${refund['amount']}")
```

---

## Usage Tracking

### Recording Usage

```python
# Record API usage
billing.record_usage(
    user_id="user_123",
    usage_type="api_calls",
    amount=150
)

# Record compute usage
billing.record_usage(
    user_id="user_123",
    usage_type="compute_minutes",
    amount=45.5
)

# Record storage usage
billing.record_usage(
    user_id="user_123",
    usage_type="storage_gb",
    amount=2.3
)
```

### Getting Usage Statistics

```python
# Get current month usage
usage = billing.get_usage(user_id="user_123")

print(f"API calls: {usage['api_calls']} / {usage['api_calls_limit']}")
print(f"Compute minutes: {usage['compute_minutes']}")
print(f"Storage: {usage['storage_gb']} GB")

# Check if over limit
if usage['api_calls'] > usage['api_calls_limit']:
    print("Warning: API call limit exceeded")
```

### Usage Alerts

```python
# Set usage alert
billing.set_usage_alert(
    user_id="user_123",
    usage_type="api_calls",
    threshold=800,  # Alert at 80% of limit
    callback=lambda: send_email_alert(user_id)
)
```

---

## Invoice Management

### Generating Invoices

```python
# Generate invoice for current period
invoice = billing.generate_invoice(user_id="user_123")

print(f"Invoice #{invoice['invoice_number']}")
print(f"Amount due: ${invoice['amount_due']}")
print(f"Due date: {invoice['due_date']}")

# Invoice line items
for item in invoice['line_items']:
    print(f"  {item['description']}: ${item['amount']}")
```

### Retrieving Invoices

```python
# Get specific invoice
invoice = billing.get_invoice(invoice_id="inv_abc123")

# List all invoices for user
invoices = billing.list_invoices(
    user_id="user_123",
    limit=10,
    status="paid"
)

for inv in invoices:
    print(f"Invoice {inv['invoice_number']}: ${inv['total']} - {inv['status']}")
```

### Invoice PDF

```python
# Generate invoice PDF
pdf_path = billing.generate_invoice_pdf(
    invoice_id="inv_abc123",
    output_path="/path/to/invoice.pdf"
)

print(f"Invoice PDF saved to: {pdf_path}")
```

---

## Billing History

### Transaction History

```python
# Get transaction history
transactions = billing.list_transactions(
    user_id="user_123",
    start_date="2025-01-01",
    end_date="2025-11-12",
    limit=50
)

for txn in transactions:
    print(f"{txn['date']}: {txn['description']} - ${txn['amount']} ({txn['status']})")
```

### Subscription History

```python
# Get subscription change history
history = billing.get_subscription_history(user_id="user_123")

for change in history:
    print(f"{change['date']}: {change['old_tier']} → {change['new_tier']}")
```

### Export Data

```python
# Export billing data to CSV
billing.export_billing_data(
    user_id="user_123",
    format="csv",
    output_path="/path/to/billing_data.csv",
    start_date="2025-01-01",
    end_date="2025-12-31"
)
```

---

## Webhooks

### Stripe Webhook Handling

```python
from src.system.billing import BillingWebhookHandler

# Initialize webhook handler
webhook_handler = BillingWebhookHandler(
    stripe_webhook_secret="whsec_..."
)

# Handle webhook event
@app.route('/webhooks/stripe', methods=['POST'])
def handle_stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = webhook_handler.verify_and_parse(payload, sig_header)
        
        # Handle different event types
        if event['type'] == 'payment_intent.succeeded':
            handle_successful_payment(event['data'])
        elif event['type'] == 'payment_intent.failed':
            handle_failed_payment(event['data'])
        elif event['type'] == 'customer.subscription.updated':
            handle_subscription_update(event['data'])
        
        return {'status': 'success'}, 200
    except Exception as e:
        return {'error': str(e)}, 400
```

### Webhook Event Types

| Event Type | Description | Action |
|------------|-------------|--------|
| `payment_intent.succeeded` | Payment completed successfully | Update subscription status |
| `payment_intent.failed` | Payment failed | Notify user, retry payment |
| `customer.subscription.updated` | Subscription changed | Update user tier |
| `customer.subscription.deleted` | Subscription canceled | Downgrade to free tier |
| `invoice.payment_succeeded` | Invoice paid | Mark invoice as paid |
| `invoice.payment_failed` | Invoice payment failed | Send payment reminder |

---

## Error Handling

### Billing Exceptions

```python
from src.system.billing import (
    BillingError,
    PaymentError,
    SubscriptionError,
    InsufficientFundsError
)

try:
    billing.process_payment(user_id="user_123", amount=99.00)
except InsufficientFundsError:
    print("Payment failed: Insufficient funds")
    # Notify user to update payment method
except PaymentError as e:
    print(f"Payment error: {e}")
    # Log error and retry
except BillingError as e:
    print(f"Billing system error: {e}")
    # Alert admin
```

### Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def process_payment_with_retry(user_id, amount):
    return billing.process_payment(user_id, amount)

# Automatically retries up to 3 times with exponential backoff
result = process_payment_with_retry("user_123", 29.00)
```

---

## Security

### PCI Compliance

The billing system never stores raw credit card numbers. All payment information is tokenized through Stripe, ensuring PCI DSS compliance. Only payment method tokens are stored in the database.

```python
# NEVER do this
payment_data = {
    "card_number": "4242424242424242",  # ❌ NEVER store raw card numbers
    "cvv": "123"  # ❌ NEVER store CVV
}

# DO this instead
payment_method_token = stripe.create_payment_method(...)  # ✅ Use Stripe tokenization
billing.add_payment_method(user_id, payment_method_token)  # ✅ Store only token
```

### Data Encryption

All sensitive billing data is encrypted at rest using AES-256 encryption. Transaction logs are encrypted and access is restricted to authorized personnel only.

```python
# Encryption is handled automatically
billing.store_transaction(transaction_data)  # Automatically encrypted
```

### Audit Logging

All billing operations are logged for audit purposes, including user ID, timestamp, action, and result.

```python
# Audit logs are created automatically
billing.process_payment(...)  # Logged: user_id, amount, timestamp, result

# Retrieve audit logs
logs = billing.get_audit_logs(
    user_id="user_123",
    start_date="2025-11-01",
    end_date="2025-11-12"
)
```

---

## Examples

### Complete Subscription Workflow

```python
from src.system.billing import BillingSystem, SubscriptionTier
from pathlib import Path

# Initialize
billing = BillingSystem(Path("./data/billing"))

# 1. User signs up with free tier
subscription = billing.create_subscription(
    user_id="new_user_001",
    tier=SubscriptionTier.FREE
)
print(f"Welcome! Free tier subscription created.")

# 2. User adds payment method
billing.add_payment_method(
    user_id="new_user_001",
    payment_method_token="pm_test_123",
    is_default=True
)

# 3. User upgrades to Pro
upgraded = billing.update_subscription(
    user_id="new_user_001",
    new_tier=SubscriptionTier.PRO
)
print(f"Upgraded to Pro tier. Next billing: {upgraded['next_billing_date']}")

# 4. Track usage
billing.record_usage(user_id="new_user_001", usage_type="api_calls", amount=500)

# 5. Generate invoice at end of month
invoice = billing.generate_invoice(user_id="new_user_001")
print(f"Invoice generated: ${invoice['amount_due']}")

# 6. Process payment
payment = billing.process_payment(
    user_id="new_user_001",
    amount=invoice['amount_due'],
    description=f"Invoice #{invoice['invoice_number']}"
)

if payment['status'] == 'completed':
    print("Payment successful!")
```

### Usage-Based Billing

```python
# Track detailed usage
billing.record_usage(user_id="user_123", usage_type="api_calls", amount=1500)
billing.record_usage(user_id="user_123", usage_type="compute_hours", amount=12.5)
billing.record_usage(user_id="user_123", usage_type="storage_gb", amount=5.2)

# Calculate overage charges
usage = billing.get_usage(user_id="user_123")

overage_cost = 0
if usage['api_calls'] > usage['api_calls_limit']:
    overage = usage['api_calls'] - usage['api_calls_limit']
    overage_cost += overage * 0.01  # $0.01 per extra call

# Add overage to next invoice
if overage_cost > 0:
    billing.add_invoice_item(
        user_id="user_123",
        description="API call overage",
        amount=overage_cost
    )
```

---

## See Also

- [User Management API](./user-api.md) - User account management
- [Security API](./security-api.md) - Authentication and authorization
- [System API](./system-api.md) - System integration

---

**Last Updated**: 2025-11-12  
**Version**: 2.0  
**Author**: Manus AI

