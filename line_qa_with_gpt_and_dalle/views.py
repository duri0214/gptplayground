import json

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView

from line_qa_with_gpt_and_dalle.forms import UserTextForm
from line_qa_with_gpt_and_dalle.models import ChatLogsWithLine


class HomeView(FormView):
    template_name = "line_qa_with_gpt_and_dalle/home.html"
    form_class = UserTextForm
    success_url = reverse_lazy("line_qa_with_gpt:home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        login_user = User.objects.get(pk=1)  # TODO: request.user.id
        context["chat_logs"] = ChatLogsWithLine.objects.filter(
            user=login_user
        ).order_by("thread", "created_at")

        return context

    def form_valid(self, form):
        form_data = form.cleaned_data
        login_user = User.objects.get(pk=1)  # TODO: request.user.id

        chat_history = []  # TODO: 過去ログを含めるかどうかは要判断
        formatted_answer = 'result["answer"]'
        # ChatLogs.objects.create(
        #     user=login_user, thread="XXX", role="user", message=form_data["question"]
        # )
        # ChatLogs.objects.create(
        #     user=login_user, thread="XXX", role="assistant", message=formatted_answer
        # )

        return super().form_valid(form)


@csrf_exempt
class LineWebHookView(TemplateView):
    @staticmethod
    def post(request, *args, **kwargs):
        """ラインの友達追加時に呼び出され、ラインのIDを登録する"""
        request_json = json.loads(request.body.decode("utf-8"))
        events = request_json["events"]

        # If you run the validation from the `LINE DEVELOPERS` screen, `events` will be returned as `[]`
        if events:
            line_user_id = events[0]["source"]["userId"]

            # webhook connection check at fixed id 'dead...beef'
            if line_user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
                # follow | unblock
                if events[0]["type"] == "follow":
                    print("ここにきたらdbに追加")
                    # LinePush.objects.create(line_user_id)
                # block
                if events[0]["type"] == "unfollow":
                    print("ここにきたらdbから削除")
                    # LinePush.objects.filter(line_user_id).delete()

        return HttpResponse("`callback` returned 200", status=200)
