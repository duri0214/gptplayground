import json
from pathlib import Path

import environ
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView
from openai import OpenAI

from config.settings import BASE_DIR
from line_qa_with_gpt_and_dalle.domain.service.openai import (
    MyChatCompletionMessage,
    ModelSpeechToTextService,
)
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
        ).order_by("created_at")

        return context

    def form_valid(self, form):
        form_data = form.cleaned_data
        login_user = User.objects.get(pk=1)  # TODO: request.user.id

        env = environ.Env()
        environ.Env.read_env(Path(BASE_DIR, ".env"))
        client = OpenAI(api_key=env("OPENAI_API_KEY"))

        # TODO: gpt用なのでfile_pathはありません
        # gpt_service = ModelGptService(client)
        # my_chat_completion_message = MyChatCompletionMessage(
        #     user_id=login_user.pk,
        #     role="user",
        #     content=form_data["question"],
        #     invisible=False,
        # )
        # gpt_service.generate(my_chat_completion_message, gender="man")

        # TODO: 絵にするのはassistantが回答する前の「role: userのセリフ」です
        #  ただし、gpt_serviceの中で呼べば難しくはなさそう
        # dalle_service = ModelDalleService(client)
        # my_chat_completion_message = MyChatCompletionMessage(
        #     user_id=login_user,
        #     role="user",
        #     content=form_data["question"],
        #     invisible=False,
        # )
        # dalle_service.generate(my_chat_completion_message)

        # TODO: tts用なのでfile_pathはありません
        # tts_service = ModelTextToSpeechService(client)
        # my_chat_completion_message = MyChatCompletionMessage(
        #     user_id=login_user.pk,
        #     role="user",
        #     content=form_data["question"],
        #     invisible=False,
        # )
        # tts_service.generate(my_chat_completion_message)

        # TODO: stt用なのでcontentはありません
        stt_service = ModelSpeechToTextService(client)
        my_chat_completion_message = MyChatCompletionMessage(
            user_id=login_user,
            role="user",
            file_path="audios/53f86c30db.mp3",
            invisible=False,
        )
        stt_service.generate(my_chat_completion_message)

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
