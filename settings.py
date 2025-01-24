filename = 'proton_accounts.csv'

# Please wait a few minutes before sending email alert (in register_with_temporary_email method)
time_to_slee_if_exception_in_alert_occurred = 10  # seconds

# protonmail domain
protonmail_domain = '@proton.me'

# If you want to open this file in ms excel, leave ';'
csv_delimiter =';'

# How many accounts can app create by 1 session
max_accounts_count = 5

websocket_port = 8080
websocket_uri = f"ws://localhost:{websocket_port}"

protonmail_registration_address = "https://account.proton.me/signup?plan=free&billing=24&currency=EUR&language=en"
