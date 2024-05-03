from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import FormView

from retrieval_qa_with_source.forms import UserTextForm
from retrieval_qa_with_source.models import ChatLogsWithLine


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
