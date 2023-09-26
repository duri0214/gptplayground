from django.contrib.auth.models import User
from django.views.generic import TemplateView

from chat.domain.service.gptpdfservice import GptPdfService
from chat.domain.valueobject.pdfdataloader import PdfDataloader
from chat.models import ChatGpt
from config.settings import BASE_DIR


class HomeView(TemplateView):
    template_name = 'chat/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        login_user = User.objects.get(pk=1)  # TODO: request.user.id
        context["chatlogs"] = ChatGpt.objects.filter(user=login_user).order_by('thread', 'created_at')

        file_path = str(BASE_DIR / r'chat\tests\domain\valueobject\令和4年版少子化社会対策白書全体版（PDF版）.pdf')
        dataloader = PdfDataloader(file_path)
        chat_history = []
        gpt_pdf_service = GptPdfService(dataloader)
        result = gpt_pdf_service.gpt_answer('晩婚化について教えて', chat_history)
        context["answer"] = result["answer"]
        context["sources"] = result["sources"]

        return context
