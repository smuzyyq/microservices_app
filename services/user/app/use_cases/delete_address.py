from domain.exceptions import AddressNotFoundError, UnauthorizedError
from interfaces.repositories.user_repository import IUserRepository


class DeleteAddressUseCase:
    def __init__(self, user_repo: IUserRepository) -> None:
        self.user_repo = user_repo

    def execute(self, address_id, user_id) -> bool:
        address = self.user_repo.get_address_by_id(address_id)
        if address is None:
            raise AddressNotFoundError("Address not found.")
        if address.user_id != user_id:
            raise UnauthorizedError("You do not own this address.")
        return self.user_repo.delete_address(address_id)
