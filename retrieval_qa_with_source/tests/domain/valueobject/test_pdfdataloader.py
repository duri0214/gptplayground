from unittest import TestCase

from retrieval_qa_with_source.domain.valueobject.pdfdataloader import PdfDataloader


class TestPdfDataloader(TestCase):
    def test_this_pdf_has_pages_en(self):
        dataloader = PdfDataloader('./doj_cloud_act_white_paper_2019_04_10.pdf')
        self.assertEqual(18, len(dataloader.pages))
        print(dataloader.data)

    def test_this_pdf_has_pages_jp(self):
        dataloader = PdfDataloader('./令和4年版少子化社会対策白書全体版（PDF版）.pdf')
        self.assertEqual(6, len(dataloader.pages))
        print(dataloader.data)
