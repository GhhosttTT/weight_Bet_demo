import sqlite3

conn = sqlite3.connect('weight_loss_betting.db')
cursor = conn.cursor()

user_id = 'e5aa0467-f2ad-4813-8137-f7a074e68faf'

# Check balance
cursor.execute('SELECT available_balance, frozen_balance FROM balances WHERE user_id = ?', (user_id,))
result = cursor.fetchone()
if result:
    print(f'User {user_id}:')
    print(f'  Available Balance: {result[0]}')
    print(f'  Frozen Balance: {result[1]}')
else:
    print(f'No balance record found for user {user_id}')

# Check recent transactions
cursor.execute('SELECT type, amount, status, created_at FROM transactions WHERE user_id = ? ORDER BY created_at DESC LIMIT 5', (user_id,))
transactions = cursor.fetchall()
print(f'\nRecent transactions:')
for tx in transactions:
    print(f'  {tx[0]}: {tx[1]} ({tx[2]}) at {tx[3]}')

conn.close()
