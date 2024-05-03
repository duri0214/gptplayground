from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import FormView

from config.settings import BASE_DIR
from retrieval_qa_with_source.domain.service.gptpdfservice import GptPdfService
from retrieval_qa_with_source.domain.valueobject.pdfdataloader import PdfDataloader
from retrieval_qa_with_source.forms import UserTextForm
from retrieval_qa_with_source.models import ChatLogs


class HomeView(FormView):
    template_name = "retrieval_qa_with_source/home.html"
    form_class = UserTextForm
    success_url = reverse_lazy("qa_with_src:home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        login_user = User.objects.get(pk=1)  # TODO: request.user.id
        context["chat_logs"] = ChatLogs.objects.filter(user=login_user).order_by(
            "thread", "created_at"
        )

        return context

    def form_valid(self, form):
        form_data = form.cleaned_data
        login_user = User.objects.get(pk=1)  # TODO: request.user.id

        file_path = str(
            BASE_DIR
            / r"retrieval_qa_with_source\tests\domain\valueobject\令和4年版少子化社会対策白書全体版（PDF版）.pdf"
        )
        chat_history = []  # TODO: 過去ログを含めるかどうかは要判断
        gpt_pdf_service = GptPdfService(PdfDataloader(file_path))
        result = gpt_pdf_service.gpt_answer(form_data["question"], chat_history)
        # TODO: うまく改行できてねーなー（一番下にスクロールするのもつけたほうがいいかも...っていうかAjaxだよ）
        source_documents = "<br>".join(
            [doc.metadata["source"] for doc in result["source_documents"]]
        )
        formatted_answer = f'{result["answer"]}<br><br>{source_documents}'
        ChatLogs.objects.create(
            user=login_user, thread="XXX", role="user", message=form_data["question"]
        )
        ChatLogs.objects.create(
            user=login_user, thread="XXX", role="assistant", message=formatted_answer
        )

        return super().form_valid(form)
