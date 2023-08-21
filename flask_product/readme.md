Запуск:
1.python -m venv venv
2.venv\scripts\activate.bat
3.pip install -r reqirements.txt
4.запустить mysql и изменить данные в app.py
5.запустить редис и изменить данные в app.py
6.flask run --reload
7.запустить в другой консоли Celery: celery -A app.client worker --loglevel=info




Використовувати стек:
- Flask
- Flask-Admin
- Flask-Security
- SQLAlchemy
- Celery
- Redis
- MySQL/MariaDB
- Docker


З використанням вказаного стеку реалізувати наступний функціонал:
 - створити каталог товарів з характеристиками: колір, вага, ціна.
 - окремо створити адреси доставки з фільтрами по країні, місту, вулиці. Буде плюсом реалізувати адреси у вигляді зв'язного списку.
 - створити перелік замовлень товарів з адресами, кількістю товарів, та статусами замовлень (виконано, відмнено, обробляється). 
 - реалізувати можливість додавання, видалення та модифікації вказаних об'єктів в БД MySQL/MariaDB.
 - за допомогою Celery відслідковувати статус замовлення та при зміні статусу записати подію в файл у вигляді: «Замовлення %NUM% змінило статус на %STATE%». У якості брокера для Celery використати Redis.
 - створити ендпойнт для отримання інформації по статусу замовлення за номером замовлення. Використовувати базову автризацію та JSON-RPC. Протокол взаємодії описати в README.md.
 - реалізувати авторизацію в адміністративний інтерфейс
 - запуск усіх компонентів організувати за допомогою  docker-compose  зі збереженняб данних у БД після зупинки контейнера.
 - код завдання викласти в відкритий git репозиторій
 - прикріпити дамп БД (.sql) з тестовими даними.


Выполненая работа:
1.- створити каталог товарів з характеристиками: колір, вага, ціна. 
@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)
используеться шаблон index.html, создавать товар можно через админ панель, решил не добавлять обычное создание, что-б создать нужно перейти по урл /admin вкладка Product

2.- окремо створити адреси доставки з фільтрами по країні, місту, вулиці. Буде плюсом реалізувати адреси у вигляді зв'язного списку. 
@app.route('/addresses')
def addresses():
    addresses = Address.query.all()
    return render_template('addresses.html', addresses=addresses)
    используеться шаблон addresses.html, создавать данные можно через админ панель, решил не добавлять обычное создание, что-б создать нужно перейти по урл /admin вкладка Address


3.- створити перелік замовлень товарів з адресами, кількістю товарів, та статусами замовлень (виконано, відмнено, обробляється). 
class OrderAdmin(ModelView):
    column_list = ['customer_name', 'address', 'status']

    form_choices = {
        'status': [
            ('Обробляється', 'Обробляється'),
            ('Виконано', 'Виконано'),
            ('Відмінено', 'Відмінено')
        ]
    }

получение полен и статуса 
Создание ордера через метот post возможно перейти из главной страницы http://127.0.0.1:5000/ создана специальная ссылка 
@app.route('/create_order', methods=['POST'])
def create_order():
    customer_name = request.form.get('customer_name')
    address_id = request.form.get('address_id')
    status = 'Обробляється'
    order = Order(customer_name=customer_name, address_id=address_id, status=status)
    db.session.add(order)
    db.session.commit()
    return redirect('/orders')

4.реалізувати можливість додавання, видалення та модифікації вказаних об'єктів в БД MySQL/MariaDB. Реализовано через админ панель

5.- за допомогою Celery відслідковувати статус замовлення та при зміні статусу записати подію в файл у вигляді: «Замовлення %NUM% змінило статус на %STATE%». У якості брокера для Celery використати Redis.
Подключение к redis и celery 
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
app.config['CELERY_BROKER_URL'] = 'redis://127.0.0.1:6379/'
client = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
client.conf.update(app.config)

@client.task
def track_order_status(order_id, new_status):
    event = f"Замовлення {order_id} змінило статус на {new_status}"
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'E:\Technical Task Ilya Flask\flask_product\order_events.txt')
    with open(file_path, 'a', encoding="utf-8") as file:
        file.write(event + '\n')
    return event
обновление id и статуса заказа, через сelery и записано в файл order_events.txt

6.створити ендпойнт для отримання інформації по статусу замовлення за номером замовлення.
@app.route('/get_order_status/<int:order_id>', methods=['GET'])
def get_order_status_endpoint(order_id):
    response = get_order_status(order_id)
    return jsonify(response)

7.Використовувати базову автризацію та JSON-RPC.
Не реализовано, с не удачиным поиском информации

8.реалізувати авторизацію в адміністративний інтерфейс
Не реализовано, с не удачиным поиском информации

9.- запуск усіх компонентів організувати за допомогою  docker-compose  зі збереженняб данних у БД після зупинки контейнера.
Из за проблем с компьютером, реализовать не смог, но набросал docker-compose.yaml и Dockerfile в их ввиде , не смогу запустить у себя на компьютере 

10. - код завдання викласти в відкритий git репозиторій
   
    
