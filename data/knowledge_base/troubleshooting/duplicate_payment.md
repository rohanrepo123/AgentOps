---
document_id: ts-duplicate-payment
category: troubleshooting
service: payment
document_type: troubleshooting
---

# Troubleshooting Duplicate Payments

## Symptoms

- customer reports two charges
- multiple successful payment attempts
- retry rate spike
- provider timeout immediately before retry

## Differential Diagnosis

### Hypothesis A: Payment retry
Look for timeout -> retry -> success sequence.

### Hypothesis B: Duplicate client request
Look for separate request IDs without an upstream timeout.

### Hypothesis C: Database duplication
Look for duplicate business records despite a single provider request.

### Evidence Priority

Provider/payment attempt history > application narrative.

## Conclusion Rule

Do not call the incident a payment retry problem unless logs or payment-attempt data demonstrate
that multiple charge attempts occurred.
