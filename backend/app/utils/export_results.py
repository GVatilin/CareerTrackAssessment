from subprocess import CalledProcessError
from typing import Generator
from uuid import uuid4
from pylatex import (
    Document,
    Section,
    Command,
    Package,
    Tabularx,
    Subsection,
    TikZ
)
from pylatex.utils import NoEscape, bold
import pypandoc

from contextlib import contextmanager, suppress

from app.schemas.question import QuizResult

COLOR = "6eb8e0"


def apply_color(text: str) -> NoEscape:
    return NoEscape(r"\textcolor[HTML]{" + COLOR + r"}{" + text + r"}")


def get_tasks_results_pdf(results: QuizResult) -> str:
    filename = str(uuid4())
    with pdf_document(filename) as doc:
        with (
            doc.create(Section(apply_color("Общие результаты"), numbering=False)),
            doc.create(Tabularx("lX")) as table
        ):
            table.add_hline()
            table.add_row((
                bold("Параметр"),
                bold("Значение")
            ))
            table.add_hline()
            table.add_row("Количество вопросов", results.total_questions)
            table.add_row("Правильные ответы", results.total_correct_answers)
            table.add_row("Процент успешности", f"{results.score_percent}%")
            table.add_hline()

        with doc.create(Section(apply_color("Детализация по вопросам"), numbering=False)):
            for question in results.answers:
                with doc.create(Subsection(f"{question.description}", numbering=False)):
                    text = pypandoc.convert_text(
                        question.explanation,
                        to="latex",
                        format="html"
                    )
                    doc.append(NoEscape(text))

        with doc.create(Section(apply_color("Рекомендации"), numbering=False)):
            text = pypandoc.convert_text(
                results.ai_recommendations,
                to="latex",
                format="html"
            )
            doc.append(NoEscape(text))
    
    return filename


@contextmanager
def pdf_document(filename: str) -> Generator[Document, None, None]:
    doc = Document(
        default_filepath="russian_doc",
        documentclass="article",
        document_options=["12pt", "a4paper"],
        geometry_options={
            "top": "10mm",
            "headheight": "0mm",
            "includehead": False
        }
    )
    
    doc.packages.append(Package("polyglossia"))
    doc.packages.append(Package("tikz"))
    doc.packages.append(Package("booktabs"))
    doc.packages.append(Package("array"))
    doc.packages.append(Package("xcolor"))
    doc.packages.append(Package("hyperref"))
    doc.packages.append(Package("enumitem"))
    doc.packages.append(Package("microtype"))

    doc.preamble.append(Command("setmainlanguage", "russian"))
    doc.preamble.append(Command("setotherlanguage", "english"))
    doc.preamble.append(Command("setmainfont", "Liberation Serif"))
    doc.preamble.append(NoEscape(r"\newfontfamily\cyrillicfont{Liberation Serif}"))
    doc.preamble.append(NoEscape(r"\newfontfamily\cyrillicfonttt{Liberation Mono}"))

    doc.preamble.append(Command("usetikzlibrary", "positioning"))

    doc.preamble.append(NoEscape(r"""
        \providecommand{\tightlist}{%
            \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
    """))

    doc.preamble.append(NoEscape(r"""
        \hypersetup{
            colorlinks=true,
            linkcolor=blue,
            filecolor=magenta,      
            urlcolor=cyan,
            pdftitle={Ваш заголовок},
            bookmarks=true,
        }
    """))

    doc.preamble.append(Command("title", apply_color("Результат тестирования")))
    doc.preamble.append(Command("author", "Итоговый результат с рекомендациями"))
    doc.preamble.append(Command("date", NoEscape(r"\today")))
    doc.append(NoEscape(r"\maketitle"))
        
    with doc.create(TikZ(options=["remember picture", "overlay"])) as tikz:
        tikz.append(NoEscape(r"""
            \node[anchor=north east, xshift=-10mm, yshift=-10mm] at (current page.north east) {
                \includegraphics[width=30mm]{stamp.png}
            };
        """))
    
    yield doc
    with suppress(CalledProcessError):
        output_path = f"documents/{filename}"
        doc.generate_pdf(
            filepath=output_path,
            compiler="xelatex",
            clean=False,
            clean_tex=False,
            silent=False
        )
    with suppress(CalledProcessError):
        doc.generate_pdf(
            filepath=output_path,
            compiler="xelatex"
        )
        
