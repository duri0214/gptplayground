from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView

from d_id.domain.service.did_service import DidService
from line_qa_with_gpt_and_dalle.forms import UserTextForm


class HomeView(FormView):
    template_name = "d_id/home.html"
    form_class = UserTextForm
    success_url = reverse_lazy("d_id:home")

    def form_valid(self, form):
        form_data = form.cleaned_data
        print(f"question: {form_data['question']}")

        source_url = (
            "https://www.henojiya.net/static/vietnam_research/chart/nobunaga.png"
        )
        did_service = DidService(source_url)

        # to d-id payload
        payload = {
            "script": {"type": "text", "input": form_data["question"]},
            "source_url": "https://create=images-results.d-id.com/DefaultPresenters/Noelle_f/image.jpeg",
            # "webhook":
        }

        # env = environ.Env()
        # environ.Env.read_env(Path(BASE_DIR, ".env"))
        # client = OpenAI(api_key=env("OPENAI_API_KEY"))

        # gpt_service = ModelGptService(client)
        # my_chat_completion_message = MyChatCompletionMessage(
        #     user_id=login_user.pk,
        #     role="user",
        #     content=form_data["question"],
        #     invisible=False,
        # )
        # gpt_service.generate(my_chat_completion_message, gender="man")

        return render(
            self.request,
            self.template_name,
            {"question": form_data["question"], "form": UserTextForm()},
        )
