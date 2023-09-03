import sys
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse, Response
from pydantic import BaseModel
from typing import List
from enum import Enum

app = FastAPI()


class SortField(str, Enum):
    name = "name",
    author = "author",
    genre = "genre",
    year = "year",
    pages = "pages"


class BookRequest(BaseModel):
    name: str
    author: str
    genre: str
    year: int
    pages: int


class Book(BookRequest):
    id: int


class Stat(BaseModel):
    min: int
    max: int
    avg: int


class BooksStat(BaseModel):
    year: Stat
    pages: Stat


books = [
    Book(id=1, name='War and Peace', author='Tolstoy Lev Nikolaevich', genre='novel', year=1873, pages=500),
    Book(id=2, name='Entertaining arithmetic and mathematics', author='Perelman Yakov Isidorovich', genre='education', year=1926, pages=320),
    Book(id=3, name='Hotel', author='Hailey Arthur', genre='novel', year=1965, pages=200)
]


@app.get("/", response_class=RedirectResponse, include_in_schema=False)
def main():
    return "/docs"


@app.get("/books/", response_model=List[Book])
def get_books(sort_by: SortField = None):
    if sort_by == SortField.name:
        return sorted(books, key=lambda x: x.name)
    elif sort_by == SortField.author:
        return sorted(books, key=lambda x: x.author)
    elif sort_by == SortField.genre:
        return sorted(books, key=lambda x: x.genre)
    elif sort_by == SortField.year:
        return sorted(books, key=lambda x: x.year)
    elif sort_by == SortField.pages:
        return sorted(books, key=lambda x: x.pages)
    else:
        return books


@app.post("/books/", response_model=None)
def create_book(book: BookRequest):
    id = books[-1].id + 1
    books.append(Book(id=id, **book.model_dump()))

    return Response(status_code=status.HTTP_200_OK)


@app.get("/books/{id}", response_model=Book)
def get_book(id: int):
    for index, value in enumerate(books):
        if value.id == id:
            return value

    raise HTTPException(404, detail="Book doesn't exist")


@app.put("/books/{id}", response_model=None)
def update_book(id: int, book: BookRequest):
    for index, value in enumerate(books):
        if value.id == id:
            books[index] = Book(id=id, **book.model_dump())
            return Response(status_code=status.HTTP_200_OK)

    raise HTTPException(404, detail="Book doesn't exist")


@app.delete("/books/{id}", response_model=None)
def delete_book(id: int):
    for index, value in enumerate(books):
        if value.id == id:
            books.pop(index)
            return Response(status_code=status.HTTP_200_OK)

    raise HTTPException(404, detail="Book doesn't exist")


@app.get("/books-stat", response_model=BooksStat)
def books_stat():
    year_stat = Stat(min=sys.maxsize, max=0, avg=0)
    pages_stat = Stat(min=sys.maxsize, max=0, avg=0)

    books_count = len(books)

    for index, value in enumerate(books):
        year_stat.avg += value.year / books_count
        pages_stat.avg += value.pages / books_count

        if value.year < year_stat.min:
            year_stat.min = value.year
        if value.year > year_stat.max:
            year_stat.max = value.year
        if value.pages < pages_stat.min:
            pages_stat.min = value.pages
        if value.pages > pages_stat.max:
            pages_stat.max = value.pages

    return BooksStat(year=year_stat, pages=pages_stat)
