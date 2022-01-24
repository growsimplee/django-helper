from rest_framework.views import APIView
from django.http import JsonResponse
from helper.decorators import gs_task

class ProcessView(APIView):
    task_id = None

    def pre_process(self,data,headers):
        return data.update(headers)
    
    def process(self,data):
        return data

    def post_process(self,data):
        return data

    def handle_request(self, data, headers) : 
        input  = self.pre_process(data, headers)
        output = self.process(input)
        return self.post_process(output)

    def post(self,request):
        gs_func = gs_task(self.task_id)(self.handle_request)
        response  = gs_func(request.data, request.headers)
        if not response.get("success",True): 
            return JsonResponse(response, status = 400)
        else : 
            return JsonResponse(response)

class FetchView(ProcessView):
    model = None
    serializer = None
