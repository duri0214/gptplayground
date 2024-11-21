import json

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView
from dotenv import load_dotenv

from line_qa_with_gpt_and_dalle.domain.usecase.llm_service_use_cases import (
    GeminiUseCase,
    OpenAIGptUseCase,
    OpenAIDalleUseCase,
    OpenAITextToSpeechUseCase,
    OpenAISpeechToTextUseCase,
    UseCase,
)
from line_qa_with_gpt_and_dalle.forms import UserTextForm
from line_qa_with_gpt_and_dalle.models import ChatLogsWithLine

# .env ファイルを読み込む
load_dotenv()


class HomeView(FormView):
    template_name = "line_qa_with_gpt_and_dalle/home.html"
    form_class = UserTextForm
    success_url = reverse_lazy("line_qa_with_gpt:home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        login_user = User.objects.get(pk=1)  # TODO: request.user.id
        context["chat_logs"] = ChatLogsWithLine.objects.filter(
            user=login_user
        ).order_by("created_at")

        return context

    def form_valid(self, form):
        form_data = form.cleaned_data
        login_user = User.objects.get(pk=1)  # TODO: request.user.id

        use_case_type = "OpenAISpeechToText"  # TODO: ドロップダウンでモードを決める？
        use_case: UseCase | None = None
        content: str | None = form_data["question"]
        if use_case_type == "Gemini":
            use_case = GeminiUseCase()
            content = form_data["question"]
        elif use_case_type == "OpenAIGpt":
            use_case = OpenAIGptUseCase()
            content = form_data["question"]
        elif use_case_type == "OpenAIDalle":
            use_case = OpenAIDalleUseCase()
            content = form_data["question"]
        elif use_case_type == "OpenAITextToSpeech":
            use_case = OpenAITextToSpeechUseCase()
            content = form_data["question"]
        elif use_case_type == "OpenAISpeechToText":
            use_case = OpenAISpeechToTextUseCase()
            content = None

        use_case.execute(user=login_user, content=content)

        return super().form_valid(form)


@csrf_exempt
class LineWebHookView(View):
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

        return HttpResponse(status=200)
