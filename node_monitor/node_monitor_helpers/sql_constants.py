### SQL queries for table `subscribers`
INSERT_SUBSCRIBER = """
    INSERT INTO subscribers (
        node_provider_id,
        notify_on_status_change,
        notify_email,
        notify_slack,
        node_provider_name,
        notify_telegram
    ) VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (node_provider_id) DO UPDATE SET
        notify_on_status_change = EXCLUDED.notify_on_status_change,
        notify_email = EXCLUDED.notify_email,
        notify_slack = EXCLUDED.notify_slack,
        node_provider_name = EXCLUDED.node_provider_name,
        notify_telegram = EXCLUDED.notify_telegram
"""

DELETE_SUBSCRIBER = """
    DELETE FROM subscribers
    WHERE node_provider_id = %s
"""