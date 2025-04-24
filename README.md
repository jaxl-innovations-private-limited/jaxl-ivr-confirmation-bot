# Jaxl IVR: Confirmation Bot

Automate post-order confirmation calls with dynamic, programmable IVRs.

This is a reference implementation demonstrating how to build a custom outgoing IVR flow using [jaxl-ivr-simulator](https://github.com/jaxl-innovations-private-limited/jaxl-ivr-simulator). It simulates automated calls made to customers right after they place an order — either via your website or mobile app — allowing them to confirm or cancel with a single key press.

## 📚 Table of Contents

- [📦 Use Case](#-use-case)
- [🧠 How It Works](#-how-it-works)
- [🛠️ Features](#️-features)
- [🚀 Getting Started](#-getting-started)
  - [Pre-requisites](#pre-requisites)
  - [Configure `confirmation.json`](#configure-confirmationjson)
  - [Authenticate your IVR application](#authenticate-your-ivr-application)
  - [Run the IVR locally](#run-the-ivr-locally)
- [📞 Making Test Calls](#-making-test-calls)
- [✏️ Customization](#️-customization)
  - [Fetch Customer Data Dynamically](#fetch-customer-data-dynamically)
  - [Customize Prompts](#customize-prompts)
- [🧠 Integrate with AI/LLMs](#-integrate-with-aillms)
  - [⛴️ Requirement](#️-requirement)
  - [🎧 Access Raw Audio](#-access-raw-audio)
  - [🧠 Enable LLM-Driven Conversations](#-enable-llm-driven-conversations)
  - [📝 Get Real-Time Transcriptions](#-get-real-time-transcriptions)
- [💬 Need Help?](#-need-help)

## 📦 Use Case

- 🔁 **Automated**: Send confirmation calls immediately after checkout.
- 🕐 **Scheduled**: Queue calls for optimal customer reach (e.g., after delivery).
- 🎯 **Personalized**: Dynamically greet users with their name and order info.

## 🧠 How It Works

1. Your system receives a new order.
2. It triggers an outgoing call via Jaxl IVR with the customer’s number.
3. This webhook fetches the customer context.
4. The IVR plays a dynamic message with the order details.
5. The customer presses:
   - `1` → Hear message again
   - `9` → Confirm the order
   - Any other key or hangup → Cancel and trigger an audit trail

## 🛠️ Features

- 🗣️ Text-to-speech based dynamic prompts
- 📲 DTMF input handling
- 🔌 Easy backend integration
- 🧱 Configurable schema using [confirmation.json](schemas/confirmation.json)
- 🧩 Extensible: Bring your own AI, CRM, or data source
- 🧪 Simulate before deploy: Run locally or in staging before going live.

## 🚀 Getting Started

### Pre-requisites

- Docker installed
- An active Indian phone number on your [Jaxl Business Phone](https://business.jaxl.com) account
- Access to `jaxl-api-credentials.json` file. `Jaxl Developer Platform` is current under invite-only mode. Please fill up the [Early Access Form](https://forms.gle/veuBL4Bmz54Vp8xa9) to receive the credentials file over email

### Configure `confirmation.json`

Update `confirmation.json` to add number purchased from [Jaxl Business Phone](https://business.jaxl.com) application.

Example:

```json
{
  "groups": [],
  "devices": [],
  "phones": [],
  "ivrs": [
    {
      "name": "confirmation",
      "webhook": true,
      "phone_number": "+91XXXXXXXXXX"
    }
  ]
}
```

> Providing a `phone_number` key ensures that all incoming calls to your Jaxl Business Phone number are handled by the confirmation bot.

### Authenticate your IVR application

Login with your [Jaxl Business Phone](https://business.jaxl.com) Email ID:

```bash
docker run \
    -it --rm \
    -v ~/.jaxl:/jaxl/.jaxl \
    -v ~/.proxy:/jaxl/.proxy \
    -v ${PWD}:/jaxl/ivr \
    jaxlinnovationsprivatelimited/jaxl-ivr-simulator:v27 login
```

### Run the IVR locally

Start the IVR application.

> You’ll be prompted to log in again — this time using [Grout](https://github.com/abhinavsingh/proxy.py?tab=readme-ov-file#grout-ngrok-alternative), the tunneling library that securely connects Jaxl backend servers to your local simulator.

```bash
docker run \
    -it --rm \
    -v ~/.jaxl:/jaxl/.jaxl \
    -v ~/.proxy:/jaxl/.proxy \
    -v ${PWD}:/jaxl/ivr \
    jaxlinnovationsprivatelimited/jaxl-ivr-simulator:v27 run \
    confirmation

2025-04-23 09:53:10,022 - grout - Logged in as <grout-account-email-id>
2025-04-23 09:53:13,785 - setup - Grouting https://<uuid>.jaxl.io
[🍀] Logged in as <jaxl-business-phone-account-email-id>
[confirmation] [1139] created IVR "https://<uuid>.jaxl.io/webhook/"
[📲] +91XXXXXXXXXX is now using IVR#1139
```

> Above, application instance IVR ID is 1139.

## 📞 Making Test Calls

To trigger an outgoing call run following command:

```bash
docker run \
    -it --rm \
    -v ~/.jaxl:/jaxl/.jaxl \
    -v ~/.proxy:/jaxl/.proxy \
    -v ${PWD}:/jaxl/ivr \
    jaxlinnovationsprivatelimited/jaxl-ivr-simulator:v27 call \
    --from-number <+91XXXXXXXXXX> \
    --to-number <+91YYYYYYYYYY>

Call#76213 placed from +91XXXXXXXXXX to +91YYYYYYYYYY
```

1. `--from-number` is the phone number purchased from [Jaxl Business Phone](https://business.jaxl.com) application
2. `--to-number` is target customer phone number

## ✏️ Customization

### Fetch Customer Data Dynamically

Replace [`def _get_customer_context(customer_number: str) -> CustomerContext:`](webhooks/confirmation.py)
with your real customer data logic:

```python
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
```

### Customize Prompts

Edit `_get_greeting(brand_name: str, ctx: CustomerContext)` to localize messages or add more steps.

```python
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
```

## 🧠 Integrate with AI/LLMs

Want to build a truly conversational IVR that leverages real-time speech, transcription, and AI-generated responses? `jaxl-ivr-simulator` makes it easy with a few opt-in flags and plugin hooks:

### ⛴️ Requirement

You MUST use `realtime` variant of Docker image available. See [Docker Image Tags](https://github.com/jaxl-innovations-private-limited/jaxl-ivr-simulator?tab=readme-ov-file#docker-image-tags) for more information.

TL;DR -- Use `:v27r` instead of `v27` when using the flags below.

### 🎧 Access Raw Audio

1. Run the IVR app with the `--stream` flag
2. Implement the following method in your plugin to handle audio chunks during a live call:

   ```python
   async def handle_raw_audio(
       self,
       call_id: int,
       ivr_id: int,
       chunk_id: int,
       audio: bytes,
   ) -> None:
       """Handle raw incoming audio bytes from the caller."""
       raise NotImplementedError()
   ```

This gives you direct access to the raw 8kHz 16-bit mono PCM audio stream from the caller in near real-time — perfect for AI/ML pipelines, sentiment analysis, or streaming to an STT engine.

### 🧠 Enable LLM-Driven Conversations

To keep the call open while waiting for AI-generated replies (instead of hanging up on silence):

1. Run with the `--conversational` flag
2. This tells the Jaxl server not to hang up if a prompt has `num_characters=0`, allowing conversational flows driven entirely by backend logic or LLMs.

### 📝 Get Real-Time Transcriptions

For speech-to-text (STT) integration:

1. Add the `--transcribe` flag
2. Then implement the transcription hook in your plugin:

   ```python
   async def on_transcription(
       self,
       call_id: int,
       ivr_id: int,
       chunk_id: int,
       duration: float,
       transcription: str,
   ) -> Optional[JaxlIVRResponse]:
       """Invoked when silence is detected."""
       raise NotImplementedError()
   ```

This gives you structured access to transcribed speech segments during the call — ideal for building bots that listen, understand, and respond in real-time.

By combining `--stream`, `--transcribe`, and `--conversational`, you can build end-to-end conversational AI bots using your favorite models, frameworks, or pipelines — all powered by [Jaxl](https://jaxl.com).

## 💬 Need Help?

This project is for client integrations only. For support or enterprise deployment, contact support@jaxl.com or write to us [jaxl.com/contact/](https://jaxl.com/contact/). Found a bug or have a feature request? [Open an issue on GitHub](https://github.com/jaxl-innovations-private-limited/jaxl-ivr-confirmation-bot/issues).
