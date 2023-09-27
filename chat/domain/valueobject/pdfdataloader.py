import os
from typing import List

from langchain.document_loaders import PyPDFLoader
from langchain.schema import Document

from chat.domain.valueobject.dataloader import Dataloader


class PdfDataloader(Dataloader):
    @property
    def data(self) -> List[Document]:
        return self._docs

    def __init__(self, file_path: str):
        super().__init__()
        self._file_path = file_path
        self._load()
        self._split()

    def _load(self):
        self.data_raw = PyPDFLoader(self._file_path).load()

    def _split(self):
        """
        PDFを切り刻み、出典（ページ数）をつけます
        """
        self._docs = self.text_splitter.split_documents(self.data_raw)
        filename = os.path.basename(self._file_path)
        for i, doc in enumerate(self._docs):
            doc.page_content = doc.page_content.replace("\n", " ")
            doc.metadata = {"source": f'{filename} {i + 1}ページ'}
