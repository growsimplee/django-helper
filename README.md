# Django Helper Package

## Motivation 
This package is designed for DRY by standardizing common practices required for django microservices powered by AWS.

## Django Settings Variables
EB_AWS_REGION
EB_ACCESS_KEY_ID
EB_SECRET_ACCESS_KEY
ERROR_QUEUE - central error queue for data pipeline
ERROR_CODES - Mapping error class with error codes 
SERVICE_NAME - name of microservice

## Features Handled
### Error Handling 
A helpful decorator that handles error. 
```
from helper.decorators import gs_tasks

@gs_task("divider"):
def divide(n,d=1):
    return n/d

divide(1,0)
```
The above piece of code will generate a message which is sent to ERROR_QUEUE with a task_id and microservice name as well as exception and traceback.

### Process API View
Standardized abstract process view for any use case - handles pre, during and post-process

### Model Fetch View
Write fast DB fetching with error handling, search, filter, pagination 

### Standard database controller
With all features for search, filter, aggregation, bulk create, bulk update or create

### Simple In Memory Cache 
Easily implementable cache with decorators. 

## Examples

### Implement simple caching
```
from helpers.decorators import simple_gs_cache
@simple_gs_cache(128)
def fib(n):
    print("actually running )
    if n in [0,1]:
        return n
    else :
        return fib(n-1) + fib(n-2)

fib(5) ## will actually compute
fib(4) ## wont be computed
```

### Quickly write a search and filter view with pagination for a model
```
from helper.dbctl import BaseDbctl as dbctl 
from helper.views import FetchView

class StockDbctl(dbctl):
        model = Stock
        search_fields = ["product__sku_id", "product__name", "product__category", "warehouse__warehouse_id", "warehouse__warehouse_name"]

class StockPageView(FetchView):
    task_id = "stock_fetch"
    dbctl = StockDbctl()
    serializer = StockSerializer

    def pre_process(self,data,headers):
        data["filters"] = data.get("filters", {})
        data["filters"]["product__user_id"] = headers["orgId"]
        return data

```

