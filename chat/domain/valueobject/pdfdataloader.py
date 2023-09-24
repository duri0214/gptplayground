from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PDFMinerLoader

from chat.domain.valueobject.dataloader import Dataloader


class PdfDataloader(Dataloader):
    @property
    def data(self):
        return self._data_by_page

    def __init__(self, file_path: str, separators: list, chunk_size: int = 600, chunk_overlap: int = 100):
        self._file_path = file_path
        self._separators = separators
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._load()
        self._split(self._separators)

    def _load(self):
        self.data_raw = PDFMinerLoader(self._file_path).load()

    def _split(self, separators: list):
        """
        PDFをページ単位に切り刻み、出典（ページ数）をつけます
        :param separators: ページを識別する正規表現 e.g. ['\n\n \n']
        """
        self._text_splitter = RecursiveCharacterTextSplitter(
                separators=self._separators,
                chunk_size=self._chunk_size,
                chunk_overlap=self._chunk_overlap
        )
        self._data_by_page = self._text_splitter.split_documents(self.data_raw)
        for i, a_page in enumerate(self._data_by_page):
            a_page.metadata['type'] = 'pdf'
            a_page.metadata['page'] = i + 1
