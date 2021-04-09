import hashlib
import json
from typing import Union

from pc4store import config

from pc4store.data import (
    CreateOrderInput, CreateOrderSuccess, CreateOrderError
)
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


class BaseClient:
    CREATE_ORDER = f'{config.HOST}/create'
    GET_ORDER = f'{config.HOST}/order'

    def __init__(self, store_id: str, store_key: str):
        self.store_id = store_id
        self.store_key = store_key
        self.public_key: Ed25519PublicKey = Ed25519PublicKey.from_public_bytes(
            bytes(bytearray.fromhex(config.PUBLIC_KEY)))

    @classmethod
    def _get_validated_create_input(cls, params: Union[CreateOrderInput, dict]
                                    ) -> CreateOrderInput:
        assert isinstance(params, (CreateOrderInput, dict))
        if isinstance(params, dict):
            return CreateOrderInput.from_dict(params)

    @classmethod
    def _get_formatted_create_res(
            cls, data: dict
    ) -> Union[CreateOrderSuccess, CreateOrderError]:
        if data['status'] == 'OK':
            return CreateOrderSuccess.from_dict(**data)
        else:
            return CreateOrderError(error=data.get('error'))

    def is_signature_correct(self, json_body: dict, headers: dict) -> bool:
        signature = headers.get('SIGNATURE')
        assert signature is not None
        str_body = json.dumps(json_body, separators=(',', ':'))
        hashlib.sha256(str_body.encode()).hexdigest()
        try:
            self.public_key.verify(bytes(bytearray.fromhex(signature)),
                                   bytes(bytearray(str_body)))
        except Exception:
            return False
        return True
