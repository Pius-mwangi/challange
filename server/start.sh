pip install uwsgi
uwsgi --http :5000 --wsgi-file app.py --callable app
