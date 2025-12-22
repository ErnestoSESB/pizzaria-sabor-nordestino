import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

cursor.execute('SELECT id, nome, especial FROM pizzaria_pizza WHERE nome = "Nordestina"')
pizza = cursor.fetchone()

if pizza:
    print(f'✅ Pizza encontrada:')
    print(f'   ID: {pizza[0]}')
    print(f'   Nome: {pizza[1]}')
    print(f'   Especial: {pizza[2]} {"(SIM)" if pizza[2] == 1 else "(NÃO)"}')
else:
    print('❌ Pizza Nordestina não encontrada!')

# Verificar todas as especiais
print('\n📋 Todas as pizzas especiais no banco:')
cursor.execute('SELECT id, nome FROM pizzaria_pizza WHERE especial = 1')
for row in cursor.fetchall():
    print(f'   ⭐ ID {row[0]}: {row[1]}')

conn.close()
