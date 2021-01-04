Bare minimal setup

```bash
pip install -r requirements.txt
export APP_CFG=`pwd`/config.cfg'
export PYTHONPATH=`pwd`


```

Cfg file

```ini
[test]
db_uri = mysql+pymysql://money:money123@localhost/money

[prod]
db_uri = mysql+pymysql://money:money123@localhost/money
```
