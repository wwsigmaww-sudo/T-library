import json
import os
from dataclasses import dataclass, asdict
from typing import List, Optional

DATA_FILE = "library.json"

@dataclass
class Book:
    title: str
    author: str
    genre: str
    year: int
    description: str
    read: bool = False
    favorite: bool = False

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return Book(**data)


class Library:
    def __init__(self):
        self.books: List[Book] = []
        self.load()

    def save(self):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump([book.to_dict() for book in self.books], f, ensure_ascii=False, indent=2)

    def load(self):
        if not os.path.exists(DATA_FILE):
            return
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.books = [Book.from_dict(item) for item in data]

    def add_book(self, title: str, author: str, genre: str, year: int, description: str):
        book = Book(title, author, genre, year, description)
        self.books.append(book)
        self.save()
        return book

    def remove_book(self, index: int):
        if 0 <= index < len(self.books):
            removed = self.books.pop(index)
            self.save()
            return removed
        return None

    def get_books(self, sort_by: Optional[str] = None, genre: Optional[str] = None, read_status: Optional[bool] = None):
        books = self.books[:]
        if genre:
            books = [b for b in books if b.genre.lower() == genre.lower()]
        if read_status is not None:
            books = [b for b in books if b.read == read_status]
        if sort_by == 'title':
            books.sort(key=lambda b: b.title.lower())
        elif sort_by == 'author':
            books.sort(key=lambda b: b.author.lower())
        elif sort_by == 'year':
            books.sort(key=lambda b: b.year)
        return books

    def add_to_favorites(self, index: int):
        if 0 <= index < len(self.books):
            self.books[index].favorite = True
            self.save()
            return True
        return False

    def remove_from_favorites(self, index: int):
        if 0 <= index < len(self.books):
            self.books[index].favorite = False
            self.save()
            return True
        return False

    def toggle_read_status(self, index: int):
        if 0 <= index < len(self.books):
            self.books[index].read = not self.books[index].read
            self.save()
            return self.books[index].read
        return None

    def get_favorites(self):
        return [b for b in self.books if b.favorite]

    def search(self, keyword: str):
        keyword = keyword.lower()
        results = []
        for book in self.books:
            if (keyword in book.title.lower() or
                keyword in book.author.lower() or
                keyword in book.description.lower()):
                results.append(book)
        return results


def display_books(books, title="Список книг"):
    if not books:
        print("Нет книг для отображения.")
        return
    print(f"\n{title}:")
    for i, book in enumerate(books):
        status_read = "✔" if book.read else "✘"
        status_fav = "★" if book.favorite else " "
        print(f"{i+1}. [{status_read}] [{status_fav}] {book.title} - {book.author} ({book.year})")
        print(f"   Жанр: {book.genre}")
        print(f"   Описание: {book.description[:100]}{'...' if len(book.description) > 100 else ''}")
        print()


def main():
    lib = Library()
    while True:
        print("\n=== T-Библиотека ===")
        print("1. Добавить книгу")
        print("2. Просмотреть все книги")
        print("3. Добавить в избранное")
        print("4. Удалить из избранного")
        print("5. Изменить статус прочтения")
        print("6. Показать избранные книги")
        print("7. Удалить книгу")
        print("8. Найти книгу")
        print("9. Выход")
        choice = input("Выберите действие: ").strip()

        if choice == '1':
            title = input("Название: ").strip()
            author = input("Автор: ").strip()
            genre = input("Жанр: ").strip()
            year = input("Год издания: ").strip()
            while not year.isdigit():
                year = input("Введите корректный год: ").strip()
            year = int(year)
            description = input("Описание: ").strip()
            lib.add_book(title, author, genre, year, description)
            print("Книга добавлена!")

        elif choice == '2':
            sort_by = input("Сортировать по (title/author/year, или Enter для без сортировки): ").strip().lower()
            if sort_by not in ('title', 'author', 'year'):
                sort_by = None
            genre = input("Фильтр по жанру (Enter - без фильтра): ").strip()
            if not genre:
                genre = None
            read_filter = input("Фильтр по статусу (read/unread, Enter - все): ").strip().lower()
            read_status = None
            if read_filter == 'read':
                read_status = True
            elif read_filter == 'unread':
                read_status = False
            books = lib.get_books(sort_by=sort_by, genre=genre, read_status=read_status)
            display_books(books)

        elif choice == '3':
            books = lib.get_books()
            if not books:
                print("Нет книг для добавления в избранное.")
                continue
            display_books(books, "Выберите книгу для добавления в избранное:")
            try:
                idx = int(input("Номер книги: ")) - 1
                if lib.add_to_favorites(idx):
                    print("Книга добавлена в избранное!")
                else:
                    print("Неверный номер.")
            except ValueError:
                print("Введите число.")

        elif choice == '4':
            favs = lib.get_favorites()
            if not favs:
                print("Нет избранных книг.")
                continue
            display_books(favs, "Избранные книги для удаления:")
            try:
                # Нужно найти индекс в общем списке, а не в favs
                idx = int(input("Номер книги в избранном (для удаления): ")) - 1
                if 0 <= idx < len(favs):
                    book = favs[idx]
                    # Найдём индекс в основном списке
                    for i, b in enumerate(lib.books):
                        if b is book:
                            if lib.remove_from_favorites(i):
                                print("Книга удалена из избранного!")
                            break
                else:
                    print("Неверный номер.")
            except ValueError:
                print("Введите число.")

        elif choice == '5':
            books = lib.get_books()
            if not books:
                print("Нет книг для изменения статуса.")
                continue
            display_books(books, "Выберите книгу для изменения статуса прочтения:")
            try:
                idx = int(input("Номер книги: ")) - 1
                new_status = lib.toggle_read_status(idx)
                if new_status is not None:
                    print(f"Статус изменён на {'прочитана' if new_status else 'не прочитана'}.")
                else:
                    print("Неверный номер.")
            except ValueError:
                print("Введите число.")

        elif choice == '6':
            favs = lib.get_favorites()
            display_books(favs, "Избранные книги")

        elif choice == '7':
            books = lib.get_books()
            if not books:
                print("Нет книг для удаления.")
                continue
            display_books(books, "Выберите книгу для удаления:")
            try:
                idx = int(input("Номер книги: ")) - 1
                removed = lib.remove_book(idx)
                if removed:
                    print(f"Книга '{removed.title}' удалена.")
                else:
                    print("Неверный номер.")
            except ValueError:
                print("Введите число.")

        elif choice == '8':
            keyword = input("Введите ключевое слово для поиска: ").strip()
            if not keyword:
                print("Ключевое слово не может быть пустым.")
                continue
            results = lib.search(keyword)
            display_books(results, f"Результаты поиска по '{keyword}'")

        elif choice == '9':
            print("До свидания!")
            break

        else:
            print("Неверный выбор, попробуйте снова.")


if __name__ == "__main__":
    main()