from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.http import JsonResponse
from helper.decorators import gs_task

class ProcessView(APIView):
    task_id = None

    def pre_process(self, data, headers):
        return data

    def process(self, data):
        return data

    def post_process(self, data):
        return data

    def handle_request(self, data, headers):
        input = self.pre_process(data, headers)
        output = self.process(input)
        return self.post_process(output)

    def post(self, request):
        gs_func = gs_task(self.task_id)(self.handle_request)
        response = gs_func(request.data, request.headers)
        if not response.get("success", True):
            return JsonResponse(response, status=400)
        else:
            return JsonResponse(response)

class ProcessUserView(ProcessView):
    def handle_request(self, data, headers):
        user_id = headers.get("orgId", None)
        if user_id is None:
            return {"status": False, "message": "orgId is Invalid."}
        input = self.pre_process(data, headers)
        output = self.process(input)
        return self.post_process(output)


class RequestImpersonator:
    def __init__(self, query_params):
        self.query_params = query_params

class FetchView(ProcessUserView):
    dbctl = None
    serializer = None
    page_size = 5
    page_size_query_param = 'ps'
    max_page_size = 10000

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            class StandardPagesPagination(PageNumberPagination):
                page_size = self.page_size
                page_size_query_param = self.page_size_query_param
                max_page_size = self.max_page_size
            self._paginator = StandardPagesPagination()
        return self._paginator

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def process(self, data):
        pagination = data.pop("pagination", False)
        queryset = self.dbctl.fetch(**data).order_by()
        response = {"sucess": True}
        if pagination:
            page = self.paginate_queryset(queryset)
            num_pages = self.paginator.page.paginator.num_pages
            response["results"] = self.serializer(page, many=True).data
            response["pages"] = num_pages
        else:
            response = {"results": self.serializer(queryset, many=True).data}
        return response


