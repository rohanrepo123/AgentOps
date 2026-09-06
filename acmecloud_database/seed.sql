
INSERT INTO services VALUES
('svc-payment', 'Payment Service', 'Handles payment authorization, charge creation, refunds, and payment retries.', 'Payments Team', 'healthy', 'v2.8.1'),
('svc-subscription', 'Subscription Service', 'Manages subscription creation, upgrades, downgrades, and billing plans.', 'Billing Team', 'healthy', 'v3.4.0'),
('svc-auth', 'Authentication Service', 'Handles login, token issuance, session validation, and password reset.', 'Identity Team', 'healthy', 'v4.1.2'),
('svc-api', 'API Gateway', 'Routes external API requests and enforces authentication and rate limits.', 'Platform Team', 'healthy', 'v5.2.0'),
('svc-notification', 'Notification Service', 'Sends email, SMS, and in-app notifications.', 'Messaging Team', 'healthy', 'v2.3.5'),
('svc-worker', 'Background Worker', 'Processes asynchronous jobs such as invoices, emails, and reconciliation.', 'Platform Team', 'healthy', 'v1.9.7');

INSERT INTO users VALUES
('usr-001', 'alice@example.com', 'pro', 'US', '2026-01-10T10:00:00'),
('usr-002', 'bob@example.com', 'enterprise', 'US', '2025-11-04T08:30:00'),
('usr-003', 'charlie@example.com', 'pro', 'IN', '2026-02-17T14:20:00'),
('usr-004', 'diana@example.com', 'free', 'GB', '2026-03-02T09:15:00'),
('usr-005', 'eve@example.com', 'enterprise', 'DE', '2025-09-21T16:40:00'),
('usr-006', 'frank@example.com', 'pro', 'CA', '2026-04-11T12:10:00');

INSERT INTO subscriptions VALUES
('sub-001', 'usr-001', 'pro', 'active', 49.00, '2026-01-10T10:00:00'),
('sub-002', 'usr-002', 'enterprise', 'active', 299.00, '2025-11-04T08:30:00'),
('sub-003', 'usr-003', 'pro', 'active', 49.00, '2026-02-17T14:20:00'),
('sub-004', 'usr-004', 'free', 'active', 0.00, '2026-03-02T09:15:00'),
('sub-005', 'usr-005', 'enterprise', 'active', 299.00, '2025-09-21T16:40:00'),
('sub-006', 'usr-006', 'pro', 'active', 49.00, '2026-04-11T12:10:00');

INSERT INTO payments VALUES
('pay-001', 'usr-001', 'sub-001', 'txn-1001', 49.00, 'USD', 'SUCCESS', 'idem-1001', '2026-08-28T10:31:07'),
('pay-002', 'usr-002', 'sub-002', 'txn-1002', 299.00, 'USD', 'SUCCESS', 'idem-1002', '2026-08-28T11:12:22'),
('pay-003', 'usr-003', 'sub-003', 'txn-1003', 49.00, 'USD', 'SUCCESS', NULL, '2026-08-29T09:42:11'),
('pay-004', 'usr-004', 'sub-004', 'txn-1004', 0.00, 'USD', 'SUCCESS', NULL, '2026-08-29T12:02:31'),
('pay-005', 'usr-005', 'sub-005', 'txn-1005', 299.00, 'USD', 'SUCCESS', 'idem-1005', '2026-08-30T15:20:05'),
('pay-006', 'usr-006', 'sub-006', 'txn-1006', 49.00, 'USD', 'SUCCESS', NULL, '2026-08-31T18:45:12'),
('pay-007', 'usr-001', 'sub-001', 'txn-1007', 49.00, 'USD', 'SUCCESS', NULL, '2026-09-01T10:31:07'),
('pay-008', 'usr-003', 'sub-003', 'txn-1008', 49.00, 'USD', 'SUCCESS', NULL, '2026-09-01T13:22:45');

INSERT INTO payment_attempts VALUES
('att-001', 'pay-001', 1, 'req-7001', 'SUCCESS', 420, '2026-08-28T10:31:07'),
('att-002', 'pay-002', 1, 'req-7002', 'SUCCESS', 380, '2026-08-28T11:12:22'),
('att-003', 'pay-003', 1, 'req-7003', 'SUCCESS', 410, '2026-08-29T09:42:11'),
('att-004', 'pay-005', 1, 'req-7005', 'SUCCESS', 395, '2026-08-30T15:20:05'),
('att-005', 'pay-006', 1, 'req-7006', 'SUCCESS', 430, '2026-08-31T18:45:12'),
('att-006', 'pay-007', 1, 'req-7007', 'TIMEOUT', 3000, '2026-09-01T10:31:02'),
('att-007', 'pay-007', 2, 'req-7007-retry1', 'SUCCESS', 620, '2026-09-01T10:31:07'),
('att-008', 'pay-007', 3, 'req-7007-retry2', 'SUCCESS', 610, '2026-09-01T10:31:08'),
('att-009', 'pay-008', 1, 'req-7008', 'SUCCESS', 450, '2026-09-01T13:22:45');

INSERT INTO incidents VALUES
('INC-001', 'Duplicate charges after subscription upgrade', 'Several customers were charged twice after upgrading their subscriptions.', 'HIGH', 'svc-payment', 'Non-idempotent payment retry executed after an upstream timeout.', 'Disable automatic charge retries without idempotency keys and introduce provider-side idempotency.', '2026-09-01T11:00:00'),
('INC-002', 'Elevated API latency', 'API requests experienced unusually high response times.', 'MEDIUM', 'svc-api', 'A slow downstream dependency caused request threads to remain occupied.', 'Introduce timeout limits and parallelize independent downstream calls.', '2026-08-25T16:30:00'),
('INC-003', 'Authentication failures', 'A subset of users could not log in.', 'HIGH', 'svc-auth', 'Expired signing-key cache caused validation failures after key rotation.', 'Refresh signing keys automatically and invalidate stale cache entries.', '2026-08-19T09:20:00'),
('INC-004', 'Delayed email notifications', 'Password-reset and invoice emails were delayed.', 'MEDIUM', 'svc-notification', 'Background worker queue became saturated during a traffic spike.', 'Increase worker concurrency and configure queue backpressure.', '2026-08-14T13:10:00'),
('INC-005', 'Failed subscription upgrades', 'Some subscription upgrades remained pending.', 'HIGH', 'svc-subscription', 'Payment confirmation webhook processing failed intermittently.', 'Add webhook retry handling and make subscription state updates idempotent.', '2026-08-08T17:45:00');
