# Check if the current project has a superuser

To check if you already have a superuser in your Django project, you can:

Open a Django shell:

```python
python3 manage.py shell
```
Run the following code:
```python
from django.contrib.auth import get_user_model
User = get_user_model()
print(User.objects.filter(is_superuser=True).exists())
```

If it prints True, a superuser exists.
If it prints False, you have not created a superuser yet.