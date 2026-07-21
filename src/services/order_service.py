class BookService:

    def __init__(self, repository: BookRepository):
        self.repository = repository

    async def create_book(self, data: BookCreate):

        # проверка бизнес-логики
        if await self.repository.exists(data.title):
            raise BookAlreadyExists()

        return await self.repository.create(data)