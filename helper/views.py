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

    @gs_task(task_id)
    def handle_request(self, request) : 
        input  = self.pre_process(request.data, request.headers)
        output = self.process(input)
        return self.post_process(output)

    def post(self,request):
        response  = self.handle_request(request)
        if not response.get("success",True): 
            return JsonResponse(response, status = 400)
        else : 
            return JsonResponse(response)

class FetchView(ProcessView):
    model = None
    serializer = None
