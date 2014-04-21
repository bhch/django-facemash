## django-facemash

### A Facemash-like app as seen in the movie The Social Network.

#### Check out the DEMO **[here](http://facemash.pythonanywhere.com)**.

**Please note that this doesn't include `tests`.**

## How to install

Install it like any other Django app.

1. Extract `facemash` folder from `django-facemash` directory and keep it inside your project's directory.
2. In your project's `settings.py` file, add `facemash` to `INSTALLED_APPS`.
3. Run `python manage.py syncdb`.
4. In your project's `urls.py` file, add `url(r'^facemash/', include('facemash.urls')),`.
