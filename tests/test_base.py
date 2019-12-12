import pytest

from html2ans.base import AbstractHtmlAnsParser, BaseHtmlAnsParser
from html2ans.parsers.base import BaseElementParser, ParseResult
from html2ans.parsers.text import ParagraphParser


def test_interface():
    with pytest.raises(NotImplementedError):
        AbstractHtmlAnsParser().generate_ans('<p></p>')


def test_suppress_exceptions():
    default_parser = BaseHtmlAnsParser(suppress_exceptions=True)
    default_parser.add_parser(DummyParserException())
    assert default_parser.generate_ans('\n<body><foo>dummy words</foo></body>\n') == []


def test_dont_suppress_exceptions():
    default_parser = BaseHtmlAnsParser(suppress_exceptions=False)
    default_parser.add_parser(DummyParserException())
    with pytest.raises(Exception):
        default_parser.generate_ans('\n<body><foo>dummy words</foo></body>\n')


def test_add_parser(test_html2ans):
    test_html2ans.add_parser(DummyParser())
    assert test_html2ans.generate_ans('\n<body><foo>dummy words</foo></body>\n') == [
        {'type': 'foo', 'bar': "dummy words"}
    ]


def test_insert_parser(test_html2ans):
    test_html2ans.insert_parser("foo", DummyParser(), 0)
    assert test_html2ans.generate_ans('\n<body><foo>dummy words</foo></body>\n') == [
        {'type': 'foo', 'bar': "dummy words"}
    ]


def test_parse(test_html2ans):
    test_html2ans.insert_parser("foo", DummyParserList(), 0)
    assert test_html2ans.generate_ans('\n<body><foo>dummy words</foo></body>\n') == [
        {'type': 'foo', 'bar': "dummy words"},
        {'type': 'foo', 'bar': "others"}
    ]


def test_add_parser_multiple_applicable(test_html2ans):
    parser = ParagraphParser()
    parser.applicable_elements.append('blockquote')
    test_html2ans.add_parser(parser)
    assert test_html2ans.parsers['blockquote'][len(test_html2ans.parsers['blockquote'])-1] == parser


def test_start_tag(test_html2ans):
    assert test_html2ans.generate_ans('<body><p></p></body>', start_tag='blockquote') == []


"""
    These instances were returning a content element of 
    {
        "type": "quote",
        "content_elements": [None]
    }
    which is not valid ans.  The reason was due to the way these fell back to
    the blockquote parser when the initial parsers failed.
"""
@pytest.mark.parametrize('data', [
    '<blockquote class="twitter-tweet" data-lang="en">\n	&nbsp;</blockquote>',
    '<blockquote class="twitter-tweet" data-partner="tweetdeck">\n	&nbsp;</blockquote>',
    '<blockquote class="imgur-embed-pub" data-id="oSDWFTJ" lang="en">\n	&nbsp;</blockquote>',
    '<blockquote class="twitter-tweet" data-lang="en">&nbsp;</blockquote>',
    '<blockquote class="twitter-video" data-lang="en">\n	&nbsp;</blockquote>',
    '<blockquote class="imgur-embed-pub" data-id="a/bMSXD" lang="en">\n	&nbsp;</blockquote>',
])
def test_ignore_empty_blocks(data, test_html2ans):
    assert test_html2ans.generate_ans(data) == []


class DummyParser(BaseElementParser):
    applicable_elements = ['foo']

    def parse(self, tag):
        return ParseResult({
            "type": "foo",
            "bar": tag.text
        }, True)


class DummyParserException(BaseElementParser):
    applicable_elements = ['foo']

    def parse(self, tag):
        raise Exception()


class DummyParserList(BaseElementParser):
    applicable_elements = ['foo']

    def parse(self, tag):
        return ParseResult([
            {'type': 'foo', 'bar': "dummy words"},
            {'type': 'foo', 'bar': "others"}
        ], True)

