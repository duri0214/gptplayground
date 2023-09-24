from typing import List

from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain

from chat.domain.valueobject.dataloader import Dataloader


class GptPdfService:
    def __init__(self, dataloader: Dataloader):
        self.dataloader = dataloader

        # TODO: systemmessageを使いたいがいまは使われていない
        # self.n_results = n_results
        # self.system_template = """
        #     以下の資料の注意点を念頭に置いて回答してください
        #     ・ユーザの質問に対して、できる限り根拠を示してください
        #     ・箇条書きで簡潔に回答してください。
        #     ・どの情報を参照したのかのメタデータも「（出典：xx）」のようにかっこ書きで示してください
        #     ・メタデータには ページid が入っているので `http://localhost:3000/pages/ページid` のようにくっつけて出してください
        #     ---下記は資料の内容です---
        #     {summaries}
        #
        #     Answer in Japanese:
        # """
        # messages = [
        #     SystemMessagePromptTemplate.from_template(self.system_template),
        #     HumanMessagePromptTemplate.from_template("{question}")
        # ]
        # self.prompt_template = ChatPromptTemplate.from_messages(messages)

    @staticmethod
    def _create_vectorstore(dataloader: Dataloader) -> Chroma:
        """
        Note: OpenAIEmbeddings runs on "text-embedding-ada-002"
        """
        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma.from_documents(
            dataloader.data,
            embedding=embeddings,
            persist_directory='.'
        )
        vectorstore.persist()

        return vectorstore

    def get_answer(self, user_text: str, chat_history: List[str]) -> dict:
        """
        Note: ChatOpenAI runs on 'gpt-3.5-turbo'
        """
        llm = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo')
        vectorstore = self._create_vectorstore(self.dataloader)
        pdf_qa = ConversationalRetrievalChain.from_llm(llm, vectorstore.as_retriever(), return_source_documents=True)

        return pdf_qa({"question": user_text, "chat_history": chat_history})
