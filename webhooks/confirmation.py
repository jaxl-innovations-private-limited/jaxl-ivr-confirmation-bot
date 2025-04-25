"""
Copyright (c) 2010-present by Jaxl Innovations Private Limited.

All rights reserved.

Redistribution and use in source and binary forms,
with or without modification, is strictly prohibited.
"""

from pathlib import Path
from typing import Any, List, Optional, Tuple, TypedDict

from jaxl.ivr.frontend.base import (
    BaseJaxlIVRWebhook,
    ConfigPathOrDict,
    JaxlIVRRequest,
    JaxlIVRResponse,
    JaxlIVRState,
)


class CustomerOrder(TypedDict):
    """Customer order metadata"""

    id: str
    name: str


class CustomerContext(TypedDict):
    """Customer context composed of customer name and last order details."""

    name: str
    last_order: CustomerOrder


# pylint: disable=unused-argument
def _get_customer_context(customer_number: str) -> CustomerContext:
    """Returns customer context by their phone number.

    TODO: Integrate this with your backend database, CSV etc to return details dynamically.
    """
    return CustomerContext(
        name="Abhinav",
        last_order=CustomerOrder(
            id="1234",
            name="Jaxl Business Phone",
        ),
    )


def _get_greeting(
    brand_name: str,
    ctx: CustomerContext,
) -> List[str]:
    return [
        f"Hello {ctx['name']}, this is a confirmation call from {brand_name}, ",
        f"for your order of {ctx['last_order']['name']}, order number {ctx['last_order']['id']}.",
        "Press 1 to repeat this message.",
        "Press 9 to confirm the order.",
        "Press any other key or hangup the call if you did not place an order.",
    ]


class JaxlIVRConfirmationWebhook(BaseJaxlIVRWebhook):
    """confirmation.json webhook implementation."""

    def __init__(self):
        super().__init__()

        # NOTE: These variables are only accessible within sync methods i.e.
        # config, setup, teardown, handle_option, stream
        #
        # NOTE: These variables are NOT accessible within async methods like
        # handle_raw_audio, on_transcription.
        #
        # NOTE: For async equivalent of __init__, implement on_init callback.
        #
        # NOTE: You can re-use these variables across your sync and async callbacks
        # but they are only available in the context they were set in.
        self._confirmed = False
        self._state: Optional[JaxlIVRState] = None
        self._ctx: Optional[CustomerContext] = None

    @staticmethod
    def config() -> ConfigPathOrDict:
        return Path(__file__).parent.parent / "schemas" / "confirmation.json"

    def setup(self, request: JaxlIVRRequest) -> JaxlIVRResponse:
        # Store state which contains call_id, from_number, to_number
        self._state = request["state"]
        assert self._state

        # NOTE: Use "to_number" for outgoing calls, use "from_number" for incoming calls
        self._ctx = _get_customer_context(self._state["to_number"])

        return JaxlIVRResponse(
            prompt=_get_greeting(brand_name="My Company", ctx=self._ctx),
            num_characters=1,
            stream=None,
        )

    def teardown(self, request: JaxlIVRRequest) -> None:
        print("State", self._state, "Confirmed?", self._confirmed)

    def handle_option(self, request: JaxlIVRRequest) -> JaxlIVRResponse:
        assert self._ctx
        # Option 1 == Repeat the menu
        if request["option"] == "1":
            return JaxlIVRResponse(
                prompt=_get_greeting(brand_name="My Company", ctx=self._ctx),
                num_characters=1,
                stream=None,
            )

        # Option 9 == Customer confirmed the order
        if request["option"] == "9":
            # NOTE: Sync confirmation state in db before replying
            self._confirmed = True
            return JaxlIVRResponse(
                prompt=["Thank you for your confirmation.", "Bye."],
                num_characters=0,
                stream=None,
            )

        return JaxlIVRResponse(
            prompt=[
                "Sorry for the trouble.",
                "Our team will audit this order placed from your account.",
                "Thank you.",
                "Bye.",
            ],
            num_characters=0,
            stream=None,
        )

    def stream(
        self,
        request: JaxlIVRRequest,
        chunk_id: int,
        sstate: Any,
    ) -> Optional[Tuple[Any, JaxlIVRResponse]]:
        raise NotImplementedError()

    # Uncomment async methods below and start your IVR using
    # "--stream" flag.
    #
    # async def on_init(self, state: JaxlIVRState) -> None:
    #     self._state = state
    #
    # async def handle_raw_audio(
    #     self,
    #     call_id: int,
    #     ivr_id: int,
    #     chunk_id: int,
    #     audio: bytes,
    # ) -> None:
    #     print(
    #         f"Received {len(audio)} bytes for call#{call_id} on ivr#{ivr_id} "
    #         + f"with state#{self._state}"
    #     )

    # Uncomment async methods below and start your IVR using
    # "--transcribe" flag.
    #
    # NOTE: To turn this IVR app into a conversational bot, also use the
    # "--conversational" flag.
    #
    # async def on_transcription(
    #     self,
    #     call_id: int,
    #     ivr_id: int,
    #     chunk_id: int,
    #     duration: float,
    #     transcription: str,
    # ) -> Optional[JaxlIVRResponse]:
    #     print(transcription)
    #     # # If you are running in --conversational mode, its mandatory to return a response
    #     # # If you are NOT using --conversational flag, then you must return None to avoid
    #     # # overlapping system speech with IVR flow.
    #     # #
    #     # # Echo back the transcription back to the user
    #     # return JaxlIVRResponse(
    #     #     prompt=[transcription],
    #     #     # num_characters=1 ensures call is not dropped, passing 0 will drop the call.
    #     #     num_characters=1,
    #     #     stream=None,
    #     # )
    #     # # Uncomment below line if NOT using --conversational
    #     return None
